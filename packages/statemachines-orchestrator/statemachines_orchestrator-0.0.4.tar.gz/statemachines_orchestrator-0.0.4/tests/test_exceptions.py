import pytest

from statemachines_orchestrator.exceptions import (
    AnnotationIsNotAStateMachineError,
    NoMachinesOnOrchestratorError,
    StateFieldIsNotUniqueError,
)
from statemachines_orchestrator.orchestrator import Orchestrator
from tests.utils import Dummy, MachineA, MachineB, OrchestratorAB


def test_unique_state_field_enforcement() -> None:
    dummy = Dummy()
    with pytest.raises(StateFieldIsNotUniqueError):
        OrchestratorAB(
            a=MachineA(model=dummy),
            b=MachineB(model=dummy),
        )
    with pytest.raises(StateFieldIsNotUniqueError):
        OrchestratorAB(
            a=MachineA(model=dummy, state_field="same"),
            b=MachineB(model=dummy, state_field="same"),
        )


def test_no_machines_on_orchestrator() -> None:
    with pytest.raises(NoMachinesOnOrchestratorError):

        class EmptyOrchestrator(Orchestrator):
            pass


def test_annotation_is_not_a_statemachine() -> None:
    with pytest.raises(AnnotationIsNotAStateMachineError):

        class BadOrchestrator(Orchestrator):
            foo: str
