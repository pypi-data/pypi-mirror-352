# State Machines Orchestrator

[![Pypi Version](https://img.shields.io/pypi/v/statemachines-orchestrator.svg)](https://pypi.python.org/statemachines-orchestrator)
[![License](https://img.shields.io/pypi/l/statemachines-orchestrator.svg)](https://github.com/Neikow/statemachines_orchestrator/blob/main/LICENSE)
[![Supported Python Versions](https://img.shields.io/pypi/pyversions/statemachines-orchestrator.svg)](https://pypi.python.org/pypi/statemachines-orchestrator)
[![Actions status](https://github.com/Neikow/statemachines_orchestrator/actions/workflows/test_and_coverage.yml/badge.svg)](https://github.com/Neikow/statemachines_orchestrator/actions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/Neikow/statemachines_orchestrator/main.svg)](https://results.pre-commit.ci/latest/github/Neikow/statemachines_orchestrator/main)

A Python package that provides an elegant orchestration layer for managing multiple [python-statemachine](https://github.com/fgmacedo/python-statemachine) instances, enabling seamless communication and coordination between state machines.

## Overview

The State Machines Orchestrator extends the powerful [python-statemachine](https://github.com/fgmacedo/python-statemachine) library by providing a declarative way to manage multiple state machines that need to interact with each other. Instead of manually wiring up communication between state machines, this orchestrator handles the coordination automatically.

## Key Features

- **Automatic Dependency Injection**: State machines callbacks automatically receive access to the orchestrator
- **Type-Safe**: Full typing support with dataclass-like transformation
- **Clean Architecture**: Separation of concerns between individual state machines and their coordination

## Installation

```bash
pip install statemachines-orchestrator
```

## Quick Start

### 1. Define Your State Machines

First, create your individual state machines using the standard [python-statemachine](https://pypi.org/project/python-statemachine/) approach:

```python
from statemachine import StateMachine, State

class OrderStateMachine(StateMachine):
    # States
    pending = State(initial=True)
    processing = State()
    shipped = State()
    delivered = State(final=True)
    cancelled = State(final=True)

    # Transitions
    process = pending.to(processing)
    ship = processing.to(shipped)
    deliver = shipped.to(delivered)
    cancel = pending.to(cancelled) | processing.to(cancelled)

class PaymentStateMachine(StateMachine):
    # States
    unpaid = State(initial=True)
    authorized = State()
    captured = State(final=True)
    failed = State(final=True)
    refunded = State(final=True)

    # Transitions
    authorize = unpaid.to(authorized)
    capture = authorized.to(captured)
    fail = unpaid.to(failed) | authorized.to(failed)
    refund = captured.to(refunded)
```

### 2. Create an Orchestrator

Use the `Orchestrator` class to coordinate your state machines:

```python
from statemachines_orchestrator import Orchestrator

class ECommerceOrchestrator(Orchestrator):
    order: OrderStateMachine
    payment: PaymentStateMachine
```

### 3. Use the Orchestrator

```python
# Initialize the orchestrator with state machine instances
order_sm = OrderStateMachine()
payment_sm = PaymentStateMachine()

orchestrator = ECommerceOrchestrator(
    order=order_sm,
    payment=payment_sm
)

# Access individual machines
print(orchestrator.order.current_state)  # pending
print(orchestrator.payment.current_state)  # unpaid

# State machines can now communicate through the orchestrator.
# The orchestrator instance is automatically available in callbacks
# and other `python-statemachine` handlers

# For example, after an order is processed, the payment can be authorized:
class OrderStateMachine(StateMachine):
    ...
    def after_process(self, orc: ECommerceOrchestrator):
        orc.payment.authorize() # will move the payment state machine to 'authorized' if it's in 'unpaid'
```

## Advanced Usage

### Custom Orchestrator Name

You can customize the name used to access the orchestrator within state machine callbacks:

```python
class ECommerceOrchestrator(Orchestrator, orchestrator_name="coordinator"):
    order: OrderStateMachine
    payment: PaymentStateMachine

# Now accessible as 'coordinator' in callbacks instead of default 'orc'
```

### State Machine Communication

State machines can interact with each other through the orchestrator context that's automatically injected:

```python
class OrderStateMachine(StateMachine):
    pending = State(initial=True)
    processing = State()
    done = State()

    process = pending.to(processing)
    complete = processing.to(done)

    def before_processing(self, orc: ECommerceOrchestrator):
        # Access other state machines through orchestrator
        if orc.payment.current_state.id == 'authorized':
            orc.payment.capture()
```

## Why Use This Orchestrator?

TODO

## Rationale

TODO

## TODOs

- [ ] Add tests
- [ ] Add documentation
- [ ] Publish to PyPI
- [ ] Setup GitHub Actions
- [ ] Setup Codecov
- [ ] Support Python < 3.11
- [ ] Support multiple versions of `python-statemachine` (not tested)

## Requirements

- Python 3.11+
- [python-statemachine](https://pypi.org/project/python-statemachine/)

## Related Projects

- [python-statemachine](https://github.com/fgmacedo/python-statemachine) - The underlying state machine library this orchestrator extends

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
