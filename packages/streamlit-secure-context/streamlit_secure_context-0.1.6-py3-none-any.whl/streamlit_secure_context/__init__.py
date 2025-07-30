"""
Python API for streamlit-secure-context Component.
Provides `streamlit_secure_context()` to embed a secure context widget in Streamlit apps.
"""
__version__ = "0.1.6"

import os
import importlib
from streamlit.errors import StreamlitAPIException

# Toggle between development mode (local build) and release mode (CDN-hosted)
# NOTE: _RELEASE is determined dynamically based on the presence of a local build directory.

# Compute path to the frontend build directory
_MODULE_DIR = os.path.abspath(os.path.dirname(__file__))
_ROOT_DIR = os.path.abspath(os.path.join(_MODULE_DIR, os.pardir))
# Possible local build locations
_PKG_BUILD_DIR = os.path.join(_MODULE_DIR, "frontend", "build")
_ROOT_BUILD_DIR = os.path.join(_ROOT_DIR, "frontend", "build")

# Determine release mode based on presence of local build artifacts or env override
_env_release = os.getenv("STREAMLIT_SECURE_CONTEXT__RELEASE")
if _env_release is not None:
    # Env var override: "1"/"true" enables release mode (CDN), "0"/"false" disables
    _RELEASE = _env_release.lower() in ("1", "true")
else:
    _RELEASE = not (
        os.path.isdir(_PKG_BUILD_DIR) or os.path.isdir(_ROOT_BUILD_DIR)
    )

# Guard: ensure frontend is built before use in development mode
if not _RELEASE:
    # Determine which build directory to check
    if os.path.isdir(_PKG_BUILD_DIR):
        _BUILD_DIR = _PKG_BUILD_DIR
    else:
        _BUILD_DIR = _ROOT_BUILD_DIR
    index_html = os.path.join(_BUILD_DIR, "index.html")
    if not os.path.exists(index_html):
        raise StreamlitAPIException(
            f"Could not find frontend build at '{_BUILD_DIR}'. "
            "Please run `npm install && npm run build` in the frontend directory."
        )

# Will declare Streamlit component at runtime
_streamlit_secure_context = None

def streamlit_secure_context(
    model_path: str,
    security_config: dict = None,
    inference_params: dict = None,
    key: str = None,
    timeout: int = 0,
    **component_kwargs
):
    """
    Embed a secure context component in a Streamlit app.

    Parameters:
    - model_path (str): URL or file path to the ML model (HTTPS recommended in production).
    - security_config (dict, optional): Security parameters (COOP, COEP, CSP, sandbox, HTTPS enforcement).
    - inference_params (dict, optional): Parameters to pass to the ML inference worker.
    - key (str, optional): Identifier for this component instance (required if multiple on one page).
    - timeout (int, optional): Seconds to wait for component initialization before raising an error. Default is 0 (no timeout).
    - **component_kwargs: Additional kwargs (e.g., height, width) forwarded to the Streamlit component.

    Returns:
    - The result object from the frontend worker via `Streamlit.setComponentValue()`.

    Usage:
    ```python
    result = streamlit_secure_context(
        model_path="https://.../model.json",
        security_config={"requireHTTPS": True},
        inference_params={"input": [[1,2,3,4]]},
        key="demo1",
        height=400,
        width=600,
        timeout=30,  # wait up to 30 seconds for the component to load
    )
    ```
    """
    # Dynamic import to capture monkeypatched streamlit.components.v1
    # Lazy-declare Streamlit component so tests can monkeypatch declare_component
    # Import the components module directly to respect sys.modules overrides
    components = importlib.import_module("streamlit.components.v1")
    global _streamlit_secure_context
    # Declare the Streamlit component once and cache the component function
    if _streamlit_secure_context is None:
        if not _RELEASE:
            # During development, serve component assets from local build
            if os.path.isdir(_PKG_BUILD_DIR):
                comp_path = _PKG_BUILD_DIR
            else:
                comp_path = _ROOT_BUILD_DIR
            # Ensure the frontend build artifacts are present
            index_html = os.path.join(comp_path, "index.html")
            if not os.path.exists(index_html):
                raise StreamlitAPIException(
                    f"Could not find frontend build at '{comp_path}'. "
                    "Please run `npm install && npm run build` in the frontend directory."
                )
            _streamlit_secure_context = components.declare_component(
                "streamlit_secure_context",
                path=comp_path,
            )
        else:
            # Release mode: serve from CDN
            _streamlit_secure_context = components.declare_component(
                "streamlit_secure_context",
                url="https://unpkg.com/streamlit-secure-context@0.1.6/dist/index.js",
            )
    # Only forward timeout if non-zero (0 = no timeout)
    if timeout:
        component_kwargs['timeout'] = timeout
    # Forward additional kwargs (e.g., height, width) to the Streamlit component
    try:
        return _streamlit_secure_context(
            modelPath=model_path,
            securityConfig=security_config or {},
            inferenceParams=inference_params or {},
            key=key,
            **component_kwargs,
        )
    except Exception as e:
        # Provide a clearer error message on timeout or component failure
        raise StreamlitAPIException(
            f"streamlit_secure_context failed or timed out: {e}\n"
            "Ensure the frontend is built (npm run build), modelPath is reachable, and security settings are correct."
        )
