import warnings
from typing import Callable, Literal, Optional, Union, overload

from classiq.interface.exceptions import ClassiqDeprecationWarning, ClassiqInternalError

from classiq.qmod.global_declarative_switch import get_global_declarative_switch
from classiq.qmod.quantum_callable import QCallable
from classiq.qmod.quantum_function import (
    BaseQFunc,
    ExternalQFunc,
    GenerativeQFunc,
    QFunc,
)


@overload
def qfunc(func: Callable) -> GenerativeQFunc: ...


@overload
def qfunc(
    *,
    external: Literal[True],
    synthesize_separately: Literal[False] = False,
    unchecked: Optional[list[str]] = None,
) -> Callable[[Callable], ExternalQFunc]: ...


@overload
def qfunc(
    *,
    generative: Literal[False],
    synthesize_separately: bool = False,
    unchecked: Optional[list[str]] = None,
) -> Callable[[Callable], QFunc]: ...


@overload
def qfunc(
    *, synthesize_separately: bool, unchecked: Optional[list[str]] = None
) -> Callable[[Callable], GenerativeQFunc]: ...


@overload
def qfunc(
    *,
    synthesize_separately: bool = False,
    unchecked: Optional[list[str]] = None,
) -> Callable[[Callable], GenerativeQFunc]: ...


def qfunc(
    func: Optional[Callable] = None,
    *,
    external: bool = False,
    generative: Optional[bool] = None,
    synthesize_separately: bool = False,
    unchecked: Optional[list[str]] = None,
) -> Union[Callable[[Callable], QCallable], QCallable]:
    if generative is True:
        warnings.warn(
            "The use of `generative=True` is no longer required. Note that the "
            "treatment of parameters of Qmod types will change from Python value to "
            "symbolic in a near release. Change Qmod types to the corresponding Python "
            "built-in types in order to use the parameters in Python expression "
            "contexts.\n"
            "Recommended changes:\n"
            "@qfunc(generative=True) -> @qfunc\n"
            "CInt->int\n"
            "CReal->float\n"
            "CArray->list\n\n"
            "For more information see https://docs.classiq.io/latest/qmod-reference/language-reference/generative-descriptions/",
            ClassiqDeprecationWarning,
            stacklevel=2,
        )
    elif generative is None:
        generative = True
    if get_global_declarative_switch():
        generative = False

    def wrapper(func: Callable) -> QCallable:
        qfunc: BaseQFunc

        if external:
            _validate_directives(synthesize_separately, unchecked)
            return ExternalQFunc(func)

        if generative:
            qfunc = GenerativeQFunc(func)
        else:
            qfunc = QFunc(func)
        if synthesize_separately:
            qfunc.update_compilation_metadata(should_synthesize_separately=True)
        if unchecked is not None and len(unchecked) > 0:
            qfunc.update_compilation_metadata(unchecked=unchecked)
        return qfunc

    if func is not None:
        return wrapper(func)
    return wrapper


def _validate_directives(
    synthesize_separately: bool, unchecked: Optional[list[str]] = None
) -> None:
    error_msg = ""
    if synthesize_separately:
        error_msg += "External functions can't be marked as synthesized separately. \n"
    if unchecked is not None and len(unchecked) > 0:
        error_msg += "External functions can't have unchecked qualifiers."
    if error_msg:
        raise ClassiqInternalError(error_msg)
