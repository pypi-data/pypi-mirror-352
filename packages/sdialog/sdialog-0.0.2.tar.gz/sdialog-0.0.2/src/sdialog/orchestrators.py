# SPDX-FileCopyrightText: Copyright © 2025 Idiap Research Institute <contact@idiap.ch>
# SPDX-FileContributor: Sergio Burdisso <sergio.burdisso@idiap.ch>
# SPDX-License-Identifier: MIT
import json
import random
import inspect
import numpy as np

from time import time
from abc import ABC, abstractmethod
from typing import List, Union, Dict, Optional
from sentence_transformers import SentenceTransformer
from langchain_core.messages import SystemMessage, AIMessage

from . import Turn, Event, Instruction
from .util import make_serializable
# from .personas import PersonaAgent


class BaseOrchestrator(ABC):
    _target = None
    _event_label = None
    _persistent = False

    def __init__(self, target_agent = None, persistent: bool = None, event_label: str = None):
        self._target = target_agent
        self._persistent = persistent
        self._event_label = event_label

    def __call__(self):
        dialog = self.__get_current_dialog()
        return self.instruct(dialog, dialog[-1].text if dialog and dialog[-1].speaker != self._target.get_name() else "")

    def __str__(self) -> str:
        data = self.json()
        attrs = " ".join(f"{key}={value}" for key, value in data["args"].items())
        return f"{data['name']}({attrs})"

    def __get_current_dialog(self) -> List[Turn]:
        return [Turn(speaker=self._target.get_name() if type(message) == AIMessage else None, text=message.content)
                for message in self._target.memory if type(message) != SystemMessage]

    def _set_target_agent(self, agent):  # target: PersonaAgent
        self._target = agent

    def json(self, string: bool = False, indent: int =None):
        sig = inspect.signature(self.__init__)
        data = {"name": type(self).__name__,
                "args": {key: self.__dict__[key] for key in sig.parameters
                         if key in self.__dict__ and self.__dict__[key] is not None}}
        make_serializable(data["args"])
        return json.dumps(data, indent=indent) if string else data

    def get_event_label(self) -> str:
        return self._event_label if self._event_label else type(self).__name__

    def get_target_agent(self):
        return self._target

    def is_persistent(self):
        return self._persistent

    def set_persistent(self, value: bool):
        self._persistent = value

    def agent_response_lookahead(self):
        return self._target.response_lookahead()

    @abstractmethod
    def instruct(self, dialog: List[Turn], utterance: str) -> str:
        pass

    def reset(self):
        pass


class BasePersistentOrchestrator(BaseOrchestrator):  #, ABC):
    _persistent = True

    @abstractmethod
    def instruct(self, dialog: List[Turn], utterance: str) -> str:
        pass

    def reset(self):
        pass


class SimpleReflexOrchestrator(BaseOrchestrator):
    def __init__(self, condition: callable, instruction: str, persistent: bool = False, event_label: str = None):
        super().__init__(persistent=persistent, event_label=event_label)
        self.condition = condition
        self.instruction = instruction

    def instruct(self, dialog: List[Turn], utterance: str) -> str:
        if self.condition(utterance):
            return self.instruction


class LengthOrchestrator(BaseOrchestrator):
    def __init__(self, min: int = None, max: int = None, persistent: bool = False, event_label: str = None):
        super().__init__(persistent=persistent, event_label=event_label)
        self.max = max
        self.min = min

    def instruct(self, dialog: List[Turn], utterance: str) -> str:
        if self.min is not None and len(dialog) < self.min and len(dialog) > 1:
            return "Make sure you DO NOT finish the conversation, keep it going!"
        elif self.max and len(dialog) >= self.max - 1:  # + answer
            return "Now FINISH the conversation AS SOON AS possible, if possible, RIGHT NOW!"


class ChangeMindOrchestrator(BaseOrchestrator):
    def __init__(self, probability: float = 0.3,
                 reasons: Union[str, List[str]] = None,
                 max_times: int = 1,
                 persistent: bool = False,
                 event_label: str = None):
        super().__init__(persistent=persistent, event_label=event_label)
        self.probability = probability
        self.reasons = [reasons] if type(reasons) == str else reasons
        self.max_times = max_times
        self.times = 0

    def reset(self):
        self.times = 0

    def instruct(self, dialog: List[Turn], utterance: str) -> str:
        if self.max_times and self.times >= self.max_times:
            return

        if random.random() <= self.probability:
            self.times += 1
            instruction = "Change your mind completely, in your next utterance, suggest something completely different!"
            if self.reasons:
                instruction += f" **Reason:** {random.choice(self.reasons)}."
            return instruction


class SimpleResponseOrchestrator(BaseOrchestrator):
    def __init__(self,
                 responses: List[Union[str, Dict[str, str]]],
                 graph: Dict[str, str] = None,
                #  sbert_model: str = "sentence-transformers/LaBSE",
                 sbert_model: str = "sergioburdisso/dialog2flow-joint-bert-base",
                 top_k: int = 5):

        self.sent_encoder = SentenceTransformer(sbert_model)
        self.responses = responses
        self.top_k = top_k

        if type(responses) == dict:
            self.resp_utts = np.array([resp for resp in responses.values()])
            self.resp_acts = np.array([act for act in responses.keys()])
            self.graph = graph
        else:
            self.resp_utts = np.array(responses)
            self.resp_acts = None
            self.graph = None

        self.resp_utt_embs = self.sent_encoder.encode(self.resp_utts)

    def instruct(self, dialog: List[Turn], utterance: str) -> str:
        agent = self.get_target_agent()

        agent_last_turn = None
        if self.graph and dialog:
            for turn in dialog[::-1]:
                if turn.speaker == agent.get_name():
                    agent_last_turn = turn.text
                    break

        response = agent_last_turn if agent_last_turn else agent.response_lookahead()

        events = [Event(agent=agent.get_name(),
                        action="request_suggestions",
                        actionLabel=self.get_event_label(),
                        text=f'Previous response: "{response}"' if agent_last_turn else f'Lookahead response: "{response}"',
                        timestamp=int(time()))]

        sims = self.sent_encoder.similarity(self.sent_encoder.encode(response), self.resp_utt_embs)[0]
        top_k_ixs = sims.argsort(descending=True)[:self.top_k]

        if self.resp_acts is None:
            instruction = ("If applicable, try to pick your next response from the following list: " +
                           "; ".join(f'({ix + 1}) {resp}' for ix, resp in enumerate(self.resp_utts[top_k_ixs])))
        else:
            next_actions = self.resp_acts[top_k_ixs].tolist()
            events.append(Event(agent=agent.get_name(),
                            action="request_suggestions",
                            actionLabel=self.get_event_label(),
                            text="Actions for the response: "+ ", ".join(action for action in next_actions),
                            timestamp=int(time())))
            if agent_last_turn:
                next_actions = [self.graph[action] if action in self.graph else action
                                for action in next_actions]
                events.append(Event(agent=agent.get_name(),
                            action="request_suggestions",
                            actionLabel=self.get_event_label(),
                            text="Graph next actions: " + ", ".join(action for action in next_actions),
                            timestamp=int(time())))

            # TODO: remove repeated actions! (make it a set()?)
            next_actions = [action for action in next_actions if action in self.responses]
            instruction = ("If applicable, pick your next response from the following action list in order of importance: " + 
                           "; ".join(f'({ix + 1}) Action: {action}. Response: "{self.responses[action]}"' for ix, action in enumerate(next_actions)))

        return Instruction(text=instruction, events=events)


class InstructionListOrchestrator(BaseOrchestrator):
    def __init__(self,
                 instructions: List[Union[str, Dict[int, str]]],
                 persistent: bool = False):
        super().__init__(persistent=persistent)
        self.instructions = instructions

    def instruct(self, dialog: List[Turn], utterance: str) -> str:
        agent = self.get_target_agent()

        if dialog:
            current_user_len = len([t for t in dialog if t.speaker == agent.get_name()])
        else:
            current_user_len = 0

        if (type(self.instructions) == dict and current_user_len in self.instructions) or \
           (type(self.instructions) == list and current_user_len < len(self.instructions)):
            return self.instructions[current_user_len]
