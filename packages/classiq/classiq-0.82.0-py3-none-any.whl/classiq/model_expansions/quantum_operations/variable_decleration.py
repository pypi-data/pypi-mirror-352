from classiq.interface.exceptions import ClassiqExpansionError
from classiq.interface.model.handle_binding import HandleBinding
from classiq.interface.model.variable_declaration_statement import (
    VariableDeclarationStatement,
)

from classiq.model_expansions.evaluators.parameter_types import (
    evaluate_type_in_quantum_symbol,
)
from classiq.model_expansions.quantum_operations.emitter import Emitter
from classiq.model_expansions.scope import Evaluated, QuantumSymbol


class VariableDeclarationStatementEmitter(Emitter[VariableDeclarationStatement]):
    def emit(self, variable_declaration: VariableDeclarationStatement, /) -> bool:
        var_decl = variable_declaration.model_copy(
            update=dict(back_ref=variable_declaration.uuid)
        )
        var_decl.quantum_type = variable_declaration.quantum_type.model_copy()
        if variable_declaration.name in self._current_scope:
            raise ClassiqExpansionError(
                f"Variable {variable_declaration.name!r} is already defined"
            )
        self._current_scope[variable_declaration.name] = Evaluated(
            value=QuantumSymbol(
                handle=HandleBinding(name=var_decl.name),
                quantum_type=evaluate_type_in_quantum_symbol(
                    var_decl.quantum_type,
                    self._current_scope,
                    var_decl.name,
                ),
            ),
            defining_function=self._builder.current_function,
        )
        self._builder.current_block.captured_vars.init_var(
            var_decl.name, self._builder.current_function
        )
        self.emit_statement(var_decl)
        return True
