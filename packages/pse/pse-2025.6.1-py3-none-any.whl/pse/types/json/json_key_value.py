from __future__ import annotations

from typing import Any

from pse_core import StateId

from pse.types.base.chain import ChainStateMachine
from pse.types.base.phrase import PhraseStateMachine
from pse.types.json import _json_schema_to_state_machine
from pse.types.key_value import KeyValueStateMachine, KeyValueStepper
from pse.types.string import StringStateMachine
from pse.types.whitespace import WhitespaceStateMachine


class KeyValueSchemaStateMachine(KeyValueStateMachine):
    """
    Args:
        prop_name (str): The name of the property.
        prop_schema (Dict[str, Any]): The schema of the property.
        context (Dict[str, Any]): The parsing context.
    """

    def __init__(
        self,
        prop_name: str | None,
        prop_schema: dict[str, Any],
        context: dict[str, Any],
    ):
        self.prop_name = prop_name
        self.prop_schema = prop_schema
        self.prop_context = {
            "defs": context.get("defs", {}),
            "path": f"{context.get('path', '')}/{prop_name}",
        }
        if self.prop_name:
            key_value_sm = ChainStateMachine(
                [
                    PhraseStateMachine('"'),
                    PhraseStateMachine(self.prop_name),
                    PhraseStateMachine('"'),
                ]
            )
        else:
            key_value_sm = StringStateMachine()

        is_optional = self.prop_schema.get("nullable", False) or "default" in self.prop_schema
        super().__init__(
            [
                key_value_sm,
                WhitespaceStateMachine(),
                PhraseStateMachine(":"),
                WhitespaceStateMachine(),
                _json_schema_to_state_machine(self.prop_schema, self.prop_context),
            ],
            is_optional=is_optional,
        )

    def get_new_stepper(self, state: StateId | None = None) -> KeyValueSchemaStepper:
        return KeyValueSchemaStepper(self, state)


class KeyValueSchemaStepper(KeyValueStepper):
    def __init__(
        self,
        state_machine: KeyValueSchemaStateMachine,
        current_state: StateId | None = None,
    ):
        super().__init__(state_machine, current_state)
        self.state_machine: KeyValueSchemaStateMachine = state_machine
