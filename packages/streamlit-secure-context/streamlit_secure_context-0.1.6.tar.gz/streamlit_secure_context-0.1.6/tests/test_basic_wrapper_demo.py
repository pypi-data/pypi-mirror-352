import importlib
import sys
import types
import pytest

from streamlit_secure_context import streamlit_secure_context

def _setup_dummy_streamlit(monkeypatch):
    """
    Monkey-patch streamlit.components.v1.declare_component to provide a dummy component
    that echoes back call kwargs.
    """
    called = {}

    def dummy_declare_component(name, **init_kwargs):
        def component_func(**call_kwargs):
            called['name'] = name
            called['init_kwargs'] = init_kwargs
            called['call_kwargs'] = call_kwargs
            return {'foo': 'bar', 'received': call_kwargs}
        return component_func

    # Create fake streamlit modules
    streamlit_mod = types.ModuleType('streamlit')
    comps_mod = types.ModuleType('streamlit.components')
    comps_v1 = types.ModuleType('streamlit.components.v1')
    comps_v1.declare_component = dummy_declare_component
    comps_mod.v1 = comps_v1
    streamlit_mod.components = comps_mod
    errors_mod = types.ModuleType('streamlit.errors')
    errors_mod.StreamlitAPIException = Exception
    streamlit_mod.errors = errors_mod

    # Inject into sys.modules
    monkeypatch.setitem(sys.modules, 'streamlit', streamlit_mod)
    monkeypatch.setitem(sys.modules, 'streamlit.components', comps_mod)
    monkeypatch.setitem(sys.modules, 'streamlit.components.v1', comps_v1)
    monkeypatch.setitem(sys.modules, 'streamlit.errors', errors_mod)

    return called

def test_basic_wrapper(monkeypatch):
    called = _setup_dummy_streamlit(monkeypatch)

    result = streamlit_secure_context(
        model_path='dummy_url',
        security_config={'coop': 'same-origin'},
        inference_params={'x': 123},
        key='test_key',
        height=100,
        width=100,
    )

    assert isinstance(result, dict)
    assert result['foo'] == 'bar'
    assert called['name'] == 'streamlit_secure_context'
    assert called['call_kwargs'] == {
        'modelPath': 'dummy_url',
        'securityConfig': {'coop': 'same-origin'},
        'inferenceParams': {'x': 123},
        'key': 'test_key',
        'height': 100,
        'width': 100,
    }