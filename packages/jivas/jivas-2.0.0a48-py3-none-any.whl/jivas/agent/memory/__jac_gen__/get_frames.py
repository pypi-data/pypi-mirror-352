from __future__ import annotations
from jaclang import *
import typing
from enum import Enum, auto
if typing.TYPE_CHECKING:
    from jivas.agent.memory.memory_frame_walker import memory_frame_walker
else:
    memory_frame_walker, = jac_import('jivas.agent.memory.memory_frame_walker', items={'memory_frame_walker': None})
if typing.TYPE_CHECKING:
    from jivas.agent.memory.memory import Memory
else:
    Memory, = jac_import('jivas.agent.memory.memory', items={'Memory': None})

class get_frames(memory_frame_walker, Walker):
    session_id: str = field('')

    class __specs__(Obj):
        private: static[bool] = False

    @with_entry
    def on_memory(self, here: Memory) -> None:
        frame_nodes = here.get_frames(self.session_id)
        for frame_node in frame_nodes:
            Jac.report(frame_node.export())