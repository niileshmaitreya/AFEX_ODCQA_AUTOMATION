
import os
import time
import logging

logger = logging.getLogger("bdd_hooks")
if not logger.handlers:
    handler = logging.StreamHandler()
    fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    handler.setFormatter(fmt)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def pytest_bdd_before_scenario(request, feature, scenario):
    logger.info(f"[BDD] Starting scenario: {scenario.name}")

def pytest_bdd_after_scenario(request, feature, scenario):
    status = getattr(scenario, 'status', 'completed')
    logger.info(f"[BDD] Finished scenario: {scenario.name} | status={status}")

def pytest_bdd_before_step(request, feature, scenario, step, step_func):
    request.node._step_started_at = time.time()
    logger.info(f"[BDD] Step start: {step.keyword} {step.name}")

def pytest_bdd_after_step(request, feature, scenario, step, step_func, step_func_args):
    duration = None
    if hasattr(request.node, '_step_started_at'):
        duration = time.time() - request.node._step_started_at
    if duration is not None:
        logger.info(f"[BDD] Step end: {step.keyword} {step.name} | {duration:.2f}s")
    else:
        logger.info(f"[BDD] Step end: {step.keyword} {step.name}")

def pytest_bdd_step_error(request, feature, scenario, step, step_func, exception):
    page = request.node.funcargs.get('page') if hasattr(request, 'node') else None
    ts = time.strftime("%Y%m%d_%H%M%S")
    os.makedirs('artifacts', exist_ok=True)
    if page:
        try:
            safe_scenario = scenario.name.replace(' ', '_')
            safe_step = step.name.replace(' ', '_')
            path = f"artifacts/STEP_FAIL_{safe_scenario}_{safe_step}_{ts}.png"
            page.screenshot(path=path, full_page=True)
            logger.error(f"[BDD] Step failed, screenshot saved: {path}")
        except Exception as e:
            logger.error(f"[BDD] Failed to capture screenshot: {e}")
    logger.error(f"[BDD] Step failed: {step.keyword} {step.name}: {exception}")
