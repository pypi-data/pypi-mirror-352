"""Orchestrator for managing multiple state machines in a convenient way.

The `Orchestrator` class allows you to define and manage multiple state machines
and access sibling machines from within a machine's callback methods.
"""

import dataclasses
import typing
from functools import partial, wraps
from typing import Any

from statemachine import StateMachine
from statemachine.event_data import TriggerData

from statemachines_orchestrator.exceptions import (
    AnnotationIsNotAStateMachineError,
    NoMachinesOnOrchestratorError,
    StateFieldIsNotUniqueError,
)
from statemachines_orchestrator.utils import (
    _get_machines_annotations,
    _UnknownType,
)

DUNDER_INIT = "__init__"
MACHINE_CLASSES = "_machine_classes"
ORCHESTRATOR_NAME = "_orchestrator_name"
DEFAULT_ORCHESTRATOR_NAME = "orc"
DEFAULT_MACHINE_STATE_FIELD = "state"


class _OrchestratorType(type):
    def __new__(
        cls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        *,
        orchestrator_name: str = DEFAULT_ORCHESTRATOR_NAME,
    ) -> type:
        if not bases:
            return super().__new__(cls, name, bases, namespace)

        klass: type = dataclasses.dataclass(
            super().__new__(cls, name, bases, namespace),  # type: ignore[arg-type]
        )

        setattr(klass, ORCHESTRATOR_NAME, orchestrator_name)

        if not klass.__dataclass_fields__:  # type: ignore[attr-defined]
            msg = f"No machines found on {klass.__name__} class"
            raise NoMachinesOnOrchestratorError(msg)

        cls_annotations = namespace.get("__annotations__", {})
        _machine_classes = _get_machines_annotations(cls, cls_annotations)

        for machine_name, machine_class in _machine_classes.items():
            if isinstance(machine_class, _UnknownType):
                # I don't know if this should raise or log a warning.
                continue
            if not issubclass(machine_class, StateMachine):
                msg = f"Annotation '{machine_name}' is not a subclass of StateMachine"
                raise AnnotationIsNotAStateMachineError(
                    msg,
                )

        setattr(klass, MACHINE_CLASSES, _machine_classes)

        return klass


@typing.dataclass_transform()
class Orchestrator(metaclass=_OrchestratorType):
    """The state machines orchestrator class."""

    def __post_init__(self) -> None:
        """Post-initialization method to set up the orchestrator.

        This method should perform initial checks and patch the state machines.
        """
        self._perform_initial_checks()
        self._patch_machines()

    @property
    def machine_classes(self) -> dict[str, type[StateMachine]]:
        """Return the dictionary of state machine classes."""
        return getattr(self.__class__, MACHINE_CLASSES)

    @property
    def orchestrator_name(self) -> str:
        """Return the orchestrator name.

        This name is used to inject the orchestrator instance into the trigger data.
        """
        return getattr(self.__class__, ORCHESTRATOR_NAME)

    @property
    def machines(self) -> dict[str, StateMachine]:
        """Return the dictionary of state machine instances."""
        return {machine_name: getattr(self, machine_name) for machine_name in self.machine_classes}

    def _patch_send(self) -> None:
        """Patch the `send` method of the state machines.

        Inject the orchestrator instance into the trigger data, making it accessible from the callbacks.
        """
        for machine_instance in self.machines.values():
            method = machine_instance.send
            machine_instance.send = partial(  # type: ignore[method-assign]
                method,
                **{self.orchestrator_name: self},  # type: ignore[arg-type]
            )

    def _patch_put_nonblocking(self) -> None:
        """Patch the `_put_nonblocking` method of the state machines.

        Add the orchestrator instance to the trigger data, making it accessible from the callbacks.
        """
        for machine_instance in self.machines.values():
            method = machine_instance._put_nonblocking

            @wraps(method)
            def patched_method(trigger_data: TriggerData) -> None:
                trigger_data.kwargs[self.orchestrator_name] = self
                # Events and transitions rely on a proxy of the state machine,
                # therefore, the appending to `machine_instance._engine` will
                # not add the event to the right state machine engine.
                # We operate on the engine directly as we don't want to
                # create an infinite loop.
                trigger_data.machine._engine.put(trigger_data)

            machine_instance._put_nonblocking = patched_method  # type: ignore[method-assign]

    def _patch_machines(self) -> None:
        """Perform the patches for the state machines."""
        self._patch_send()
        self._patch_put_nonblocking()

    def _check_all_machines_state_fields_are_unique(self) -> None:
        state_fields = set()
        for machine_name, machine_instance in self.machines.items():
            state_field = machine_instance.state_field
            if state_field in state_fields:
                if state_field == DEFAULT_MACHINE_STATE_FIELD:
                    msg = (
                        f"state_field '{state_field}' is not unique for '{machine_name}'.\n"
                        f"Hint: you should override the default by providing a `state_field` argument "
                        f"on '{machine_name}' initialization."
                    )
                    raise StateFieldIsNotUniqueError(
                        msg,
                    )
                msg = f"state_field '{state_field}' is not unique for '{machine_name}'"
                raise StateFieldIsNotUniqueError(
                    msg,
                )
            state_fields.add(state_field)

    def _perform_initial_checks(self) -> None:
        """Perform initial checks on the state machines.

        Ensure that no unexpected behavior occurs from machine definition.
        """
        self._check_all_machines_state_fields_are_unique()
