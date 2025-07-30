# pyright: basic
import sys

if sys.version_info >= (3, 11):

    from typing import Unpack # pyright: ignore[reportAssignmentType, reportAttributeAccessIssue]

else:

    from typing_extensions import Unpack # pyright: ignore[reportMissingModuleSource] # pragma: no cover
