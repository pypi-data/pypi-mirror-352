"""Module-level functionality for testing installation.

Example:
    Test that the package was installed properly:

    ::

        python -m pcubit.tests

"""

# from .test_zero import Zero
from .test_one import One
# from .test_many import Many
# from .test_boundary import Boundary
# from .test_interface import Interface
from .test_examples import Examples
# from .test_style import Style

# Zero().main()
One().main()
# Many().main()
# Boundary().main()
# Interface().main()
Examples().main()
# Style().main()
