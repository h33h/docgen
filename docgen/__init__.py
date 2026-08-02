"""Configuration-driven DOCX and PPTX generation."""

__version__ = "0.1.0"

from .document import DocumentGenerator
from .presentation import PresentationGenerator

__all__ = ["DocumentGenerator", "PresentationGenerator", "__version__"]
