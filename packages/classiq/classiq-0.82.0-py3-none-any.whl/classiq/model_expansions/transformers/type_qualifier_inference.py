import ast
import functools
import itertools
import warnings
from collections.abc import Collection, Iterator, Sequence
from contextlib import contextmanager

from classiq.interface.exceptions import (
    ClassiqDeprecationWarning,
    ClassiqInternalExpansionError,
)
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.generator.functions.type_qualifier import TypeQualifier
from classiq.interface.model.allocate import Allocate
from classiq.interface.model.bind_operation import BindOperation
from classiq.interface.model.control import Control
from classiq.interface.model.invert import Invert
from classiq.interface.model.model_visitor import ModelVisitor
from classiq.interface.model.phase_operation import PhaseOperation
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.power import Power
from classiq.interface.model.quantum_expressions.amplitude_loading_operation import (
    AmplitudeLoadingOperation,
)
from classiq.interface.model.quantum_expressions.arithmetic_operation import (
    ArithmeticOperation,
)
from classiq.interface.model.quantum_expressions.quantum_expression import (
    QuantumExpressionOperation,
)
from classiq.interface.model.quantum_function_call import QuantumFunctionCall
from classiq.interface.model.quantum_statement import QuantumStatement
from classiq.interface.model.within_apply_operation import WithinApply

from classiq.model_expansions.visitors.variable_references import VarRefCollector


def _inconsistent_type_qualifier_error(
    port_name: str, expected: TypeQualifier, actual: TypeQualifier
) -> str:
    return (
        f"The type modifier of variable '{port_name}' does not conform to the function signature: "
        f"expected '{expected.name}', but found '{actual.name}'.\n"
        f"Tip: If the final role of the variable in the function matches '{expected.name}', "
        f"you may use the `unchecked` flag to instruct the compiler to disregard individual operations.\n"
        # TODO add earliest date of enforcement. See https://classiq.atlassian.net/browse/CLS-2709.
    )


def _inconsistent_type_qualifier_in_binding_error(
    expected: TypeQualifier, known_qualifiers: dict[str, TypeQualifier]
) -> str:
    actual = ", ".join(
        f"{name}: {qualifier.name}" for name, qualifier in known_qualifiers.items()
    )
    return (
        f"The variable binding has inconsistent type modifiers: "
        f"Expected modifier: {expected.name}, Actual modifiers: {actual}"
        # TODO add earliest date of enforcement. See https://classiq.atlassian.net/browse/CLS-2709.
    )


class TypeQualifierValidation(ModelVisitor):
    """
    This class assumes that function calls are topologically sorted, so it traverses
    the list of function calls and infers the type qualifiers for each function call
    without going recursively into the function calls.
    The function definition ports are modified inplace.
    """

    def __init__(
        self, *, skip_validation: bool = False, support_unused_ports: bool = True
    ) -> None:
        self._signature_ports: dict[str, PortDeclaration] = dict()
        self._inferred_ports: dict[str, PortDeclaration] = dict()
        self._unchecked: set[str] = set()

        self._initialized_vars: dict[str, TypeQualifier] = dict()
        self._bound_vars: list[set[str]] = []

        self._conjugation_context: bool = False
        self._support_unused_ports = (
            support_unused_ports  # could be turned off for debugging
        )
        self._skip_validation = skip_validation

    @contextmanager
    def validate_ports(
        self, ports: Collection[PortDeclaration], unchecked: Collection[str]
    ) -> Iterator[bool]:
        for port in ports:
            if port.type_qualifier is TypeQualifier.Inferred:
                self._inferred_ports[port.name] = port
            else:
                self._signature_ports[port.name] = port
        self._unchecked.update(unchecked)

        yield len(self._inferred_ports) > 0 or (
            any(
                port.type_qualifier is not TypeQualifier.Quantum
                for port in self._signature_ports.values()
            )
            and not self._skip_validation
        )

        self._set_unused_as_const()
        self._signature_ports.clear()
        self._inferred_ports.clear()
        self._unchecked.clear()

    @contextmanager
    def conjugation_context(self) -> Iterator[None]:
        previous_context = self._conjugation_context
        self._conjugation_context = True
        try:
            yield
        finally:
            self._conjugation_context = previous_context

    def _set_unused_as_const(self) -> None:
        unresolved_ports = [
            port
            for port in self._inferred_ports.values()
            if port.type_qualifier is TypeQualifier.Inferred
        ]
        if not self._support_unused_ports and len(unresolved_ports) > 0:
            raise ClassiqInternalExpansionError(
                f"Unresolved inferred ports detected: {', '.join(port.name for port in unresolved_ports)}. "
                "All ports must have their type qualifiers resolved."
            )
        for port in unresolved_ports:
            port.type_qualifier = TypeQualifier.Const

    def _validate_qualifier(self, candidate: str, qualifier: TypeQualifier) -> None:
        if self._conjugation_context and qualifier is TypeQualifier.QFree:
            qualifier = TypeQualifier.Const

        if candidate in self._inferred_ports:
            self._inferred_ports[candidate].type_qualifier = TypeQualifier.and_(
                self._inferred_ports[candidate].type_qualifier, qualifier
            )
            return

        if self._skip_validation or candidate in self._unchecked:
            return

        if candidate in self._signature_ports:
            self._validate_signature_qualifier(candidate, qualifier)

        elif candidate in self._initialized_vars:
            self._initialized_vars[candidate] = TypeQualifier.and_(
                self._initialized_vars[candidate], qualifier
            )

    def _validate_signature_qualifier(
        self, candidate: str, qualifier: TypeQualifier
    ) -> None:
        signature_qualifier = self._signature_ports[candidate].type_qualifier
        if signature_qualifier is not TypeQualifier.and_(
            signature_qualifier, qualifier
        ):
            warnings.warn(
                _inconsistent_type_qualifier_error(
                    candidate, signature_qualifier, qualifier
                ),
                ClassiqDeprecationWarning,
                stacklevel=1,
            )

    def _add_initialized_qualifier(self, var: str, qualifier: TypeQualifier) -> None:
        if var in self._inferred_ports or var in self._signature_ports:
            return
        if self._conjugation_context and qualifier is TypeQualifier.QFree:
            qualifier = TypeQualifier.Const
        self._initialized_vars[var] = qualifier

    def run(
        self,
        ports: Collection[PortDeclaration],
        body: Sequence[QuantumStatement],
        unchecked: Collection[str],
    ) -> None:
        with self.validate_ports(ports, unchecked) as should_validate:
            if should_validate:
                self.visit(body)
                self._update_bound_vars()

    def _update_bound_vars(self) -> None:
        merged_bound_vars = _merge_overlapping(self._bound_vars)
        for bound_vars in merged_bound_vars:
            reduced_qualifier = self._get_reduced_qualifier(bound_vars)
            for var in bound_vars:
                self._validate_qualifier(var, reduced_qualifier)

    def visit_QuantumFunctionCall(self, call: QuantumFunctionCall) -> None:
        for handle, port in call.handles_with_params:
            self._validate_qualifier(handle.name, port.type_qualifier)
            if port.direction is PortDeclarationDirection.Output:
                self._add_initialized_qualifier(handle.name, port.type_qualifier)

        if self._has_inputs(call):
            bound_vars = {
                handle.name
                for handle, port in call.handles_with_params
                if port.direction is not PortDeclarationDirection.Inout
            }
            self._bound_vars.append(bound_vars)

    @staticmethod
    def _has_inputs(call: QuantumFunctionCall) -> bool:
        return any(
            port.direction is PortDeclarationDirection.Input
            for _, port in call.handles_with_params
        )

    def visit_Allocate(self, alloc: Allocate) -> None:
        self._validate_qualifier(alloc.target.name, TypeQualifier.QFree)
        self._add_initialized_qualifier(alloc.target.name, TypeQualifier.QFree)

    def visit_BindOperation(self, bind_op: BindOperation) -> None:
        var_names = {
            handle.name
            for handle in itertools.chain(bind_op.in_handles, bind_op.out_handles)
        }
        self._bound_vars.append(var_names)
        for handle in bind_op.out_handles:
            self._add_initialized_qualifier(handle.name, TypeQualifier.Inferred)

    def _get_reduced_qualifier(self, bound_vars: set[str]) -> TypeQualifier:
        signature_qualifier = {
            name: self._signature_ports[name].type_qualifier
            for name in bound_vars.intersection(self._signature_ports)
        }
        known_inferred_qualifiers = {
            name: self._inferred_ports[name].type_qualifier
            for name in bound_vars.intersection(self._inferred_ports)
            if self._inferred_ports[name].type_qualifier is not TypeQualifier.Inferred
        }
        known_initialized_qualifiers = {
            name: self._initialized_vars[name]
            for name in bound_vars.intersection(self._initialized_vars)
            if self._initialized_vars[name] is not TypeQualifier.Inferred
        }
        known_qualifiers = (
            signature_qualifier
            | known_inferred_qualifiers
            | known_initialized_qualifiers
        )
        min_qualifier = self._get_min_qualifier(list(known_qualifiers.values()))
        if not all(
            type_qualifier is min_qualifier
            for type_qualifier in signature_qualifier.values()
        ):
            warnings.warn(
                _inconsistent_type_qualifier_in_binding_error(
                    min_qualifier, known_qualifiers
                ),
                ClassiqDeprecationWarning,
                stacklevel=1,
            )

        return min_qualifier

    @staticmethod
    def _get_min_qualifier(qualifiers: list[TypeQualifier]) -> TypeQualifier:
        if len(qualifiers) == 0:
            return TypeQualifier.Const
        elif len(qualifiers) == 1:
            return qualifiers[0]
        else:
            return functools.reduce(TypeQualifier.and_, qualifiers)

    @staticmethod
    def _extract_expr_vars(expr_op: QuantumExpressionOperation) -> list[str]:
        vrc = VarRefCollector(
            ignore_duplicated_handles=True, ignore_sympy_symbols=True, unevaluated=True
        )
        vrc.visit(ast.parse(expr_op.expression.expr))
        return [handle.name for handle in vrc.var_handles]

    def visit_ArithmeticOperation(self, arith: ArithmeticOperation) -> None:
        result_var = arith.result_var.name
        self._validate_qualifier(result_var, TypeQualifier.QFree)
        for expr_var in self._extract_expr_vars(arith):
            self._validate_qualifier(expr_var, TypeQualifier.Const)
        if not arith.is_inplace:
            self._add_initialized_qualifier(result_var, TypeQualifier.QFree)

    def visit_AmplitudeLoadingOperation(
        self, amp_load: AmplitudeLoadingOperation
    ) -> None:
        result_var = amp_load.result_var.name
        self._validate_qualifier(result_var, TypeQualifier.Quantum)
        for expr_var in self._extract_expr_vars(amp_load):
            self._validate_qualifier(expr_var, TypeQualifier.Const)

    def visit_PhaseOperation(self, phase_op: PhaseOperation) -> None:
        for expr_var in self._extract_expr_vars(phase_op):
            self._validate_qualifier(expr_var, TypeQualifier.Const)

    def visit_Control(self, control: Control) -> None:
        for control_var in self._extract_expr_vars(control):
            self._validate_qualifier(control_var, TypeQualifier.Const)
        self.visit(control.body)
        if control.else_block is not None:
            self.visit(control.else_block)

    def visit_Invert(self, invert: Invert) -> None:
        self.visit(invert.body)

    def visit_Power(self, power: Power) -> None:
        self.visit(power.body)

    def visit_WithinApply(self, within_apply: WithinApply) -> None:
        with self.conjugation_context():
            self.visit(within_apply.compute)
        self.visit(within_apply.action)


def _merge_overlapping(bound_vars: Sequence[Collection[str]]) -> list[set[str]]:
    """
    Merges overlapping sets of bound variables.
    Two sets overlap if they share at least one variable.
    """
    all_bound_vars = bound_vars
    merged_bound_vars: list[set[str]] = []
    loop_guard: int = 10
    idx: int = 0

    for _ in range(loop_guard):
        idx += 1

        merged_bound_vars = []
        modified: bool = False
        for current_bound_vars in all_bound_vars:
            for existing in merged_bound_vars:
                if existing.intersection(current_bound_vars):
                    existing.update(current_bound_vars)
                    modified = True
                    break
            else:
                merged_bound_vars.append(set(current_bound_vars))

        if not modified:
            break
        all_bound_vars = merged_bound_vars

    if idx == loop_guard - 1:
        raise ClassiqInternalExpansionError

    return merged_bound_vars
