from classiq.interface.enum_utils import StrEnum
from classiq.interface.exceptions import ClassiqInternalExpansionError


class TypeQualifier(StrEnum):
    Const = "const"
    QFree = "qfree"
    Quantum = "quantum"
    Inferred = "inferred"

    @staticmethod
    def and_(first: "TypeQualifier", second: "TypeQualifier") -> "TypeQualifier":
        if second is TypeQualifier.Inferred:
            raise ClassiqInternalExpansionError
        if first is TypeQualifier.Quantum or second is TypeQualifier.Quantum:
            return TypeQualifier.Quantum
        elif first is TypeQualifier.QFree or second is TypeQualifier.QFree:
            return TypeQualifier.QFree
        else:
            if first is not TypeQualifier.Const and second is not TypeQualifier.Const:
                raise ClassiqInternalExpansionError("Unexpected type qualifiers")
            return TypeQualifier.Const
