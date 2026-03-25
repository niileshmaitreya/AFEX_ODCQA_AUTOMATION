
import os
import base64
import pytest
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

pytest_plugins = [
    "tests.bdd.steps.afex_login_steps",
]

# =====================================================
# Environment & paths
# =====================================================

load_dotenv()

PROJECT_ROOT = Path(__file__).parent
REPORTS_DIR = PROJECT_ROOT / "reports" / "html"


# =====================================================
# Command-line options
# =====================================================

def pytest_addoption(parser):
    parser.addoption("--google-email", action="store", default=None)
    parser.addoption("--google-password", action="store", default=None)
    parser.addoption("--allow-password-submit", action="store_true", default=False)


# =====================================================
# Common fixtures
# =====================================================

@pytest.fixture(scope="session")
def creds():
    return {
        "email": os.getenv("USERNAME"),
        "password": os.getenv("PASSWORD"),
        "allow_submit": os.getenv("ALLOW_PASSWORD_SUBMIT", "false").lower()
        in ("1", "true", "yes"),
    }


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "locale": "en-US",
        "user_agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/121.0.0.0 Safari/537.36"
        ),
    }


# =====================================================
# pytest-html report (MASTER ONLY)
# =====================================================

def pytest_configure(config):
    """
    Generate exactly ONE pytest-html report per run.
    Only the master node is allowed to do this.
    """
    if hasattr(config, "workerinput"):
        return  # skip workers

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_path = REPORTS_DIR / f"report_{timestamp}.html"

    config.option.htmlpath = str(report_path)
    config.option.self_contained_html = True


# =====================================================
# Screenshot capture + attach (xdist-safe)
# =====================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    This hook runs inside the same process that executed the test.
    With pytest-xdist, this means the WORKER that owns the Playwright
    page. This is the ONLY reliable place to take and attach screenshots.
    """
    outcome = yield
    report = outcome.get_result()

    # Only act on test execution failure
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")

        if page:
            pytest_html = item.config.pluginmanager.getplugin("html")

            screenshot_bytes = page.screenshot(full_page=True)
            encoded = base64.b64encode(screenshot_bytes).decode("utf-8")

            report.extra = getattr(report, "extra", [])
            report.extra.append(pytest_html.extras.png(encoded))
# # import os
# # import time
# # import pytest
# # from dotenv import load_dotenv
# # from datetime import datetime
# # from pathlib import Path
# # import pytest_html
# # import base64

# # # Ensure hooks are loaded
# # pytest_plugins = [
# #     "hooks.bdd_hooks",                 # your hooks layer
# #     "tests.bdd.steps.afex_login_steps" # force step registration as plugin
# # ]

# # # Load .env if present
# # load_dotenv()

# # # @pytest.hookimpl(hookwrapper=True, tryfirst=True)
# # # def pytest_runtest_makereport(item, call):
# # #     outcome = yield
# # #     rep = outcome.get_result()
# # #     if rep.when == "call" and rep.failed:
# # #         page = item.funcargs.get("page")
# # #         if page:
# # #             ts = time.strftime("%Y%m%d_%H%M%S")
# # #             os.makedirs("artifacts", exist_ok=True)
# # #             page.screenshot(path=f"artifacts/{item.name}_{ts}.png", full_page=True)

# # def pytest_addoption(parser):
# #     parser.addoption("--google-email", action="store", default=None, help="AFEX email to use")
# #     parser.addoption("--google-password", action="store", default=None, help="AFEX password to use")
# #     parser.addoption("--allow-password-submit", action="store_true", default=False, help="Actually submit the password (disabled by default)")

# # @pytest.fixture(scope="session")
# # def creds(pytestconfig):
# #     email =os.getenv("USERNAME")
# #     password = os.getenv("PASSWORD")
# #     allow_submit = (os.getenv("ALLOW_PASSWORD_SUBMIT", "false").lower() in ("1", "true", "yes"))
# #     return {"email": email, "password": password, "allow_submit": allow_submit}

# # @pytest.fixture(scope="session")
# # def browser_context_args(browser_context_args):
# #     args = dict(browser_context_args)
# #     args.update({
# #         "ignore_https_errors": True,
# #         "locale": "en-US",
# #         "user_agent": (
# #             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
# #             "AppleWebKit/537.36 (KHTML, like Gecko) "
# #             "Chrome/121.0.0.0 Safari/537.36"
# #         ),
# #     })
# #     return args


# ===== MSSQL support =====
from db.mssql_client import MSSQLClient



@pytest.fixture(scope="session")
def mssql_client():
    host = os.getenv("MSSQL_HOST")
    user = os.getenv("MSSQL_USER")
    database = os.getenv("MSSQL_DATABASE")

    if not (host and user and database):
        return None

    return MSSQLClient.from_env()



# # PROJECT_ROOT = Path(__file__).parent
# # REPORTS_DIR = PROJECT_ROOT / "reports" / "html"


# # # def pytest_configure(config):
# # #     """
# # #     Automatically generate a timestamped pytest-html report
# # #     for every test run (CLI or VS Code UI).
# # #     """
# # #     REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# # #     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# # #     report_path = REPORTS_DIR / f"report_{timestamp}.html"

# # #     # Inject pytest-html options dynamically
# # #     config.option.htmlpath = str(report_path)
# # #     config.option.self_contained_html = True

# # from datetime import datetime
# # from pathlib import Path



# # PROJECT_ROOT = Path(__file__).parent
# # REPORTS_DIR = PROJECT_ROOT / "reports" / "html"


# # def pytest_configure(config):
# #     """
# #     Ensure pytest-html report is created ONLY by the master node,
# #     even when pytest-xdist (-n auto) is enabled.
# #     """

# #     # ✅ Skip worker processes completely
# #     if hasattr(config, "workerinput"):
# #         return

# #     REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# #     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
# #     report_path = REPORTS_DIR / f"report_{timestamp}.html"

# #     config.option.htmlpath = str(report_path)
# #     config.option.self_contained_html = True


# # @pytest.fixture(autouse=True)
# # def capture_screenshot_on_failure(request):
# #     """
# #     Capture screenshot immediately at failure time (WORKER process).
# #     """
# #     yield

# #     # This attribute is added in Step B below
# #     rep_call = getattr(request.node, "rep_call", None)
# #     page = request.node.funcargs.get("page", None)

# #     if rep_call and rep_call.failed and page:
# #         # Screenshot is captured while browser is still alive
# #         request.node._screenshot_bytes = page.screenshot(full_page=True)


# # @pytest.hookimpl(hookwrapper=True)
# # def pytest_runtest_makereport(item, call):
# #     outcome = yield
# #     rep = outcome.get_result()

# #     if rep.when == "call":
# #         item.rep_call = rep

# # @pytest.hookimpl(hookwrapper=True)
# # def pytest_html_results_table_row(report, cells):

# #     # ✅ ONLY master may modify HTML
# #     if hasattr(report.config, "workerinput"):
# #         return

# #     node = getattr(report, "item", None)
# #     if node and hasattr(node, "_screenshot_bytes"):
# #         pytest_html = report.config.pluginmanager.getplugin("html")
# #         encoded = base64.b64encode(node._screenshot_bytes).decode()
# #         report.extra = report.extra or []
# #         report.extra.append(pytest_html.extras.png(encoded))
# # # @pytest.hookimpl(hookwrapper=True)
# # # def pytest_runtest_makereport(item, call):
# # #     outcome = yield
# # #     report = outcome.get_result()

# # #     # ✅ Only attach screenshots in the MASTER process
# # #     if hasattr(item.config, "workerinput"):
# # #         return

# # #     # ✅ Only for failures during test call
# # #     if report.when == "call" and report.failed:
# # #         page = item.funcargs.get("page", None)
# # #         if page:
# # #             # Take screenshot
# # #             screenshot_bytes = page.screenshot(full_page=True)

# # #             # Encode screenshot
# # #             encoded = base64.b64encode(screenshot_bytes).decode("utf-8")

# # #             # Get pytest-html plugin safely
# # #             pytest_html = item.config.pluginmanager.getplugin("html")
# # #             if pytest_html:
# # #                 extra = getattr(report, "extra", [])
# # #                 extra.append(pytest_html.extras.png(encoded))
# # #                 report.extra = extra


# # # @pytest.hookimpl(hookwrapper=True)
# # # def pytest_runtest_makereport(item, call):
# # #     """
# # #     Attach Playwright screenshot to pytest-html report on failure.
# # #     """
# # #     outcome = yield
# # #     report = outcome.get_result()

# # #     # Only on test failure
# # #     if report.when == "call" and report.failed:
# # #         page = item.funcargs.get("page", None)
# # #         if page:
# # #             # Take screenshot as bytes
# # #             screenshot_bytes = page.screenshot(full_page=True)

# # #             # Encode for pytest-html
# # #             encoded = base64.b64encode(screenshot_bytes).decode("utf-8")

# # #             extra = getattr(report, "extra", [])
# # #             extra.append(pytest_html.extras.png(encoded, mime_type="image/png"))
# # #             report.extra = extra

# # import pytest

# # @pytest.fixture(autouse=True)
# # def capture_screenshot_on_failure(request):
# #     """
# #     Capture Playwright screenshot immediately when a test fails
# #     (works correctly with pytest-xdist).
# #     """
# #     yield

# #     # Only after test execution
# #     rep_call = getattr(request.node, "rep_call", None)
# #     page = request.node.funcargs.get("page", None)

# #     if rep_call and rep_call.failed and page:
# #         # Capture screenshot while browser is still alive
# #         request.node._screenshot_bytes = page.screenshot(full_page=True)

# import os
# import base64
# import pytest
# from dotenv import load_dotenv
# from datetime import datetime
# from pathlib import Path

# # ======================
# # Environment
# # ======================

# load_dotenv()

# PROJECT_ROOT = Path(__file__).parent
# REPORTS_DIR = PROJECT_ROOT / "reports" / "html"


# # ======================
# # pytest-html (MASTER only)
# # ======================

# def pytest_configure(config):
#     """
#     Generate ONE pytest-html report per run (MASTER node only).
#     """
#     if hasattr(config, "workerinput"):
#         return

#     REPORTS_DIR.mkdir(parents=True, exist_ok=True)
#     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#     report_path = REPORTS_DIR / f"report_{timestamp}.html"

#     config.option.htmlpath = str(report_path)
#     config.option.self_contained_html = True


# # ======================
# # Store test result early
# # ======================

# @pytest.hookimpl(hookwrapper=True)
# def pytest_runtest_makereport(item, call):
#     """
#     This hook runs in both worker and master.
#     It is the ONLY safe place to attach pytest-html extras.
#     """
#     outcome = yield
#     report = outcome.get_result()

#     # Store report for fixtures
#     if report.when == "call":
#         item.rep_call = report

#         # ✅ MASTER only: attach screenshot to report
#         if not hasattr(item.config, "workerinput"):
#             if hasattr(item, "_screenshot_bytes"):
#                 pytest_html = item.config.pluginmanager.getplugin("html")
#                 encoded = base64.b64encode(item._screenshot_bytes).decode("utf-8")

#                 report.extra = report.extra or []
#                 report.extra.append(pytest_html.extras.png(encoded))


# # ======================
# # Capture screenshot (WORKER only)
# # ======================

# @pytest.fixture(autouse=True)
# def capture_screenshot_on_failure(request):
#     """
#     Capture screenshot at failure time in WORKER
#     before Playwright context is destroyed.
#     """
#     yield

#     if hasattr(request.config, "workerinput"):
#         rep_call = getattr(request.node, "rep_call", None)
#         page = request.node.funcargs.get("page", None)

#         if rep_call and rep_call.failed and page:
#             request.node._screenshot_bytes = page.screenshot(full_page=True)