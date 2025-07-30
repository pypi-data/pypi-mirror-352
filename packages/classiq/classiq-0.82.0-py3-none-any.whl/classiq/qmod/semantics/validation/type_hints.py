from typing import Any

from typing_extensions import _AnnotatedAlias

from classiq.interface.exceptions import ClassiqValueError
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.generator.functions.type_qualifier import TypeQualifier


def validate_annotation(type_hint: Any) -> None:
    if not isinstance(type_hint, _AnnotatedAlias):
        return
    directions: list[PortDeclarationDirection] = [
        direction
        for direction in type_hint.__metadata__
        if isinstance(direction, PortDeclarationDirection)
    ]
    qualifiers: list[TypeQualifier] = [
        qualifier
        for qualifier in type_hint.__metadata__
        if isinstance(qualifier, TypeQualifier)
    ]
    if len(directions) <= 1 and len(qualifiers) <= 1:
        return
    error_message = ""
    if len(directions) > 1:
        error_message += (
            f"Multiple directions are not allowed in a single type hint: "
            f"[{', '.join(direction.name for direction in reversed(directions))}]\n"
        )
    if len(qualifiers) > 1:
        error_message += (
            f"Multiple qualifiers are not allowed in a single type hint: "
            f"[{', '.join(qualifier.name for qualifier in reversed(qualifiers))}]\n"
        )
    raise ClassiqValueError(error_message)
