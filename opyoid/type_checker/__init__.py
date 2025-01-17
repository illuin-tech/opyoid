import sys

PEP_604 = sys.version_info[:3] >= (3, 10, 0)

if PEP_604:  # pragma: nocover
    from .pep604_type_checker import Pep604TypeChecker as TypeChecker
else:  # pragma: nocover
    from .pep585_type_checker import Pep585TypeChecker as TypeChecker  # type: ignore[assignment]
