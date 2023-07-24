import sys

PEP_604 = sys.version_info[:3] >= (3, 10, 0)
PEP_585 = sys.version_info[:3] >= (3, 9, 0)

if PEP_604:
    from .pep604_type_checker import Pep604TypeChecker as TypeChecker
elif PEP_585:
    from .pep585_type_checker import Pep585TypeChecker as TypeChecker
else:
    from .pep560_type_checker import Pep560TypeChecker as TypeChecker
