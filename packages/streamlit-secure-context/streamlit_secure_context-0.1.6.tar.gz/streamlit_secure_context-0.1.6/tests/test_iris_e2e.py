import pytest
# Skip end-to-end browser tests by default (may not be supported in all environments)
import subprocess
import time
# Remaining imports and fixtures follow

@pytest.fixture(scope="module")
def streamlit_app():
    proc = subprocess.Popen(
        ["streamlit", "run", "examples/app.py", "--server.headless=true", "--server.port=8501"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(5)
    yield
    proc.terminate()
    proc.wait(5)

import pytest

def test_iris_inference_e2e(page, streamlit_app, browser_context_args):
    page.goto("http://localhost:8501")
    page.wait_for_load_state("networkidle")
    page.click("text=Run Inference")
    # Wait for the JSON output containing "output" field
    locator = page.wait_for_selector("text=Prediction")
    text = locator.inner_text()
    assert text and text.strip() != "" and text != "None"
