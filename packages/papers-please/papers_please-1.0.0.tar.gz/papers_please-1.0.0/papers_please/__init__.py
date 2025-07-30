# papers_please/__init__.py

__version__ = "1.0.0"
__author__ = "Henrique Marques, Gabriel Barbosa, Renato Spessoto, Henrique Gomes, Eduardo Neves"

# Entidades principais
from .core.Researcher import Researcher
from .core.ResearchGroup import ResearchGroup
from .core.XMLParser import XMLParser

__all__ = [
    "Researcher",
    "ResearchGroup",
    "XMLParser"
]