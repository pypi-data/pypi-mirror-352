# -*- coding: utf-8 -*-
class AlternativeScheme:

    def __init__(self, name: str = None, instruction: str = None) -> None:
        self._name = name
        self._instruction = instruction

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @property
    def instruction(self):
        return self._instruction

    @instruction.setter
    def instruction(self, value: str):
        self._instruction = value

    def __str__(self) -> str:
        return f'''
        AlternativeScheme
            name="{self._name}", instruction="{self._instruction}"
        '''
