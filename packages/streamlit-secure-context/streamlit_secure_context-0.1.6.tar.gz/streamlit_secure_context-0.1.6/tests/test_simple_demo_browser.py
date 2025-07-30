import subprocess
import time
import signal
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture(scope="module")
def streamlit_server():
    # Launch the simple demo on port 8501
    proc = subprocess.Popen(
        ["streamlit", "run", "examples/simple_demo.py", "--server.port", "8501"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait for Streamlit to start
    time.sleep(5)
    yield
    proc.send_signal(signal.SIGINT)
    proc.wait()

@pytest.mark.skip(reason="Skipping Selenium UI test due to offline environment and driver download constraints")
def test_simple_demo_ui(streamlit_server):
    # Start Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    try:
        driver.get("http://localhost:8501")
        # Verify page title contains our Iris demo title
        # Streamlit page title is set via st.set_page_config
        assert "Simple Iris Inference Demo" in driver.title
        # Click the Run Inference button
        button = driver.find_element(By.TAG_NAME, "button")
        button.click()
        # Wait for result to appear
        time.sleep(3)
        # Check that the result subheader is present
        subheader = driver.find_element(By.TAG_NAME, "h2")
        assert "Result" in subheader.text
        # Ensure some output is displayed
        output = driver.find_element(By.CSS_SELECTOR, ".stMarkdown")
        assert output.text.strip() != ""
    finally:
        driver.quit()
