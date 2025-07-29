from __future__ import annotations

from typing import TYPE_CHECKING

from statemachines_orchestrator.orchestrator import Orchestrator

if TYPE_CHECKING:
    from tests.utils import MachineA


def test_orchestrator_with_state_machine_type_annotation_should_compile() -> None:
    class _StateMachineOrchestrator(Orchestrator):
        machine_a: MachineA
