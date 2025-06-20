# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pyDAEDALUS is a Python-based tool for designing nucleic acid-scaffolded wireframe origami with double duplex edges. It processes 3D geometric input (PLY files) and generates scaffold routing and staple sequences for DNA/RNA origami folding.

## Architecture

### Direct Module Interface
- **pydaedalus.py**: Main module with `design_structure()` function
- **exceptions.py**: Comprehensive error handling with detailed messages
- **Automated_Design/**: Core processing modules for scaffold and staple assignment

### Key Processing Pipeline (11 steps in DX_cage_design):
1. Generate connectivity graphs and vertex-face indexing
2. Create spanning tree (designate edge types)
3. Split edges to implement scaffold crossovers
4. Split vertices into degree-N nodes
5. Set scaffold routing direction
6. Enumerate scaffold bases (DX/Hybrid/Twisted forms)
7. Assign scaffold bases to edges
8. Adjust scaffold nick positions
9. Assign staples with crossover choices
10. Generate staple sequences
11. Export to multiple formats (CanDo, PDB, CSV)

### Module Interface
- **Direct function calls**: Pure Python module interface
- **Enhanced error handling**: Detailed messages with troubleshooting guidance
- **Type hints**: Full IDE support with documentation

## Development Commands

### Using the Module
```bash
# Direct Python usage
python -c "import pydaedalus; result = pydaedalus.design_structure('test', 'tet.ply')"

# Run examples
python example.py
```

### Testing the Module
```bash
# Test imports and basic functionality
python -c "import pydaedalus; print('✓ Module imports successfully')"
```

### Installing Dependencies
```bash
# Python dependencies
pip install -r requirements.txt
```

## Key File Types and Formats

### Input Files
- **PLY files**: 3D geometry (vertices, edges, faces)
- **TXT files**: Scaffold sequences (ACTGU nucleotides)

### Output Files (generated in project folders)
- **CSV**: Staple sequences and scaffold sequence
- **CNDO**: CanDo format for 3D structure visualization
- **PDB**: Multiple atomic model variants (single chain, multi-model, segid)
- **PNG**: Edge length distributions and Schlegel diagrams
- **Pickle**: Serialized DnaInfo and routing data

## Helical Forms and Parameters
- **A-form**: RNA default, 11 bp/turn, minimum 4 helical turns (44 bp)
- **B-form**: DNA default, 10.5 bp/turn, minimum 3 helical turns (31 bp)
- **Hybrid/Twisted**: Alternative A-form variants

## Important Constants and Sequences
- **M13_SCAF_SEQ**: Default 7249 nt scaffold sequence (constants.py)
- **Default sequences**: M13.txt, EGFP_seq.txt, 23SdomIIV_seq.txt

## Error Handling
- Comprehensive error validation with detailed messages
- Custom exception hierarchy for specific error types
- Technical details and actionable troubleshooting suggestions
- File path validation and alternative suggestions
- Constraint validation with scientific context

## Code Conventions
- Python 3.7+ codebase with modern package versions
- Uses numpy arrays for coordinate/edge data structures
- NetworkX graphs for connectivity analysis
- Matplotlib for visualization outputs
- Enhanced error handling with custom exception classes