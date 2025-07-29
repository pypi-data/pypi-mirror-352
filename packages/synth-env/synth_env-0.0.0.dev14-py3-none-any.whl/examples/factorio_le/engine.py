"""FactorioEngine — Stateful, reproducible wrapper around Factorio Learning Environment.

This engine implements the code-execution based Factorio environment where agents
write Python code as actions and receive text output as observations.
"""

from __future__ import annotations

import logging
import asyncio
import subprocess
import socket
import time
import json
import io
import contextlib
import traceback
import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union, TYPE_CHECKING
from pathlib import Path

import numpy as np
from pydantic import BaseModel

from environment.shared_engine import (
    GetObservationCallable,
    InternalObservation,
)
from stateful.engine import StatefulEngine, StatefulEngineSnapshot
from tasks.core import TaskInstance
from reproducibility.core import IReproducibleEngine
from environment.rewards.core import RewardStack, RewardComponent

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Dataclasses for snapshot & state
# -----------------------------------------------------------------------------

@dataclass
class FactorioEngineSnapshot(StatefulEngineSnapshot):
    """Snapshot of Factorio engine state for reproducibility"""
    rcon_config: Dict[str, Any]
    scenario_name: str
    total_reward_snapshot: float
    agent_namespace_snapshot: Dict[str, Any]
    production_metrics: Dict[str, int]
    step_count: int

@dataclass
class FactorioPublicState:
    """Public state visible to observations"""
    scenario_name: str
    step_count: int
    max_steps: int
    last_code_output: str
    last_error_output: str
    production_metrics: Dict[str, int]
    is_server_running: bool
    error_info: Optional[str] = None

    def diff(self, prev_state: "FactorioPublicState") -> Dict[str, Any]:
        changes = {}
        for field in self.__dataclass_fields__:  # type: ignore[attr-defined]
            new_v, old_v = getattr(self, field), getattr(prev_state, field)
            if new_v != old_v:
                changes[field] = (old_v, new_v)
        return changes

@dataclass
class FactorioPrivateState:
    """Private state for internal engine tracking"""
    reward_last_step: float
    total_reward_episode: float
    terminated: bool
    truncated: bool
    rcon_connected: bool

    def diff(self, prev_state: "FactorioPrivateState") -> Dict[str, Any]:
        changes = {}
        for field in self.__dataclass_fields__:  # type: ignore[attr-defined]
            new_v, old_v = getattr(self, field), getattr(prev_state, field)
            if new_v != old_v:
                changes[field] = (old_v, new_v)
        return changes

# -----------------------------------------------------------------------------
# RCON Client
# -----------------------------------------------------------------------------

class FactorioRCON:
    """Simple RCON client for communicating with Factorio server"""
    
    def __init__(self, host: str, port: int, password: str):
        self.host = host
        self.port = port
        self.password = password
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to the Factorio server via RCON"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(10)
            self.socket.connect((self.host, self.port))
            
            # Authenticate
            auth_packet = self._create_packet(3, self.password)
            self.socket.send(auth_packet)
            response = self._read_packet()
            
            if response[0] == -1:  # Authentication failed
                return False
                
            self.connected = True
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Factorio RCON: {e}")
            return False
    
    def send_command(self, command: str) -> str:
        """Send a command to Factorio and return the response"""
        if not self.connected:
            raise RuntimeError("RCON not connected")
        
        try:
            packet = self._create_packet(2, command)
            self.socket.send(packet)
            response = self._read_packet()
            return response[2].decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to send RCON command: {e}")
            return f"RCON Error: {e}"
    
    def close(self):
        """Close the RCON connection"""
        if self.socket:
            self.socket.close()
            self.socket = None
        self.connected = False
    
    def _create_packet(self, packet_type: int, data: str) -> bytes:
        """Create an RCON packet"""
        data_bytes = data.encode('utf-8')
        length = len(data_bytes) + 10
        packet_id = 1
        
        packet = bytearray()
        packet.extend(length.to_bytes(4, 'little'))
        packet.extend(packet_id.to_bytes(4, 'little'))
        packet.extend(packet_type.to_bytes(4, 'little'))
        packet.extend(data_bytes)
        packet.extend(b'\x00\x00')
        
        return bytes(packet)
    
    def _read_packet(self) -> Tuple[int, int, bytes]:
        """Read an RCON packet response"""
        length_bytes = self.socket.recv(4)
        if len(length_bytes) < 4:
            raise RuntimeError("Failed to read packet length")
        
        length = int.from_bytes(length_bytes, 'little')
        
        packet_id_bytes = self.socket.recv(4)
        packet_type_bytes = self.socket.recv(4)
        
        data_length = length - 8
        data = b''
        while len(data) < data_length:
            chunk = self.socket.recv(data_length - len(data))
            if not chunk:
                break
            data += chunk
        
        packet_id = int.from_bytes(packet_id_bytes, 'little')
        packet_type = int.from_bytes(packet_type_bytes, 'little')
        
        return packet_id, packet_type, data

# -----------------------------------------------------------------------------
# Observation helpers
# -----------------------------------------------------------------------------

class FactorioObservationCallable(GetObservationCallable):
    def __init__(self) -> None:
        pass

    async def get_observation(
        self, pub: FactorioPublicState, priv: FactorioPrivateState
    ) -> InternalObservation:  # type: ignore[override]
        observation = pub.last_code_output
        if pub.last_error_output:
            observation += "\n" + pub.last_error_output
        
        return {
            "output": observation,
            "step": pub.step_count,
            "scenario": pub.scenario_name,
            "reward_last": priv.reward_last_step,
            "total_reward": priv.total_reward_episode,
            "terminated": priv.terminated,
            "truncated": priv.truncated,
            "production": pub.production_metrics,
        }

# -----------------------------------------------------------------------------
# Factorio Tools (simplified subset)
# -----------------------------------------------------------------------------

class FactorioTools:
    """Python API tools for Factorio interactions"""
    
    def __init__(self, rcon_client: FactorioRCON):
        self.rcon = rcon_client
    
    def get_entities(self, entity_type: Optional[str] = None) -> str:
        """Get list of entities in the world"""
        if entity_type:
            cmd = f'/sc game.print(serpent.line(game.player.surface.find_entities_filtered{{name="{entity_type}"}}):sub(1,500))'
        else:
            cmd = '/sc game.print(serpent.line(game.player.surface.find_entities()):sub(1,500))'
        return self.rcon.send_command(cmd)
    
    def place_entity(self, entity_name: str, x: float, y: float, direction: int = 0) -> str:
        """Place an entity at the specified position"""
        cmd = f'/sc local entity = game.player.surface.create_entity{{name="{entity_name}", position={{{x}, {y}}}, direction={direction}}}; game.print(entity and "Placed " .. entity.name .. " at " .. entity.position.x .. "," .. entity.position.y or "Failed to place entity")'
        return self.rcon.send_command(cmd)
    
    def craft_item(self, item_name: str, count: int = 1) -> str:
        """Craft items"""
        cmd = f'/sc local result = game.player.begin_crafting{{recipe="{item_name}", count={count}}}; game.print("Crafting " .. {count} .. " " .. "{item_name}" .. ", queued: " .. result)'
        return self.rcon.send_command(cmd)
    
    def get_inventory(self) -> str:
        """Get player inventory contents"""
        cmd = '/sc local inv = {}; for name, count in pairs(game.player.get_main_inventory().get_contents()) do inv[name] = count end; game.print(serpent.line(inv))'
        return self.rcon.send_command(cmd)
    
    def get_production_stats(self) -> str:
        """Get production statistics"""
        cmd = '/sc local stats = game.player.force.item_production_statistics.output_counts; game.print(serpent.line(stats))'
        return self.rcon.send_command(cmd)
    
    def move_to(self, x: float, y: float) -> str:
        """Move player to position"""
        cmd = f'/sc game.player.teleport({{{x}, {y}}}); game.print("Moved to " .. {x} .. "," .. {y})'
        return self.rcon.send_command(cmd)

# -----------------------------------------------------------------------------
# Reward Components
# -----------------------------------------------------------------------------

class FactorioProductionComponent(RewardComponent):
    """Reward component based on production increase"""
    
    async def score(self, state: FactorioPublicState, action: Any) -> float:
        # Simple production-based reward
        total_production = sum(state.production_metrics.values())
        # This would need previous state for proper diff calculation
        return float(total_production) * 0.001

class FactorioStepPenaltyComponent(RewardComponent):
    """Small step penalty to encourage efficiency"""
    
    def __init__(self, penalty: float = -0.001):
        super().__init__()
        self.penalty = penalty
        self.weight = 1.0
    
    async def score(self, state: Any, action: Any) -> float:
        return self.penalty

# -----------------------------------------------------------------------------
# FactorioEngine implementation
# -----------------------------------------------------------------------------

class FactorioEngine(StatefulEngine, IReproducibleEngine):
    """StatefulEngine wrapper around Factorio Learning Environment"""

    task_instance: TaskInstance
    
    def __init__(self, task_instance: TaskInstance):
        self.task_instance = task_instance
        self._total_reward: float = 0.0
        
        # Configuration
        cfg = getattr(task_instance, "config", {}) or {}
        self.scenario_name = cfg.get("scenario", "lab")
        self.max_steps = cfg.get("max_steps", 1000)
        self.rcon_host = cfg.get("rcon_host", "localhost")
        self.rcon_port = cfg.get("rcon_port", 27015)
        self.rcon_password = cfg.get("rcon_password", "factorio")
        self.auto_start = cfg.get("auto_start", True)
        
        # State tracking
        self.step_count = 0
        self.agent_namespace: Dict[str, Any] = {}
        self.production_metrics: Dict[str, int] = {}
        self.rcon_client: Optional[FactorioRCON] = None
        self.tools: Optional[FactorioTools] = None
        
        # Reward system
        self.reward_stack = RewardStack(components=[
            FactorioProductionComponent(),
            FactorioStepPenaltyComponent(penalty=-0.001)
        ])
        
        # Auto-start server if configured
        if self.auto_start:
            self._start_factorio_server()

    def _start_factorio_server(self) -> bool:
        """Start the Factorio server via Docker"""
        try:
            # Check if container is already running
            result = subprocess.run(
                ["docker", "ps", "--filter", "name=factorio_env", "--format", "{{.Names}}"],
                capture_output=True, text=True
            )
            
            if "factorio_env" in result.stdout:
                logger.info("Factorio server already running")
                return True
            
            # Start new container
            cmd = [
                "docker", "run", "-d", "--rm",
                "-p", f"{self.rcon_port}:{self.rcon_port}",
                "-p", "34197:34197/udp",
                "--name", "factorio_env",
                "factorio-env-image",
                "--start-server-load-latest",
                "--scenario", f"{self.scenario_name}_scenario",
                "--rcon-password", self.rcon_password,
                "--rcon-port", str(self.rcon_port)
            ]
            
            subprocess.run(cmd, check=True)
            
            # Wait for server to start
            time.sleep(5)
            logger.info("Factorio server started")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start Factorio server: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error starting server: {e}")
            return False

    def _connect_rcon(self) -> bool:
        """Connect to Factorio RCON"""
        if self.rcon_client and self.rcon_client.connected:
            return True
        
        self.rcon_client = FactorioRCON(self.rcon_host, self.rcon_port, self.rcon_password)
        
        # Retry connection with backoff
        for attempt in range(5):
            if self.rcon_client.connect():
                self.tools = FactorioTools(self.rcon_client)
                logger.info("RCON connected successfully")
                return True
            time.sleep(2 ** attempt)
        
        logger.error("Failed to connect to RCON after retries")
        return False

    def _setup_agent_namespace(self):
        """Setup the Python namespace with Factorio tools"""
        self.agent_namespace.clear()
        
        if self.tools:
            # Add tool functions to namespace
            self.agent_namespace.update({
                'get_entities': self.tools.get_entities,
                'place_entity': self.tools.place_entity,
                'craft_item': self.tools.craft_item,
                'get_inventory': self.tools.get_inventory,
                'get_production_stats': self.tools.get_production_stats,
                'move_to': self.tools.move_to,
                'print': print,  # Allow printing
            })

    def _execute_agent_code(self, code: str) -> Tuple[str, str]:
        """Execute agent code and capture output/errors"""
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()
        
        try:
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(error_buffer):
                exec(code, self.agent_namespace, self.agent_namespace)
        except Exception as e:
            traceback.print_exc(file=error_buffer)
        
        output = output_buffer.getvalue()
        error = error_buffer.getvalue()
        
        return output, error

    def _get_production_metrics(self) -> Dict[str, int]:
        """Get current production metrics from Factorio"""
        if not self.tools:
            return {}
        
        try:
            stats_str = self.tools.get_production_stats()
            # Parse the returned stats (simplified)
            # In real implementation, would parse Lua serpent output
            return {"iron_plates": 0, "copper_plates": 0}  # Placeholder
        except Exception as e:
            logger.error(f"Failed to get production metrics: {e}")
            return {}

    # ────────────────────────────────────────────────────────────────────────
    # Core StatefulEngine API
    # ────────────────────────────────────────────────────────────────────────

    async def _reset_engine(
        self, *, seed: Optional[int] = None
    ) -> Tuple[FactorioPrivateState, FactorioPublicState]:
        """Reset the Factorio environment"""
        self.step_count = 0
        self._total_reward = 0.0
        
        # Connect to RCON if not connected
        rcon_connected = self._connect_rcon()
        
        if rcon_connected:
            # Reset game state (simplified - would trigger scenario restart)
            self.rcon_client.send_command("/c game.reset_scenario()")
            self._setup_agent_namespace()
        
        # Initialize production metrics
        self.production_metrics = self._get_production_metrics()
        
        priv = FactorioPrivateState(
            reward_last_step=0.0,
            total_reward_episode=0.0,
            terminated=False,
            truncated=False,
            rcon_connected=rcon_connected
        )
        
        pub = FactorioPublicState(
            scenario_name=self.scenario_name,
            step_count=0,
            max_steps=self.max_steps,
            last_code_output="",
            last_error_output="",
            production_metrics=self.production_metrics.copy(),
            is_server_running=rcon_connected
        )
        
        return priv, pub

    async def _step_engine(
        self, action: str
    ) -> Tuple[FactorioPrivateState, FactorioPublicState]:
        """Execute agent code action and return new state"""
        self.step_count += 1
        
        # Execute the agent's code
        output, error = self._execute_agent_code(action)
        
        # Update production metrics
        prev_production = self.production_metrics.copy()
        self.production_metrics = self._get_production_metrics()
        
        # Build public state
        pub = FactorioPublicState(
            scenario_name=self.scenario_name,
            step_count=self.step_count,
            max_steps=self.max_steps,
            last_code_output=output,
            last_error_output=error,
            production_metrics=self.production_metrics.copy(),
            is_server_running=self.rcon_client.connected if self.rcon_client else False
        )
        
        # Calculate reward
        reward = await self.reward_stack.step_reward(state=pub, action=action)
        self._total_reward += reward
        
        # Check termination conditions
        terminated = False
        truncated = self.step_count >= self.max_steps
        
        # Build private state
        priv = FactorioPrivateState(
            reward_last_step=reward,
            total_reward_episode=self._total_reward,
            terminated=terminated,
            truncated=truncated,
            rcon_connected=self.rcon_client.connected if self.rcon_client else False
        )
        
        return priv, pub

    async def _render(
        self,
        private_state: FactorioPrivateState,
        public_state: FactorioPublicState,
        get_observation: Optional[GetObservationCallable] = None,
    ) -> str:  # type: ignore[override]
        """Render the current state as text"""
        obs_cb = get_observation or FactorioObservationCallable()
        obs = await obs_cb.get_observation(public_state, private_state)
        
        if isinstance(obs, str):
            return obs
        
        if isinstance(obs, dict):
            header = f"Step {public_state.step_count}/{public_state.max_steps} | "
            header += f"Reward: {private_state.reward_last_step:.3f} | "
            header += f"Total: {private_state.total_reward_episode:.3f}"
            
            output = obs.get("output", "")
            if output:
                return f"{header}\n{output}"
            else:
                return header
        
        return str(obs)

    # ------------------------------------------------------------------
    # Snapshotting for reproducibility
    # ------------------------------------------------------------------

    async def _serialize_engine(self) -> FactorioEngineSnapshot:
        """Serialize engine state for snapshotting"""
        return FactorioEngineSnapshot(
            rcon_config={
                "host": self.rcon_host,
                "port": self.rcon_port,
                "password": self.rcon_password
            },
            scenario_name=self.scenario_name,
            total_reward_snapshot=self._total_reward,
            agent_namespace_snapshot=copy.deepcopy(self.agent_namespace),
            production_metrics=self.production_metrics.copy(),
            step_count=self.step_count
        )

    @classmethod
    async def _deserialize_engine(
        cls, snapshot: FactorioEngineSnapshot, task_instance: TaskInstance
    ) -> "FactorioEngine":
        """Deserialize engine from snapshot"""
        engine = cls(task_instance)
        
        # Restore state
        engine._total_reward = snapshot.total_reward_snapshot
        engine.step_count = snapshot.step_count
        engine.production_metrics = snapshot.production_metrics.copy()
        engine.scenario_name = snapshot.scenario_name
        
        # Restore RCON config
        engine.rcon_host = snapshot.rcon_config["host"]
        engine.rcon_port = snapshot.rcon_config["port"]
        engine.rcon_password = snapshot.rcon_config["password"]
        
        # Reconnect RCON
        engine._connect_rcon()
        engine._setup_agent_namespace()
        
        return engine

    def close(self):
        """Clean up resources"""
        if self.rcon_client:
            self.rcon_client.close()
        
        if self.auto_start:
            try:
                subprocess.run(["docker", "stop", "factorio_env"], capture_output=True)
            except Exception as e:
                logger.error(f"Error stopping Factorio server: {e}")