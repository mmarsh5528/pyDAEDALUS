# pyDAEDALUS

A Python-based tool for designing nucleic acid-scaffolded wireframe origami with double duplex edges. pyDAEDALUS processes 3D geometric input (PLY files) and generates scaffold routing and staple sequences for DNA/RNA origami folding.

## Features

- **Modern Python Module Interface**: Direct function calls with comprehensive error handling
- **Multiple Helical Forms**: Support for A-form (RNA), B-form (DNA), and hybrid variants
- **Comprehensive Output**: Generate CanDo, PDB, CSV formats and visualization plots
- **Robust Error Handling**: Detailed error messages with troubleshooting guidance
- **Example Geometries**: Includes tetrahedron, octahedron, and other test shapes

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/mmarsh5528/pyDAEDALUS.git
cd pyDAEDALUS

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
import pydaedalus

# Design a DNA tetrahedron
result = pydaedalus.design_dna_structure(
    project_name="my_tetrahedron",
    geometry_file="tet.ply",
    helical_turns=4
)

print(f"Output saved to: {result.output_dir}")
print(f"Staples: {result.csv_file}")
print(f"3D model: {result.pdb_file}")
```

### Run Examples

```bash
# Run the included examples
python example.py
```

## Usage

### Design Functions

#### `design_structure(project_name, geometry_file, **options)`
Main design function with full customization options.

```python
result = pydaedalus.design_structure(
    project_name="my_design",
    geometry_file="geometry.ply",
    helical_form="Bform",           # "Bform", "Aform", "Hybrid", "Twisted"
    helical_turns=4,                # Minimum turns per edge
    scaffold_sequence="M13.txt",    # Scaffold sequence file or None
    output_dir="./results",         # Output directory
    single_crossovers=False,        # Crossover type
    print_output=True               # Progress messages
)
```

#### Convenience Functions

```python
# DNA structures (B-form helices)
result = pydaedalus.design_dna_structure("dna_cage", "octahedron.ply")

# RNA structures (A-form helices) 
result = pydaedalus.design_rna_structure("rna_cage", "tetrahedron.ply")
```

### Input Files

#### Geometry Files (PLY format)
3D polyhedron geometry with vertices, edges, and faces:
```
ply
format ascii 1.0
element vertex 4
property float32 x
property float32 y
property float32 z
element face 4
property list uint8 int32 vertex_indices
end_header
0.000000 0.000000 0.612372
-0.288675 -0.500000 -0.204124
...
```

#### Scaffold Sequences (TXT format)
Nucleotide sequences for scaffold strands:
- `M13.txt` - 7,249 nt M13 bacteriophage sequence (default)
- `EGFP_seq.txt` - 793 nt EGFP sequence  
- `23SdomIIV_seq.txt` - 1,981 nt ribosomal RNA sequence

### Output Files

Each design generates multiple output files:

- **`staples_*.csv`** - Staple sequences for ordering/synthesis
- **`*.cndo`** - CanDo format for 3D structure visualization
- **`*.pdb`** - Atomic model files (multiple variants)
- **`*.png`** - Edge length distributions and Schlegel diagrams

## Helical Forms

| Form | Type | bp/turn | Min turns | Min edge length |
|------|------|---------|-----------|-----------------|
| **B-form** | DNA | 10.5 | 3 | 31 bp |
| **A-form** | RNA | 11 | 4 | 44 bp |
| **Hybrid** | RNA variant | 11 | 4 | 44 bp |
| **Twisted** | RNA variant | 11 | 4 | 44 bp |

## Examples

### DNA Tetrahedron
```python
result = pydaedalus.design_dna_structure(
    project_name="tetrahedron",
    geometry_file="tet.ply",
    helical_turns=4
)
```

### RNA Octahedron with Custom Scaffold  
```python
result = pydaedalus.design_structure(
    project_name="rna_octahedron", 
    geometry_file="oct.ply",
    helical_form="Aform",
    helical_turns=5,
    scaffold_sequence="23SdomIIV_seq.txt"
)
```

### Custom Output Directory
```python
result = pydaedalus.design_dna_structure(
    project_name="my_design",
    geometry_file="geometry.ply", 
    output_dir="/path/to/output",
    single_crossovers=True
)
```

## Architecture

### Processing Pipeline
1. **Parse Geometry**: Extract vertices, edges, faces from PLY file
2. **Generate Connectivity**: Create graphs and vertex-face indexing  
3. **Designate Edge Types**: Build spanning tree structure
4. **Split Elements**: Implement scaffold crossovers and vertex splitting
5. **Route Scaffold**: Set scaffold direction and enumerate bases
6. **Assign Staples**: Generate staple sequences with crossover choices
7. **Export Results**: Output to CanDo, PDB, CSV, and visualization formats

### Core Modules
- **`pydaedalus.py`** - Main module interface
- **`exceptions.py`** - Comprehensive error handling  
- **`Automated_Design/`** - Core processing algorithms
  - `ply_to_input.py` - PLY file parsing
  - `DX_cage_design.py` - Main design algorithm
  - `assign_staples_wChoices.py` - Staple sequence generation
  - `gen_PDB.py` - Atomic model generation

## Error Handling

pyDAEDALUS provides detailed error messages with troubleshooting guidance:

```python
try:
    result = pydaedalus.design_structure("test", "geometry.ply")
except pydaedalus.GeometryFileError as e:
    print(f"Geometry issue: {e}")
    # Detailed suggestions provided in error message
    
except pydaedalus.ScaffoldSequenceError as e:
    print(f"Scaffold issue: {e}")
    # Technical details and solutions provided
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality  
5. Submit a pull request

## License

This project is licensed under GPL-2.0. See the source files for detailed license information.

## Citation

If you use pyDAEDALUS in your research, please cite the original DAEDALUS paper and this Python implementation.

## Support

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/mmarsh5528/pyDAEDALUS/issues)
- **Examples**: See `example.py` for working code examples
- **Documentation**: Refer to function docstrings and error messages for detailed guidance