from typing import Literal, Optional

from classiq.interface.helpers.custom_pydantic_types import PydanticFloatTuple
from classiq.interface.model.handle_binding import ConcreteHandleBinding
from classiq.interface.model.quantum_statement import QuantumOperation


class SetBoundsStatement(QuantumOperation):
    kind: Literal["SetBoundsStatement"]

    target: ConcreteHandleBinding
    bounds: Optional[PydanticFloatTuple]
