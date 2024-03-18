"""
This is the entry point used when run as a module (via python -m sprawl_runner).

Note this should never do anything more than call the main function. This file
is being excluded from automated testing based on the assumption that the core
logic executed is tested via other means; in this case the main function
invoked here has its own set of tests.
"""

from sprawl_runner.main import main

# Call main if this is run as a module.
main()
