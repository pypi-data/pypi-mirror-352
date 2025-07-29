#!/usr/bin/env python3
"""
Comprehensive tests to expose and debug Verilog environment issues.

This test suite specifically targets the issues identified in env_debugging.py:
1. Module naming mismatch (TopModule vs top_module1)
2. Simulate status parsing issues
3. Missing VVP output in observations
4. Task completion detection bugs
"""

import pytest
import tempfile
import json
import subprocess
import logging
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict, Any

# Setup logging for detailed debugging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import the Verilog environment components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.verilog.environment import VerilogEnvironment, VerilogObservationCallable
from examples.verilog.engine import VerilogEngine
from examples.verilog.taskset import create_verilog_taskset


class TestModuleNamingIssue:
    """Test the module naming mismatch issue."""
    
    @pytest.mark.asyncio
    async def test_module_naming_mismatch_reproduction(self):
        """
        Reproduce the exact module naming issue where:
        1. Task description says "implement a module named TopModule"
        2. Agent creates module TopModule(...)
        3. Testbench expects top_module1
        4. Compilation fails
        """
        logger.info("=== Testing Module Naming Mismatch Issue ===")
        
        # Create a simple task that demonstrates the issue
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create task files that reproduce the issue
            # 1. TopModule.v - what the agent would create
            top_module_content = """module TopModule(
    input wire a,
    input wire b,
    output wire out
);
    assign out = a & b;
endmodule
"""
            
            # 2. testbench that expects top_module1 (common in VerilogEval)
            testbench_content = """module tb();
    reg a, b;
    wire out;
    
    // This expects 'top_module1' not 'TopModule' - this is the bug!
    top_module1 uut(
        .a(a),
        .b(b),
        .out(out)
    );
    
    initial begin
        a = 0; b = 0; #10;
        $display("Test: a=%b, b=%b, out=%b", a, b, out);
        
        a = 1; b = 0; #10;
        $display("Test: a=%b, b=%b, out=%b", a, b, out);
        
        a = 1; b = 1; #10;
        $display("Test: a=%b, b=%b, out=%b", a, b, out);
        
        $finish;
    end
endmodule
"""
            
            # Write files
            (temp_path / "TopModule.v").write_text(top_module_content)
            (temp_path / "testbench.v").write_text(testbench_content)
            
            # Try to compile - this should fail with module naming error
            build_dir = temp_path / "build"
            build_dir.mkdir()
            
            cmd = [
                "iverilog", "-g2012", 
                "-o", str(build_dir / "test.out"),
                str(temp_path / "TopModule.v"),
                str(temp_path / "testbench.v")
            ]
            
            logger.info(f"Running compile command: {' '.join(cmd)}")
            proc = subprocess.run(cmd, capture_output=True, text=True)
            
            logger.info(f"Compile returncode: {proc.returncode}")
            logger.info(f"Compile stdout: {proc.stdout}")
            logger.info(f"Compile stderr: {proc.stderr}")
            
            # This should fail because testbench expects 'top_module1' but module is 'TopModule'
            assert proc.returncode != 0, "Compilation should fail due to module name mismatch"
            assert "top_module1" in proc.stderr, "Error should mention the expected module name"
            
            # Log the exact error for debugging
            logger.error(f"Module naming mismatch error (as expected): {proc.stderr}")
            
    @pytest.mark.asyncio
    async def test_get_actual_task_module_names(self):
        """
        Load actual VerilogEval tasks and check what module names they expect.
        This will help us understand the scope of the naming issue.
        """
        logger.info("=== Analyzing Actual Task Module Names ===")
        
        try:
            # Load a small sample of tasks
            taskset = await create_verilog_taskset(max_instances=5)
            
            for task in taskset.instances:
                logger.info(f"\n--- Task: {task.metadata.problem_name} ---")
                logger.info(f"Description: {task.impetus.instructions[:200]}...")
                
                # Check files provided with task
                if hasattr(task, 'initial_engine_snapshot') and task.initial_engine_snapshot:
                    snapshot_data = task.initial_engine_snapshot
                    if 'files' in snapshot_data:
                        for filename, content in snapshot_data['files'].items():
                            if filename.endswith('_tb.v') or 'testbench' in filename.lower():
                                # Analyze testbench for module instantiation
                                logger.info(f"Testbench file: {filename}")
                                
                                # Look for module instantiation patterns
                                lines = content.split('\n')
                                for i, line in enumerate(lines):
                                    line_stripped = line.strip()
                                    # Look for module instantiation (not declaration)
                                    if (line_stripped and 
                                        not line_stripped.startswith('//') and
                                        not line_stripped.startswith('module ') and
                                        ('uut' in line_stripped or 'dut' in line_stripped or 
                                         line_stripped.endswith('('))):
                                        
                                        # Check if this looks like a module instantiation
                                        words = line_stripped.split()
                                        if len(words) >= 2 and not any(kw in line_stripped for kw in ['reg', 'wire', 'input', 'output', 'assign']):
                                            potential_module = words[0]
                                            if potential_module not in ['initial', 'always', 'assign', 'begin', 'end']:
                                                logger.warning(f"  Potential module instance: '{potential_module}' at line {i+1}: {line_stripped}")
                
        except Exception as e:
            logger.error(f"Failed to load taskset: {e}")
            # Skip this test if we can't load tasks
            pytest.skip(f"Could not load VerilogEval tasks: {e}")


class TestSimulateStatusIssue:
    """Test the simulate status parsing issue."""
    
    @pytest.mark.asyncio
    async def test_vvp_output_parsing_success(self):
        """Test that VVP success output is correctly parsed."""
        logger.info("=== Testing VVP Success Output Parsing ===")
        
        # Mock VVP output for a successful simulation
        mock_vvp_success_output = """VCD info: dumpfile testbench.vcd opened for output.
Hint: Output 'out' has no mismatches.
Hint: Total mismatched samples is 0 out of 100 samples

Simulation finished at 1000 ps
Mismatches: 0 in 100 samples
"""
        
        # Test the current parsing logic from engine.py
        stdout = mock_vvp_success_output
        passed = (
            "ALL_TESTS_PASSED" in stdout or
            ("Mismatches: 0 " in stdout and "samples" in stdout) or
            ("no mismatches" in stdout.lower() and "errors" not in stdout.lower())
        )
        
        logger.info(f"VVP Success Output:\n{stdout}")
        logger.info(f"Parsed as passed: {passed}")
        
        assert passed, "VVP success output should be parsed as passed"
        
    @pytest.mark.asyncio  
    async def test_vvp_output_parsing_failure(self):
        """Test that VVP failure output is correctly parsed."""
        logger.info("=== Testing VVP Failure Output Parsing ===")
        
        # Mock VVP output for a failed simulation
        mock_vvp_failure_output = """VCD info: dumpfile testbench.vcd opened for output.
Hint: Output 'out' has 25 mismatches. First mismatch occurred at time 250.
Hint: Total mismatched samples is 25 out of 100 samples

Simulation finished at 1000 ps
Mismatches: 25 in 100 samples
"""
        
        # Test the current parsing logic
        stdout = mock_vvp_failure_output
        passed = (
            "ALL_TESTS_PASSED" in stdout or
            ("Mismatches: 0 " in stdout and "samples" in stdout) or
            ("no mismatches" in stdout.lower() and "errors" not in stdout.lower())
        )
        
        logger.info(f"VVP Failure Output:\n{stdout}")
        logger.info(f"Parsed as passed: {passed}")
        
        assert not passed, "VVP failure output should be parsed as failed"
        
    @pytest.mark.asyncio
    async def test_observation_includes_vvp_output(self):
        """Test that VVP output is included in environment observations."""
        logger.info("=== Testing VVP Output in Observations ===")
        
        # This test checks if the actual VVP stdout is available to agents
        # Currently it might not be, which is a problem
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a simple working Verilog module and testbench
            module_content = """module TopModule(
    input wire a,
    output wire out
);
    assign out = a;
endmodule
"""
            
            testbench_content = """module testbench();
    reg a;
    wire out;
    
    TopModule uut(
        .a(a),
        .out(out)
    );
    
    initial begin
        $dumpfile("test.vcd");
        $dumpvars(0, testbench);
        
        a = 0; #10;
        if (out !== 0) $display("MISMATCH: Expected 0, got %b", out);
        
        a = 1; #10;
        if (out !== 1) $display("MISMATCH: Expected 1, got %b", out);
        
        $display("Mismatches: 0 in 2 samples");
        $finish;
    end
endmodule
"""
            
            # Create a mock task instance
            mock_task = MagicMock()
            mock_task.id = "test_task"
            mock_task.impetus.instructions = "Test task"
            mock_task.metadata.problem_name = "test_problem"
            mock_task.initial_engine_snapshot = {}
            mock_task.snapshot_dir = temp_path
            mock_task.pristine_dir = temp_path
            
            # Write files to temp directory
            (temp_path / "TopModule.v").write_text(module_content)
            (temp_path / "testbench.v").write_text(testbench_content)
            
            # Create VerilogEnvironment (not engine directly) and test
            env = VerilogEnvironment(mock_task)
            obs = await env.initialize()
            logger.info(f"Initial observation: {obs}")
            
            # Compile
            compile_obs = await env.step({
                "tool": "compile",
                "args": {"sources": ["TopModule.v"], "testbench": "testbench.v"}
            })
            logger.info(f"Compile observation: {compile_obs}")
            assert "compile_status" in compile_obs, "Should have compile status"
            
            compile_status = compile_obs.get("compile_status", "")
            if "Failed" in compile_status:
                logger.error(f"Compilation failed: {compile_status}")
                pytest.fail(f"Compilation should succeed but failed: {compile_status}")
            
            # Simulate
            simulate_obs = await env.step({
                "tool": "simulate",
                "args": {}
            })
            logger.info(f"Simulate observation: {simulate_obs}")
            
            # Check if VVP stdout is captured somewhere
            simulate_status = simulate_obs.get("simulate_status", "")
            logger.info(f"Simulate status from observation: '{simulate_status}'")
            
            # Check if it's properly parsed
            task_completed = simulate_obs.get("task_completed", False)
            logger.info(f"Task completed after simulation: {task_completed}")
            
            # The key issue: Are agents getting the actual VVP output?
            # Currently they only get the parsed simulate_status, not the raw VVP output
            if "vvp_output" not in simulate_obs:
                logger.warning("⚠️  MISSING VVP OUTPUT: Agents cannot see raw VVP output in observations")
                logger.warning("   This means agents must rely on parsed simulate_status which may be buggy")
            else:
                vvp_output = simulate_obs["vvp_output"]
                logger.info(f"✅ VVP output is available to agents: {vvp_output[:100]}...")
                
            # Check if simulation was correctly detected as successful
            if "Mismatches: 0" in str(simulate_obs):
                logger.info("✅ VVP output contains success pattern")
                if "Failed" in simulate_status:
                    logger.error("❌ BUG DETECTED: VVP shows success but simulate_status shows 'Failed'")
                    logger.error(f"   Raw simulate_status: '{simulate_status}'")
            else:
                logger.warning(f"VVP success pattern not found in observation: {simulate_obs}")


class TestTaskCompletionIssue:
    """Test task completion detection."""
    
    @pytest.mark.asyncio
    async def test_task_completion_on_successful_simulation(self):
        """Test that task_completed is set correctly when simulation passes."""
        logger.info("=== Testing Task Completion Detection ===")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a simple correct solution
            mock_task = MagicMock()
            mock_task.id = "test_task"
            mock_task.impetus.instructions = "Test task"
            mock_task.metadata.problem_name = "test_problem"
            mock_task.initial_engine_snapshot = {}
            mock_task.snapshot_dir = temp_path
            mock_task.pristine_dir = temp_path
            
            # Create working module and testbench
            module_content = """module TopModule(input a, output out);
    assign out = a;
endmodule
"""
            testbench_content = """module tb();
    reg a; wire out;
    TopModule uut(.a(a), .out(out));
    initial begin
        a = 0; #10; 
        if (out !== 0) $display("MISMATCH at test 1");
        a = 1; #10;
        if (out !== 1) $display("MISMATCH at test 2");
        $display("Mismatches: 0 in 2 samples");
        $finish;
    end
endmodule
"""
            
            (temp_path / "TopModule.v").write_text(module_content)
            (temp_path / "testbench.v").write_text(testbench_content)
            
            # Test with environment
            env = VerilogEnvironment(mock_task)
            await env.initialize()
            
            # Compile
            await env.step({"tool": "compile", "args": {"sources": ["TopModule.v"], "testbench": "testbench.v"}})
            
            # Simulate
            obs = await env.step({"tool": "simulate", "args": {}})
            
            # Check task completion
            task_completed = obs.get("task_completed", False)
            logger.info(f"Task completed after successful simulation: {task_completed}")
            
            # This might reveal the bug - task might not be marked complete even after successful simulation
            if not task_completed:
                logger.warning("⚠️  POTENTIAL BUG: Task not marked complete after successful simulation")
                
                # Let's check what the simulate_status says
                simulate_status = obs.get("simulate_status", "")
                logger.info(f"Simulate status: '{simulate_status}'")
                
                # And let's submit to see what happens
                submit_obs = await env.step({"tool": "submit", "args": {}})
                logger.info(f"Submit observation: {submit_obs}")
                
                task_completed_after_submit = submit_obs.get("task_completed", False)
                logger.info(f"Task completed after submit: {task_completed_after_submit}")
                
            # For now, let's just log this for investigation
            logger.info(f"Final task completion state: {task_completed}")


class TestEnvironmentIntegrationIssues:
    """Integration tests to catch environment-wide issues."""
    
    @pytest.mark.asyncio
    async def test_full_agent_workflow_simulation(self):
        """Simulate a full agent workflow to catch integration issues."""
        logger.info("=== Testing Full Agent Workflow ===")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a mock task that represents a typical VerilogEval problem
            mock_task = MagicMock()
            mock_task.id = "test_task"
            mock_task.impetus.instructions = """
            Implement a module named TopModule with the following interface:
            - input a
            - input b  
            - output out
            
            The module should output the AND of the two inputs.
            """
            mock_task.metadata.problem_name = "test_and_gate"
            mock_task.initial_engine_snapshot = {}
            mock_task.snapshot_dir = temp_path
            mock_task.pristine_dir = temp_path
            
            # Provide initial files (like a real VerilogEval task would)
            testbench_content = """module testbench();
    reg a, b;
    wire out;
    
    // This uses TopModule - correct module name
    TopModule uut(
        .a(a),
        .b(b), 
        .out(out)
    );
    
    initial begin
        $dumpfile("test.vcd");
        $dumpvars(0, testbench);
        
        // Test all combinations
        a = 0; b = 0; #10;
        if (out !== 0) $display("MISMATCH: Expected 0, got %b at test 1", out);
        
        a = 0; b = 1; #10;
        if (out !== 0) $display("MISMATCH: Expected 0, got %b at test 2", out);
        
        a = 1; b = 0; #10;
        if (out !== 0) $display("MISMATCH: Expected 0, got %b at test 3", out);
        
        a = 1; b = 1; #10;
        if (out !== 1) $display("MISMATCH: Expected 1, got %b at test 4", out);
        
        $display("Mismatches: 0 in 4 samples");
        $finish;
    end
endmodule
"""
            
            (temp_path / "testbench.v").write_text(testbench_content)
            
            # Create environment
            env = VerilogEnvironment(mock_task)
            
            # Simulate agent actions
            logger.info("Step 1: Initialize environment")
            obs = await env.initialize()
            logger.info(f"Initial observation keys: {list(obs.keys())}")
            
            logger.info("Step 2: Agent writes module")
            obs = await env.step({
                "tool": "write_file",
                "args": {
                    "path": "TopModule.v",
                    "content": """module TopModule(
    input a,
    input b,
    output out
);
    assign out = a & b;
endmodule
"""
                }
            })
            logger.info(f"After write_file - files: {obs.get('files', {}).keys()}")
            
            logger.info("Step 3: Agent compiles")
            obs = await env.step({
                "tool": "compile", 
                "args": {"sources": ["TopModule.v"], "testbench": "testbench.v"}
            })
            compile_status = obs.get("compile_status", "")
            logger.info(f"Compile status: '{compile_status}'")
            
            if "Failed" in compile_status:
                logger.error(f"❌ Compilation failed: {compile_status}")
                # This might be the module naming issue
                return
                
            logger.info("Step 4: Agent simulates")
            obs = await env.step({
                "tool": "simulate",
                "args": {}
            })
            simulate_status = obs.get("simulate_status", "")
            task_completed = obs.get("task_completed", False)
            
            logger.info(f"Simulate status: '{simulate_status}'")
            logger.info(f"Task completed: {task_completed}")
            
            # Check for the issues we're investigating
            if "Failed" in simulate_status and not task_completed:
                logger.warning("⚠️  POTENTIAL ISSUE: Simulation marked as failed despite correct implementation")
                
            logger.info("Step 5: Agent submits")
            obs = await env.step({
                "tool": "submit",
                "args": {}
            })
            
            final_task_completed = obs.get("task_completed", False)
            logger.info(f"Final task completed: {final_task_completed}")
            
            # Log final state for analysis
            logger.info("=== FINAL WORKFLOW STATE ===")
            logger.info(f"Compile Status: '{obs.get('compile_status', '')}'")
            logger.info(f"Simulate Status: '{obs.get('simulate_status', '')}'")
            logger.info(f"Task Completed: {obs.get('task_completed', False)}")
            logger.info(f"Total Reward: {obs.get('total_reward', 0)}")


if __name__ == "__main__":
    # Run with detailed logging
    pytest.main([__file__, "-v", "-s", "--tb=short"]) 