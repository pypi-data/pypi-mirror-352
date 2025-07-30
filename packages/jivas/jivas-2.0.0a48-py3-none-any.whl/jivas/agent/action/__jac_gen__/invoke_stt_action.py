from __future__ import annotations
from jaclang import *
import typing
from enum import Enum, auto
if typing.TYPE_CHECKING:
    from jivas.agent.core.agent import Agent
else:
    Agent, = jac_import('jivas.agent.core.agent', items={'Agent': None})
if typing.TYPE_CHECKING:
    from jivas.agent.action.action import Action
else:
    Action, = jac_import('jivas.agent.action.action', items={'Action': None})
if typing.TYPE_CHECKING:
    from jivas.agent.action.actions import Actions
else:
    Actions, = jac_import('jivas.agent.action.actions', items={'Actions': None})
if typing.TYPE_CHECKING:
    from jivas.agent.action.interact_graph_walker import interact_graph_walker
else:
    interact_graph_walker, = jac_import('jivas.agent.action.interact_graph_walker', items={'interact_graph_walker': None})
if typing.TYPE_CHECKING:
    import os
else:
    os, = jac_import('os', 'py')
if typing.TYPE_CHECKING:
    import uuid
else:
    uuid, = jac_import('uuid', 'py')
if typing.TYPE_CHECKING:
    import base64
else:
    base64, = jac_import('base64', 'py')

class invoke_stt_action(interact_graph_walker, Walker):
    files: list[dict] = field(gen=lambda: JacList([]))

    @with_entry
    def on_agent(self, here: Agent) -> None:
        action_node = here.get_stt_action()
        if not self.files:
            self.response = {'success': False, 'message': 'No audio file provided'}
        else:
            file = self.files[0]
            if 'audio' in file['type'] or file['type'] == 'application/octet-stream':
                result = action_node.invoke_file(audio_content=file['content'], audio_type=file['type'])
                self.response = {'success': True, 'duration': result['duration'], 'transcript': result['transcript']}
            else:
                self.response = {'success': False, 'message': 'Invalid file type, must be audio'}