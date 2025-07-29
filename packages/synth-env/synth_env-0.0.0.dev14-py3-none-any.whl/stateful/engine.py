from environment.shared_engine import Engine
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Any, Tuple, Optional, Type
from dataclasses import dataclass, asdict

SnapshotType = TypeVar("SnapshotType", bound="StatefulEngineSnapshot")


class StatefulEngineSnapshot:
    pass


class StatefulEngine(Engine):
    async def serialize(self):
        pass

    @classmethod
    async def deserialize(cls, engine_snapshot: StatefulEngineSnapshot):
        pass

    async def _step_engine(self):
        pass
