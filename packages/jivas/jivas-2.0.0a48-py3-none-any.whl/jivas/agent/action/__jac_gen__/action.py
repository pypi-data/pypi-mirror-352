from __future__ import annotations
from jaclang import *
import typing
from enum import Enum, auto
if typing.TYPE_CHECKING:
    import logging
else:
    logging, = jac_import('logging', 'py')
if typing.TYPE_CHECKING:
    import traceback
else:
    traceback, = jac_import('traceback', 'py')
if typing.TYPE_CHECKING:
    from logging import Logger
else:
    Logger, = jac_import('logging', 'py', items={'Logger': None})
if typing.TYPE_CHECKING:
    from jivas.agent.core.graph_node import GraphNode
else:
    GraphNode, = jac_import('jivas.agent.core.graph_node', items={'GraphNode': None})
if typing.TYPE_CHECKING:
    from jivas.agent.memory.collection import Collection
else:
    Collection, = jac_import('jivas.agent.memory.collection', items={'Collection': None})

class Action(GraphNode, Node):
    agent_id: str = field('')
    version: str = field('')
    label: str = field('')
    description: str = field('basic agent action')
    enabled: bool = field(True)
    _package: dict = field(gen=lambda: {})
    logger: static[Logger] = logging.getLogger(__name__)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.protected_attrs += JacList(['_package', 'label', 'version', 'agent_id'])
        self.transient_attrs += JacList(['agent_id'])

    def on_register(self) -> None:
        pass

    def post_register(self) -> None:
        pass

    def on_enable(self) -> None:
        pass

    def on_disable(self) -> None:
        pass

    def on_deregister(self) -> None:
        pass

    def pulse(self) -> None:
        pass

    def analytics(self) -> None:
        pass

    def healthcheck(self) -> Union[bool, dict]:
        return True

    def update(self, data: dict={}) -> GraphNode:
        if data:
            for attr in data.keys():
                if attr not in self.protected_attrs:
                    if hasattr(self, attr):
                        if attr == 'enabled' and getattr(self, attr) != data[attr]:
                            if data[attr] == True:
                                self.on_enable()
                            else:
                                self.on_disable()
                        setattr(self, attr, data[attr])
                    else:
                        self._context[attr] = data[attr]
        self.get_agent().dump_descriptor()
        self.post_update()
        return self

    def get_agent(self) -> None:
        return jobj(id=self.agent_id)

    def get_namespace(self) -> None:
        return self._package.get('config', {}).get('namespace', None)

    def get_module(self) -> None:
        return self._package.get('config', {}).get('module', None)

    def get_module_root(self) -> None:
        return self._package.get('config', {}).get('module_root', None)

    def get_package_path(self) -> None:
        return self._package.get('config', {}).get('path', None)

    def get_version(self) -> None:
        return self.version

    def get_package_name(self) -> None:
        return self._package.get('config', {}).get('package_name', None)

    def get_namespace_package_name(self) -> None:
        return self._package.get('name', None)

    def get_collection(self) -> Collection:
        return self.get_agent().get_memory().get_collection(self.label)

    def remove_collection(self) -> list:
        return self.get_agent().get_memory().purge_collection_memory(self.label)

    def get_file(self, path: str) -> bytes | None:
        return self.get_agent().get_file(f'{self.get_type()}/{path}')

    def save_file(self, path: str, content: bytes) -> bool:
        return self.get_agent().save_file(f'{self.get_type()}/{path}', content)

    def delete_file(self, path: str) -> bool:
        return self.get_agent().delete_file(f'{self.get_type()}/{path}')

    def get_file_url(self, path: str) -> str | None:
        return self.get_agent().get_file_url(f'{self.get_type()}/{path}')

    def get_short_file_url(self, path: str, with_filename: bool=False) -> str | None:
        return self.get_agent().get_short_file_url(f'{self.get_type()}/{path}', with_filename)