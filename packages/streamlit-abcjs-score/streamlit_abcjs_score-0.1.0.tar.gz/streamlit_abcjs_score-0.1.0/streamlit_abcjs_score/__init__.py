import os
import mimetypes
import streamlit.components.v1 as components
from typing import Optional

# Register MIME types to ensure proper file serving
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/json', '.json')
mimetypes.add_type('text/html', '.html')

# Create a _component_func which will call the frontend component.
# We create this here so we can add some caching, import the frontend HTML, etc.

_RELEASE = True
COMPONENT_NAME = "streamlit_abcjs_score"

if _RELEASE:
    # Use the build folder when in release mode
    root_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(root_dir, "frontend/build")
    _component_func = components.declare_component(COMPONENT_NAME, path=build_dir)
else:
    # Use the development server when in development mode
    _component_func = components.declare_component(
        COMPONENT_NAME,
        url="http://localhost:3001",
    )


def abc_score(
    notation: str,
    height: int = 400,
    width: Optional[int] = None,
    scale: float = 1.0,
    responsive: bool = True,
    key: Optional[str] = None,
    **kwargs
) -> None:
    """
    Create a new instance of "streamlit_abcjs_score".
    
    This component renders ABC notation as sheet music using the abc.js library.
    
    Parameters
    ----------
    notation : str
        The ABC notation string to render as sheet music.
        
    height : int, default 400
        The height of the rendered score container in pixels.
        
    width : int, optional
        The width of the rendered score container in pixels.
        If None, the component will use the full width available.
        
    scale : float, default 1.0
        The scale factor for the rendered score (1.0 = normal size).
        
    responsive : bool, default True
        Whether the rendered score should be responsive to container size changes.
        
    key : str, optional
        An optional key that uniquely identifies this component. If this is
        None, and the component's arguments are changed, the component will
        be re-mounted in the Streamlit frontend and lose its current state.

    Returns
    -------
    None
        This component doesn't return any value.

    Example
    -------
    >>> import streamlit as st
    >>> from streamlit_abcjs_score import abc_score
    >>> 
    >>> notation = '''T: Twinkle, Twinkle, Little Star
    ... M: 4/4
    ... L: 1/4
    ... K: C
    ... |: C C G G | A A G2 | F F E E | D D C2 :|'''
    >>> 
    >>> abc_score(notation=notation, height=300)
    """
    
    # Validate inputs
    if not isinstance(notation, str):
        raise TypeError("notation must be a string")
    
    if not notation.strip():
        raise ValueError("notation cannot be empty")
    
    if height <= 0:
        raise ValueError("height must be positive")
    
    if width is not None and width <= 0:
        raise ValueError("width must be positive")
    
    if scale <= 0:
        raise ValueError("scale must be positive")
    
    # Call through to our private component function
    component_value = _component_func(
        notation=notation,
        height=height,
        width=width,
        scale=scale,
        responsive=responsive,
        key=key,
        default=None,
        **kwargs
    )
    
    return component_value


# Add some example ABC notation for testing
EXAMPLE_NOTATION = {
    "twinkle_star": """T: Twinkle, Twinkle, Little Star
M: 4/4
L: 1/4
K: C
|: C C G G | A A G2 | F F E E | D D C2 :|""",
    
    "cooley_reel": """T: Cooley's
M: 4/4
L: 1/8
R: reel
K: Emin
|:D2|EB{c}BA B2 EB|~B2 AB dBAG|FDAD BDAD|FDAD dAFD|
EBBA B2 EB|B2 AB defg|afe^c dBAF|DEFD E2:|
|:gf|eB B2 efge|eB B2 gedB|A2 FA DAFA|A2 FA defg|
eB B2 eBgB|eB B2 defg|afe^c dBAF|DEFD E2:|""",
    
    "mary_had_lamb": """T: Mary Had a Little Lamb
M: 4/4
L: 1/4
K: C
E D C D | E E E2 | D D D2 | E G G2 |
E D C D | E E E2 | D D E D | C4 |"""
}


def get_example_notation(name: str) -> str:
    """
    Get example ABC notation by name.
    
    Parameters
    ----------
    name : str
        Name of the example. Available examples:
        - "twinkle_star": Twinkle, Twinkle, Little Star
        - "cooley_reel": Cooley's Reel (traditional Irish tune)
        - "mary_had_lamb": Mary Had a Little Lamb
    
    Returns
    -------
    str
        The ABC notation string for the requested example.
        
    Raises
    ------
    KeyError
        If the requested example name is not found.
    """
    if name not in EXAMPLE_NOTATION:
        available = ", ".join(EXAMPLE_NOTATION.keys())
        raise KeyError(f"Example '{name}' not found. Available examples: {available}")
    
    return EXAMPLE_NOTATION[name]


def list_examples() -> list:
    """
    List all available example notation names.
    
    Returns
    -------
    list
        List of available example names.
    """
    return list(EXAMPLE_NOTATION.keys())
