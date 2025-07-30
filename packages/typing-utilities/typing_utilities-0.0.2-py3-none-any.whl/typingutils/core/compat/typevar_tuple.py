# pyright: basic
import sys
from typing import Any

if sys.version_info >= (3, 11):

    from typing import TypeVarTuple # pyright: ignore[reportAssignmentType, reportAttributeAccessIssue]

else:

    from typing_extensions import TypeVarTuple # pyright: ignore[reportMissingModuleSource] # pragma: no cover

    # class TypeVarTuple313(): # pragma: no cover
    #     def __init__(self, name: str, *, default: Any | None = None):
    #         self.__name__ = name
    #         self.__default__ = default

    #     def has_default(self) -> bool:
    #         return self.__default__ is not None

    #     def __repr__(self) -> str:
    #         return self.__name__

    # class TypeVarTuple311(): # pragma: no cover
    #     def __init__(self, name: str):
    #         self.__name__ = name

    #     def __repr__(self) -> str:
    #         return self.__name__


    # TypeVarTuple = TypeVarTuple313
