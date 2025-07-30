from dataclasses import dataclass, fields, is_dataclass

from classiq.interface.generator.types.struct_declaration import StructDeclaration

from classiq.qmod.builtins.enums import LadderOperator, Pauli
from classiq.qmod.cparam import CArray, CBool, CInt, CReal
from classiq.qmod.python_classical_type import PythonClassicalType


@dataclass
class PauliTerm:
    """
    A term in a Hamiltonian, represented as a product of single-qubit Pauli matrices.

    Attributes:
        pauli (CArray[Pauli]): The list of the chosen Pauli operators in the term, corresponds to a product of them.
        coefficient (CReal): The coefficient of the term (floating number).
    """

    pauli: CArray[Pauli]
    coefficient: CReal


@dataclass
class IndexedPauli:
    """
    A single-qubit Pauli matrix on a specific qubit given by its index.

    Attributes:
        pauli (Pauli): The Pauli operator.
        index (CInt): The index of the qubit being operated on.
    """

    pauli: Pauli
    index: CInt


@dataclass
class SparsePauliTerm:
    """
    A term in the Hamiltonian, represented as a sparse product of single-qubit Pauli
    matrices.

       Attributes:
           paulis (CArray[IndexedPauli]): The list of chosen sparse Pauli operators in the term corresponds to a product of them. (See IndexedPauli)
           coefficient (CReal): The coefficient of the term (floating number).
    """

    paulis: CArray[IndexedPauli]
    coefficient: CReal


@dataclass
class SparsePauliOp:
    """
    Represents a collection of sparse Pauli operators.

    Attributes:
        paulis (CArray[SparsePauliTerm]): The list of chosen sparse Pauli operators in the term, corresponds to a product of them. (See: SparsePauliTerm)
        num_qubits (CInt): The number of qubits in the Hamiltonian.
    """

    paulis: CArray[SparsePauliTerm]
    num_qubits: CInt


@dataclass
class Position:
    x: CReal
    y: CReal
    z: CReal


@dataclass
class ChemistryAtom:
    element: CInt
    position: Position


@dataclass
class Molecule:
    atoms: CArray[ChemistryAtom]
    spin: CInt
    charge: CInt


@dataclass
class MoleculeProblem:
    mapping: CInt
    z2_symmetries: CBool
    molecule: Molecule
    freeze_core: CBool
    remove_orbitals: CArray[CInt]


@dataclass
class LadderOp:
    op: LadderOperator
    index: CInt


@dataclass
class LadderTerm:
    coefficient: CReal
    ops: CArray[LadderOp]


@dataclass
class FockHamiltonianProblem:
    mapping: CInt
    z2_symmetries: CBool
    terms: CArray[LadderTerm]
    num_particles: CArray[CInt]


@dataclass
class CombinatorialOptimizationSolution:
    probability: CReal
    cost: CReal
    solution: CArray[CInt]
    count: CInt


@dataclass
class GaussianModel:
    num_qubits: CInt
    normal_max_value: CReal
    default_probabilities: CArray[CReal]
    rhos: CArray[CReal]
    loss: CArray[CInt]
    min_loss: CInt


@dataclass
class LogNormalModel:
    num_qubits: CInt
    mu: CReal
    sigma: CReal


@dataclass
class FinanceFunction:
    f: CInt
    threshold: CReal
    larger: CBool
    polynomial_degree: CInt
    use_chebyshev_polynomial_approximation: CBool
    tail_probability: CReal


@dataclass
class QsvmResult:
    test_score: CReal
    predicted_labels: CArray[CReal]


@dataclass
class QSVMFeatureMapPauli:
    feature_dimension: CInt
    reps: CInt
    entanglement: CInt
    alpha: CReal
    paulis: CArray[CArray[Pauli]]


BUILTIN_STRUCT_DECLARATIONS = {
    struct_decl.__name__: StructDeclaration(
        name=struct_decl.__name__,
        variables={
            field.name: PythonClassicalType().convert(field.type)
            for field in fields(struct_decl)
        },
    )
    for struct_decl in vars().values()
    if is_dataclass(struct_decl)
}


__all__ = [
    "ChemistryAtom",
    "CombinatorialOptimizationSolution",
    "FinanceFunction",
    "FockHamiltonianProblem",
    "GaussianModel",
    "IndexedPauli",
    "LadderOp",
    "LadderTerm",
    "LogNormalModel",
    "Molecule",
    "MoleculeProblem",
    "PauliTerm",
    "Position",
    "QSVMFeatureMapPauli",
    "QsvmResult",
    "SparsePauliOp",
    "SparsePauliTerm",
]
