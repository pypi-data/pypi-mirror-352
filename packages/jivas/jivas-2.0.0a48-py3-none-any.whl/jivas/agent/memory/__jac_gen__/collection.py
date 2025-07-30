from __future__ import annotations
from jaclang import *
import typing
from enum import Enum, auto
if typing.TYPE_CHECKING:
    from jivas.agent.core.graph_node import GraphNode
else:
    GraphNode, = jac_import('jivas.agent.core.graph_node', items={'GraphNode': None})

class Collection(GraphNode, Node):
    name: str = field('')
    data: dict = field(gen=lambda: {})

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name

    def get_data_item(self, label: str) -> any:
        return self.data.get(label, None)

    def set_data_item(self, label: str, value: any) -> None:
        self.data[label] = value