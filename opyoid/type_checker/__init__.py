import sys

PEP_585 = sys.version_info[:3] >= (3, 9, 0)
PEP_560 = sys.version_info[:3] >= (3, 7, 0)
if PEP_585:
    from .pep585_type_checker import Pep585TypeChecker as TypeChecker
elif PEP_560:
    from .pep560_type_checker import Pep560TypeChecker as TypeChecker
else:
    from .pep484_type_checker import Pep484TypeChecker as TypeChecker
