from pydantic import BaseModel, Field, NonNegativeInt, PrivateAttr


class CompilationMetadata(BaseModel):
    should_synthesize_separately: bool = Field(default=False)
    occurrences_number: NonNegativeInt = Field(default=1)
    _occupation_number: NonNegativeInt = PrivateAttr(default=0)
    unchecked: list[str] = Field(default_factory=list)
    atomic_qualifiers: list[str] = Field(
        default_factory=list, exclude=True
    )  # TODO remove after deprecation https://classiq.atlassian.net/browse/CLS-2671                                                                                                                                                                                       atomic_qualifiers: list[str] = Field(default_factory=list)

    @property
    def occupation_number(self) -> NonNegativeInt:
        return self._occupation_number

    @occupation_number.setter
    def occupation_number(self, value: NonNegativeInt) -> None:
        self._occupation_number = value
