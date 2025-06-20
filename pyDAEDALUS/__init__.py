"""
pyDAEDALUS - Python DAEDALUS for nucleic acid-scaffolded wireframe origami design

A Python package for designing DNA/RNA origami structures from 3D geometric inputs.
"""

from .pydaedalus import design_structure, design_dna_structure, design_rna_structure, DesignResult
from .exceptions import (
    PyDAEDALUSError, GeometryFileError, ScaffoldSequenceError, 
    HelicalParameterError, DesignConstraintError, StapleGenerationError, 
    OutputDirectoryError
)

__version__ = "1.0.0"
__author__ = "Sakul Ratanalert, Tyson Shepherd"

__all__ = [
    "design_structure",
    "design_dna_structure", 
    "design_rna_structure",
    "DesignResult",
    # Exception classes for advanced error handling
    "PyDAEDALUSError",
    "GeometryFileError", 
    "ScaffoldSequenceError",
    "HelicalParameterError",
    "DesignConstraintError", 
    "StapleGenerationError",
    "OutputDirectoryError"
]