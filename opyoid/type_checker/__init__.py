import sys

NEW_TYPING = sys.version_info[:3] >= (3, 7, 0)  # PEP 560
if NEW_TYPING:
    from .new_type_checker import TypeChecker
else:
    from .old_type_checker import TypeChecker
