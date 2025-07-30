import sys
import importlib
import pytest

import streamlit_secure_context  # ensure module name available for importlib

class DummyComponentsModule:
    def __init__(self):
        self.declared_name = None
        self.declare_args = None

    def declare_component(self, name, **kwargs):
        # Record the component name and kwargs passed during declaration
        self.declared_name = name
        self.declare_args = kwargs
        # Return a fake component function
        def fake_component(**component_kwargs):
            return {"received": component_kwargs}
        return fake_component

@pytest.fixture(autouse=True)
def patch_components_module(monkeypatch):
    """
    Monkeypatch streamlit.components.v1 to use a dummy module,
    then import/ reload the streamlit_secure_context module.
    """
    dummy = DummyComponentsModule()
    monkeypatch.setitem(sys.modules, "streamlit.components.v1", dummy)
    # Remove any cached import of the wrapper
    if "streamlit_secure_context" in sys.modules:
        del sys.modules["streamlit_secure_context"]
    # Import fresh wrapper module, which will pick up our dummy
    ssc = importlib.import_module("streamlit_secure_context")
    importlib.reload(ssc)
    return dummy, ssc

def test_streamlit_secure_context_forwards_parameters(patch_components_module):
    dummy, ssc = patch_components_module
    result = ssc.streamlit_secure_context(
        model_path="test_model",
        security_config={"a": 1},
        inference_params={"b": 2},
        key="testkey",
        timeout=5,
        height=100,
        width=200,
    )
    assert isinstance(result, dict) and "received" in result
    recv = result["received"]
    assert recv["modelPath"] == "test_model"
    assert recv["securityConfig"] == {"a": 1}
    assert recv["inferenceParams"] == {"b": 2}
    assert recv["key"] == "testkey"
    assert recv["timeout"] == 5
    assert recv["height"] == 100
    assert recv["width"] == 200
    assert dummy.declared_name == "streamlit_secure_context"

def test_streamlit_secure_context_defaults(patch_components_module):
    dummy, ssc = patch_components_module
    result = ssc.streamlit_secure_context(model_path="m")
    recv = result["received"]
    assert recv["securityConfig"] == {}
    assert recv["inferenceParams"] == {}
    assert "timeout" not in recv

def test_streamlit_secure_context_exception_wrapped(monkeypatch):
    # Dummy module whose component raises, to test exception wrapping
    class EagerDummy:
        def declare_component(self, name, **kwargs):
            def broken_component(**kwargs):
                raise RuntimeError("component failure")
            return broken_component

    monkeypatch.setitem(sys.modules, "streamlit.components.v1", EagerDummy())
    # Reload wrapper to use broken component
    if "streamlit_secure_context" in sys.modules:
        del sys.modules["streamlit_secure_context"]
    ssc = importlib.import_module("streamlit_secure_context")
    importlib.reload(ssc)
    with pytest.raises(Exception) as excinfo:
        ssc.streamlit_secure_context(model_path="m", timeout=1)
    assert "streamlit_secure_context failed or timed out" in str(excinfo.value)