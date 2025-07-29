"""Exceptions for the State Machines Orchestrator."""


class StateFieldIsNotUniqueError(Exception):
    """The state field is not unique across all machines."""


class AnnotationIsNotAStateMachineError(Exception):
    """The annotation is not a subclass of StateMachine."""


class UnexpectedAnnotationTypeError(Exception):
    """The annotation type is not a subclass of StateMachine nor a str."""


class NoMachinesOnOrchestratorError(Exception):
    """No machines found on the orchestrator class."""
