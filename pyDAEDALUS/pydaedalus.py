"""
pyDAEDALUS - Python DAEDALUS for nucleic acid-scaffolded wireframe origami design

This module provides a direct interface for designing DNA/RNA origami structures
from 3D geometric inputs (PLY files).
"""

import os
from math import floor
from pathlib import Path
from typing import Optional, Union, Tuple

from Automated_Design.ply_to_input import ply_to_input
from Automated_Design.DX_cage_design import DX_cage_design
from Automated_Design.gen_PDB import pdbgen
try:
    from .exceptions import (
        PyDAEDALUSError, GeometryFileError, ScaffoldSequenceError, 
        HelicalParameterError, DesignConstraintError, StapleGenerationError,
        OutputDirectoryError, validate_geometry_file, validate_scaffold_sequence, 
        validate_output_directory
    )
except ImportError:
    from exceptions import (
        PyDAEDALUSError, GeometryFileError, ScaffoldSequenceError, 
        HelicalParameterError, DesignConstraintError, StapleGenerationError,
        OutputDirectoryError, validate_geometry_file, validate_scaffold_sequence, 
        validate_output_directory
    )


class DesignResult:
    """Container for design results and output files."""
    
    def __init__(self, project_name: str, output_dir: str, full_file_name: str):
        self.project_name = project_name
        self.output_dir = Path(output_dir)
        self.full_file_name = full_file_name
        
    @property
    def csv_file(self) -> Path:
        """Path to staple sequences CSV file."""
        return self.output_dir / f"staples_{self.full_file_name}.csv"
    
    @property
    def cndo_file(self) -> Path:
        """Path to CanDo structure file."""
        return self.output_dir / f"{self.full_file_name}.cndo"
    
    @property
    def pdb_file(self) -> Path:
        """Path to PDB atomic model file."""
        return self.output_dir / f"{self.full_file_name}.pdb"
    
    @property
    def plot_file(self) -> Path:
        """Path to 3D visualization plot."""
        return self.output_dir / f"{self.full_file_name}.png"


def design_structure(
    project_name: str,
    geometry_file: Union[str, Path],
    helical_form: str = "Bform",
    helical_turns: int = 4,
    scaffold_sequence: Optional[Union[str, Path]] = None,
    output_dir: Optional[Union[str, Path]] = None,
    single_crossovers: bool = False,
    print_output: bool = True
) -> DesignResult:
    """
    Design a nucleic acid-scaffolded wireframe origami structure.
    
    Parameters
    ----------
    project_name : str
        Name for the design project (used for output files)
    geometry_file : str or Path
        Path to PLY file containing 3D geometry
    helical_form : {"Bform", "Aform", "Hybrid", "Twisted"}, default "Bform"
        Helical form of nucleic acid:
        - "Bform": DNA default, 10.5 bp/turn, min 3 turns
        - "Aform": RNA default, 11 bp/turn, min 4 turns  
        - "Hybrid": Alternative A-form variant
        - "Twisted": Alternative wound A-form
    helical_turns : int, default 4
        Minimum number of helical turns per edge
    scaffold_sequence : str or Path, optional
        Path to text file with scaffold sequence, or sequence string.
        If None, uses M13 for short designs or random sequence for long designs.
    output_dir : str or Path, optional
        Directory for output files. If None, uses current directory.
    single_crossovers : bool, default False
        Whether to use single crossover vertex staples (True) or 
        double crossover vertex staples (False)
    print_output : bool, default True
        Whether to print progress information
        
    Returns
    -------
    DesignResult
        Object containing paths to generated output files
        
    Raises
    ------
    FileNotFoundError
        If geometry_file or scaffold_sequence file doesn't exist
    ValueError
        If helical_form is invalid or helical_turns is too small
        
    Examples
    --------
    >>> result = design_structure("my_tetrahedron", "tetrahedron.ply")
    >>> print(f"Staples saved to: {result.csv_file}")
    >>> print(f"3D model saved to: {result.pdb_file}")
    """
    
    # Comprehensive input validation with detailed error messages
    geometry_file = Path(geometry_file)
    validate_geometry_file(geometry_file)
    
    valid_forms = {"Aform", "Bform", "Hybrid", "Twisted"}
    if helical_form not in valid_forms:
        suggestions = [
            f"Use one of the valid helical forms: {', '.join(sorted(valid_forms))}",
            "For DNA structures, use 'Bform'", 
            "For RNA structures, use 'Aform'",
            "For advanced users: 'Hybrid' and 'Twisted' are A-form variants"
        ]
        raise PyDAEDALUSError(
            f"Invalid helical_form '{helical_form}'",
            f"Valid options are: {', '.join(sorted(valid_forms))}",
            suggestions
        )
    
    # Set minimum edge length requirements
    min_turns = {"Aform": 4, "Bform": 3, "Hybrid": 4, "Twisted": 4}
    if helical_turns < min_turns[helical_form]:
        raise HelicalParameterError(helical_form, helical_turns, min_turns[helical_form])
    
    # Validate scaffold sequence
    validate_scaffold_sequence(scaffold_sequence, project_name)
    
    # Set up and validate output directory
    if output_dir is not None:
        output_dir = Path(output_dir)
    project_dir = validate_output_directory(output_dir, project_name)
    
    # Configure helical parameters
    helical_config = _get_helical_config(helical_form, helical_turns)
    
    # Process geometry file with error handling
    try:
        coordinates, edges, faces, edge_length_vec, file_name, staple_name, singleXOs = ply_to_input(
            str(geometry_file), 
            str(project_dir), 
            helical_config["min_edge_len"], 
            helical_config["h_form"]
        )
    except AssertionError as e:
        raise GeometryFileError(
            filename=str(geometry_file),
            issue="PLY file format validation failed",
            technical_details=f"The PLY file appears to be corrupted or malformed: {str(e)}"
        )
    except Exception as e:
        if "map" in str(e) and "subscriptable" in str(e):
            raise DesignConstraintError(
                constraint="Geometry processing failed",
                geometry_info=f"File: {geometry_file}",
                technical_details=(
                    "This error often occurs with Python 3 compatibility issues in PLY processing. "
                    "The geometry may have edges that are too short or the PLY format may have issues."
                )
            )
        else:
            raise DesignConstraintError(
                constraint="Geometry processing failed", 
                geometry_info=f"File: {geometry_file}",
                technical_details=f"Unexpected error during PLY processing: {str(e)}"
            )
    
    # Validate geometry constraints
    num_edges = len(edges) if edges is not None else 0
    if num_edges == 0:
        raise DesignConstraintError(
            constraint="No edges found in geometry",
            geometry_info=f"File: {geometry_file}",
            technical_details="The PLY file must define a 3D polyhedron with edges"
        )
    
    total_edge_length = sum(edge_length_vec) if edge_length_vec is not None else 0
    min_scaffold_length = 2 * total_edge_length
    
    # Handle scaffold sequence with length validation
    try:
        scaf_seq, scaf_name = _process_scaffold_sequence(
            scaffold_sequence, project_name, edge_length_vec
        )
        
        # Validate scaffold length if provided
        if scaf_seq and len(scaf_seq) < min_scaffold_length:
            raise ScaffoldSequenceError(
                issue="Scaffold sequence too short",
                sequence_info=f"Provided: {len(scaf_seq)} nt, Required: ≥{min_scaffold_length} nt",
                technical_details=(
                    f"Geometry requires ~{min_scaffold_length} nucleotides "
                    f"({num_edges} edges, total length {total_edge_length:.1f} bp). "
                    f"Rule of thumb: scaffold length ≥ 2 × total edge length."
                )
            )
    except Exception as e:
        if isinstance(e, ScaffoldSequenceError):
            raise  # Re-raise our custom errors
        else:
            raise ScaffoldSequenceError(
                issue="Error processing scaffold sequence",
                technical_details=str(e)
            )
    
    # Run the main design algorithm with comprehensive error handling
    try:
        full_file_name = DX_cage_design(
            coordinates=coordinates,
            edges=edges, 
            faces=faces,
            edge_length_vec=edge_length_vec,
            file_name=file_name,
            staple_name=staple_name,
            singleXOs=int(single_crossovers),
            scaf_seq=scaf_seq,
            scaf_name=scaf_name,
            Aform=helical_config["h_form"],
            results_foldername=str(project_dir),
            twist=helical_config["twist"],
            print_to_console=print_output
        )
    except Exception as e:
        # Analyze the error and provide specific guidance
        error_str = str(e).lower()
        
        if "scaffold" in error_str and ("short" in error_str or "length" in error_str):
            raise ScaffoldSequenceError(
                issue="Scaffold too short during design",
                sequence_info=f"Current scaffold: {len(scaf_seq) if scaf_seq else 'default'} nt",
                technical_details=f"Design algorithm error: {str(e)}"
            )
        elif "staple" in error_str:
            raise StapleGenerationError(
                stage="Staple sequence assignment",
                technical_details=f"Error during staple generation: {str(e)}"
            )
        elif "routing" in error_str or "path" in error_str:
            raise DesignConstraintError(
                constraint="Scaffold routing failed",
                geometry_info=f"Edges: {num_edges}, Form: {helical_form}",
                technical_details=f"Cannot find valid scaffold path through geometry: {str(e)}"
            )
        else:
            raise DesignConstraintError(
                constraint="Design algorithm failed",
                geometry_info=f"Project: {project_name}, Form: {helical_form}, Turns: {helical_turns}",
                technical_details=f"Unexpected error in DX_cage_design: {str(e)}"
            )
    
    # Generate PDB file with error handling
    try:
        pdbgen(full_file_name, helical_config["h_form"], str(project_dir))
    except Exception as e:
        # PDB generation failure shouldn't stop the whole process
        if print_output:
            print(f"Warning: PDB file generation failed: {e}")
            print("Other output files (CSV, CanDo) were generated successfully.")
    
    return DesignResult(project_name, str(project_dir), full_file_name)


def _get_helical_config(helical_form: str, helical_turns: int) -> dict:
    """Get helical configuration parameters."""
    if helical_form == 'Aform':
        return {
            "min_edge_len": helical_turns * 11,
            "h_form": True,
            "twist": 1
        }
    elif helical_form == 'Bform':
        return {
            "min_edge_len": floor(helical_turns * 10.5),
            "h_form": False, 
            "twist": 1
        }
    elif helical_form == 'Hybrid':
        return {
            "min_edge_len": helical_turns * 11,
            "h_form": True,
            "twist": 2
        }
    elif helical_form == 'Twisted':
        return {
            "min_edge_len": helical_turns * 11,
            "h_form": True,
            "twist": 3
        }


def _process_scaffold_sequence(
    scaffold_sequence: Optional[Union[str, Path]], 
    project_name: str,
    edge_length_vec
) -> Tuple[str, str]:
    """Process scaffold sequence input."""
    if scaffold_sequence is None or scaffold_sequence == "M13.txt":
        # Use default M13 or random sequence
        return [], []
    
    # Check if it's a file path or sequence string
    if isinstance(scaffold_sequence, (str, Path)):
        scaffold_path = Path(scaffold_sequence)
        if scaffold_path.exists():
            # Read from file
            with open(scaffold_path, 'r') as f:
                scaf_seq = ''.join(line.strip() for line in f).upper()
            scaf_name = project_name
            return scaf_seq, scaf_name
        else:
            # Treat as sequence string
            scaf_seq = str(scaffold_sequence).upper()
            scaf_name = project_name
            return scaf_seq, scaf_name
    
    return [], []


# Convenience aliases for common use cases
def design_dna_structure(project_name: str, geometry_file: Union[str, Path], **kwargs) -> DesignResult:
    """Design a DNA structure (B-form helices)."""
    return design_structure(project_name, geometry_file, helical_form="Bform", **kwargs)


def design_rna_structure(project_name: str, geometry_file: Union[str, Path], **kwargs) -> DesignResult:
    """Design an RNA structure (A-form helices)."""
    return design_structure(project_name, geometry_file, helical_form="Aform", **kwargs)