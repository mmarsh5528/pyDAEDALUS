#!/usr/bin/env python3
"""
Example usage of pyDAEDALUS module interface

This demonstrates how to use pyDAEDALUS to design DNA/RNA origami structures.
"""

import pydaedalus

def main():
    """Basic example of designing a DNA origami structure."""
    
    print("pyDAEDALUS Module Example")
    print("=" * 40)
    
    # Design a simple DNA structure with custom output directory
    try:
        result = pydaedalus.design_dna_structure(
            project_name="example_tetrahedron",
            geometry_file="tet.ply",
            helical_turns=4,
            output_dir="./results",  # Custom output directory
            print_output=True
        )
        
        print(f"\n✓ Design completed successfully!")
        print(f"  Project: {result.project_name}")
        print(f"  Output directory: {result.output_dir}")
        print(f"  Staples CSV: {result.csv_file}")
        print(f"  3D structure: {result.pdb_file}")
        print(f"  Visualization: {result.plot_file}")
        
    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
        print("Make sure tet.ply exists in the current directory")
        
    except Exception as e:
        print(f"✗ Design failed: {e}")


def advanced_example():
    """More advanced example with custom parameters."""
    
    print("\nAdvanced Example - Custom Output Directory")
    print("-" * 45)
    
    try:
        # Design a DNA structure with M13 scaffold and custom output directory
        result = pydaedalus.design_dna_structure(
            project_name="dna_octahedron",
            geometry_file="oct.ply",  # octahedron
            helical_turns=4,          # standard for DNA
            scaffold_sequence="M13.txt",  # M13 scaffold
            output_dir="/tmp/pydaedalus_output",  # Custom output location
            single_crossovers=True,   # single crossover staples
            print_output=False        # quiet mode
        )
        
        print(f"✓ DNA octahedron design completed: {result.full_file_name}")
        print(f"  Output saved to: {result.output_dir}")
        
    except Exception as e:
        print(f"✗ Advanced example failed: {e}")


def output_directory_examples():
    """Show different ways to specify output directories."""
    
    print("\nOutput Directory Examples")
    print("-" * 30)
    
    examples = [
        ("Default (current directory)", None),
        ("Relative path", "./my_designs"),
        ("Absolute path", "/tmp/origami_designs"),
        ("Home directory", "~/Documents/pyDAEDALUS_results"),
    ]
    
    for description, output_dir in examples:
        print(f"{description}:")
        print(f"  output_dir={output_dir}")
        
        # Show what the result paths would look like
        if output_dir is None:
            effective_dir = "."
        else:
            effective_dir = output_dir
            
        print(f"  → Project folder: {effective_dir}/my_project/")
        print(f"  → Results in: {effective_dir}/my_project/staples_*.csv")
        print()


if __name__ == "__main__":
    main()
    advanced_example()
    output_directory_examples()