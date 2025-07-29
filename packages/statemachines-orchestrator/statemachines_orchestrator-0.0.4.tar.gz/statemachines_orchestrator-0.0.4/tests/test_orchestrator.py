from tests.utils import Dummy, MachineA, MachineB, OrchestratorAB


def test_machine_initialization_and_states() -> None:
    dummy = Dummy()
    orch = OrchestratorAB(
        a=MachineA(model=dummy, state_field="a_state"),
        b=MachineB(model=dummy, state_field="b_state"),
    )
    assert orch.a.current_state_value == "S1"
    assert orch.b.current_state_value == "X1"
    orch.a.s1_to_s2()
    assert orch.a.current_state_value == "S2"
    orch.a.s2_to_s3()
    assert orch.a.current_state_value == "S3"
    orch.b.x1_to_x2()
    assert orch.b.current_state_value == "X2"


def test_machine_classes_property() -> None:
    dummy = Dummy()
    orch = OrchestratorAB(
        a=MachineA(model=dummy, state_field="a_state"),
        b=MachineB(model=dummy, state_field="b_state"),
    )
    assert set(orch.machine_classes.keys()) == {"a", "b"}
    assert orch.machine_classes["a"] is MachineA
    assert orch.machine_classes["b"] is MachineB


def test_orchestrator_name_property() -> None:
    dummy = Dummy()
    orch = OrchestratorAB(
        a=MachineA(model=dummy, state_field="a_state"),
        b=MachineB(model=dummy, state_field="b_state"),
    )
    assert orch.orchestrator_name == "orc"


def test_machines_property() -> None:
    dummy = Dummy()
    orch = OrchestratorAB(
        a=MachineA(model=dummy, state_field="a_state"),
        b=MachineB(model=dummy, state_field="b_state"),
    )
    assert set(orch.machines.keys()) == {"a", "b"}
    assert isinstance(orch.machines["a"], MachineA)
    assert isinstance(orch.machines["b"], MachineB)


def test_patch_send_and_put_nonblocking() -> None:
    dummy = Dummy()
    orch = OrchestratorAB(
        a=MachineA(model=dummy, state_field="a_state"),
        b=MachineB(model=dummy, state_field="b_state"),
    )
    assert callable(orch.a.send)
    assert callable(orch.b.send)
    assert hasattr(orch.a, "_put_nonblocking")
    assert hasattr(orch.b, "_put_nonblocking")


def test_perform_initial_checks() -> None:
    dummy = Dummy()
    orch = OrchestratorAB(
        a=MachineA(model=dummy, state_field="a_state"),
        b=MachineB(model=dummy, state_field="b_state"),
    )
    orch._perform_initial_checks()
