"""
Custom exceptions for pyDAEDALUS with detailed error messages and troubleshooting guidance.
"""

import os
from pathlib import Path
from typing import List, Optional


class PyDAEDALUSError(Exception):
    """Base exception class for pyDAEDALUS with enhanced error reporting."""
    
    def __init__(self, message: str, technical_details: str = "", suggestions: List[str] = None):
        self.message = message
        self.technical_details = technical_details
        self.suggestions = suggestions or []
        
        # Build comprehensive error message
        full_message = f"{message}"
        
        if technical_details:
            full_message += f"\n\nTechnical Details:\n{technical_details}"
        
        if self.suggestions:
            full_message += f"\n\nSuggestions to fix this:"
            for i, suggestion in enumerate(self.suggestions, 1):
                full_message += f"\n  {i}. {suggestion}"
        
        super().__init__(full_message)


class GeometryFileError(PyDAEDALUSError):
    """Raised when there are issues with geometry file input."""
    
    def __init__(self, filename: str, issue: str, technical_details: str = ""):
        suggestions = [
            f"Check that the file '{filename}' exists and is readable",
            "Verify the file is in PLY format (see https://en.wikipedia.org/wiki/PLY_(file_format))",
            "Try opening the PLY file in a 3D viewer (like MeshLab) to verify it's valid",
            "Check the example PLY files in the repository for reference format"
        ]
        
        message = f"Problem with geometry file '{filename}': {issue}"
        super().__init__(message, technical_details, suggestions)


class ScaffoldSequenceError(PyDAEDALUSError):
    """Raised when there are issues with scaffold sequence input."""
    
    def __init__(self, issue: str, sequence_info: str = "", technical_details: str = ""):
        suggestions = [
            "Check that scaffold sequence file exists and contains valid nucleotides (A, T, G, C, U)",
            "Verify sequence length is sufficient for your geometry (typically 2x total edge length)",
            "Use 'M13.txt' or None to use default M13 scaffold sequence",
            "For large designs, pyDAEDALUS will generate random sequence automatically"
        ]
        
        message = f"Scaffold sequence problem: {issue}"
        if sequence_info:
            message += f" ({sequence_info})"
            
        super().__init__(message, technical_details, suggestions)


class HelicalParameterError(PyDAEDALUSError):
    """Raised when helical form parameters are invalid."""
    
    def __init__(self, helical_form: str, helical_turns: int, min_required: int):
        suggestions = [
            f"Use at least {min_required} helical turns for {helical_form}",
            f"A-form (RNA): minimum 4 turns, 11 bp/turn → {4*11} bp minimum edge",
            f"B-form (DNA): minimum 3 turns, 10.5 bp/turn → {int(3*10.5)} bp minimum edge",
            "Consider using longer edges or switching helical form",
            "Check that your geometry has sufficiently long edges for the chosen parameters"
        ]
        
        message = (f"Invalid helical parameters: {helical_form} with {helical_turns} turns "
                  f"(minimum {min_required} required)")
        
        technical_details = (
            f"Helical form '{helical_form}' requires minimum {min_required} helical turns. "
            f"This ensures sufficient nucleotides for proper crossover formation and "
            f"structural stability."
        )
        
        super().__init__(message, technical_details, suggestions)


class DesignConstraintError(PyDAEDALUSError):
    """Raised when design constraints cannot be satisfied."""
    
    def __init__(self, constraint: str, geometry_info: str = "", technical_details: str = ""):
        suggestions = [
            "Try increasing the number of helical turns per edge",
            "Use a simpler geometry with fewer faces or shorter edges",
            "Check that the geometry is a valid 3D polyhedron",
            "Verify the PLY file defines a closed, manifold surface",
            "Consider using B-form instead of A-form for more flexibility"
        ]
        
        message = f"Design constraint violation: {constraint}"
        if geometry_info:
            message += f"\nGeometry: {geometry_info}"
            
        super().__init__(message, technical_details, suggestions)


class StapleGenerationError(PyDAEDALUSError):
    """Raised when staple sequence generation fails."""
    
    def __init__(self, stage: str, technical_details: str = ""):
        suggestions = [
            "Check that scaffold sequence is long enough for the design",
            "Verify geometry has reasonable edge length distribution", 
            "Try using double crossover staples instead of single crossover",
            "Use a different scaffold sequence or let pyDAEDALUS generate one",
            "Simplify the geometry to reduce design complexity"
        ]
        
        message = f"Staple generation failed at stage: {stage}"
        super().__init__(message, technical_details, suggestions)


class OutputDirectoryError(PyDAEDALUSError):
    """Raised when output directory cannot be created or accessed."""
    
    def __init__(self, directory: str, issue: str):
        suggestions = [
            f"Check that you have write permissions for '{directory}'",
            "Verify the parent directory exists",
            "Try using a different output directory",
            "Check available disk space",
            "Ensure the path doesn't contain invalid characters"
        ]
        
        message = f"Output directory problem: {issue}"
        technical_details = f"Cannot access or create directory: {directory}"
        super().__init__(message, technical_details, suggestions)


def validate_geometry_file(geometry_file: Path) -> None:
    """Validate geometry file with detailed error reporting."""
    if not geometry_file.exists():
        # Check for common mistakes
        potential_files = []
        parent_dir = geometry_file.parent
        if parent_dir.exists():
            for f in parent_dir.iterdir():
                if f.suffix.lower() == '.ply':
                    potential_files.append(f.name)
        
        technical_details = f"File path: {geometry_file.absolute()}"
        if potential_files:
            technical_details += f"\n\nFound these PLY files in {parent_dir}:\n" + "\n".join(f"  - {f}" for f in potential_files)
        
        raise GeometryFileError(
            filename=str(geometry_file),
            issue="File not found",
            technical_details=technical_details
        )
    
    if not geometry_file.suffix.lower() == '.ply':
        raise GeometryFileError(
            filename=str(geometry_file),
            issue=f"Expected PLY file, got '{geometry_file.suffix}' file",
            technical_details=f"File must have .ply extension and be in PLY format"
        )
    
    # Check if file is readable and not empty
    try:
        with open(geometry_file, 'r') as f:
            content = f.read(100)  # Read first 100 chars
            if not content.strip():
                raise GeometryFileError(
                    filename=str(geometry_file),
                    issue="File is empty",
                    technical_details="PLY file contains no data"
                )
            
            if 'ply' not in content.lower():
                raise GeometryFileError(
                    filename=str(geometry_file),
                    issue="File doesn't appear to be in PLY format",
                    technical_details=f"Expected PLY header, found: {content[:50]}..."
                )
                
    except PermissionError:
        raise GeometryFileError(
            filename=str(geometry_file),
            issue="Permission denied",
            technical_details="Cannot read file due to permission restrictions"
        )
    except Exception as e:
        raise GeometryFileError(
            filename=str(geometry_file),
            issue="Cannot read file",
            technical_details=f"Unexpected error: {str(e)}"
        )


def validate_scaffold_sequence(scaffold_sequence, project_name: str):
    """Validate scaffold sequence input with helpful error messages."""
    if scaffold_sequence is None or scaffold_sequence == "M13.txt":
        return  # Valid default cases
    
    if isinstance(scaffold_sequence, (str, Path)):
        seq_path = Path(scaffold_sequence)
        
        # If it looks like a file path, validate as file
        if '/' in str(scaffold_sequence) or '\\' in str(scaffold_sequence) or seq_path.suffix:
            if not seq_path.exists():
                raise ScaffoldSequenceError(
                    issue="Scaffold sequence file not found",
                    sequence_info=f"File: {seq_path}",
                    technical_details=f"Attempted to read: {seq_path.absolute()}"
                )
            
            try:
                with open(seq_path, 'r') as f:
                    sequence = f.read().strip()
                    if not sequence:
                        raise ScaffoldSequenceError(
                            issue="Scaffold sequence file is empty",
                            sequence_info=f"File: {seq_path}"
                        )
                    
                    # Validate nucleotides
                    valid_bases = set('ATGCU')
                    invalid_chars = set(sequence.upper()) - valid_bases
                    if invalid_chars:
                        raise ScaffoldSequenceError(
                            issue="Invalid characters in scaffold sequence",
                            sequence_info=f"Found: {', '.join(sorted(invalid_chars))}",
                            technical_details=f"Only A, T, G, C, U are allowed. Sequence length: {len(sequence)}"
                        )
            except PermissionError:
                raise ScaffoldSequenceError(
                    issue="Cannot read scaffold sequence file",
                    sequence_info=f"Permission denied: {seq_path}"
                )
        else:
            # Treat as sequence string - validate nucleotides
            sequence = str(scaffold_sequence).upper()
            valid_bases = set('ATGCU')
            invalid_chars = set(sequence) - valid_bases
            if invalid_chars:
                raise ScaffoldSequenceError(
                    issue="Invalid characters in scaffold sequence string",
                    sequence_info=f"Found: {', '.join(sorted(invalid_chars))}",
                    technical_details=f"Only A, T, G, C, U are allowed. Sequence length: {len(sequence)}"
                )


def validate_output_directory(output_dir: Optional[Path], project_name: str) -> Path:
    """Validate and create output directory with helpful error messages."""
    if output_dir is None:
        output_dir = Path.cwd()
    
    project_dir = output_dir / project_name
    
    try:
        project_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise OutputDirectoryError(
            directory=str(project_dir),
            issue="Permission denied - cannot create directory"
        )
    except OSError as e:
        if "No space left on device" in str(e):
            raise OutputDirectoryError(
                directory=str(project_dir),
                issue="No space left on device"
            )
        else:
            raise OutputDirectoryError(
                directory=str(project_dir),
                issue=f"Cannot create directory: {str(e)}"
            )
    
    # Test write permissions
    test_file = project_dir / ".write_test"
    try:
        test_file.touch()
        test_file.unlink()
    except PermissionError:
        raise OutputDirectoryError(
            directory=str(project_dir),
            issue="Directory exists but is not writable"
        )
    
    return project_dir