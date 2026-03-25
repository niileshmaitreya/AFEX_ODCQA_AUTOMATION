from pathlib import Path
from pytest_bdd import scenarios

# Force import of steps so pytest-bdd registers them at collection time
from tests.bdd.steps import afex_login_steps  # noqa: F401

# Resolve feature path relative to THIS file (not the cwd)
FEATURE = Path(__file__).parents[2] / "features" / "afex_login.feature"

# Collect scenarios
scenarios(str(FEATURE))