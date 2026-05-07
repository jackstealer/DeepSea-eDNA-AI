"""
Create sample training data for testing
"""
import os
import json
import random
from pathlib import Path
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from Bio import SeqIO

# Marine taxa for classification
TAXA = [
    {"name": "Copepoda", "rank": "Order", "lineage": ["Animalia", "Arthropoda", "Crustacea", "Copepoda"]},
    {"name": "Amphipoda", "rank": "Order", "lineage": ["Animalia", "Arthropoda", "Crustacea", "Amphipoda"]},
    {"name": "Decapoda", "rank": "Order", "lineage": ["Animalia", "Arthropoda", "Crustacea", "Decapoda"]},
    {"name": "Euphausiacea", "rank": "Order", "lineage": ["Animalia", "Arthropoda", "Crustacea", "Euphausiacea"]},
    {"name": "Mysida", "rank": "Order", "lineage": ["Animalia", "Arthropoda", "Crustacea", "Mysida"]},
]

def generate_realistic_sequence(length=500, gc_content=0.5):
    """Generate a realistic DNA sequence"""
    bases = ['A', 'C', 'G', 'T']
    
    # Adjust base probabilities for GC content
    gc_prob = gc_content / 2
    at_prob = (1 - gc_content) / 2
    
    probs = [at_prob, gc_prob, gc_prob, at_prob]
    
    sequence = ''.join(random.choices(bases, weights=probs, k=length))
    return sequence

def create_sample_dataset(output_dir, sequences_per_class=100):
    """Create sample training dataset"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    taxonomy_map = {}
    
    print(f"Creating sample dataset with {len(TAXA)} classes...")
    print(f"Sequences per class: {sequences_per_class}")
    
    for class_id, taxon in enumerate(TAXA):
        print(f"\nGenerating class {class_id}: {taxon['name']}")
        
        # Create class directory
        class_dir = output_path / f"class_{class_id}"
        class_dir.mkdir(exist_ok=True)
        
        # Generate sequences
        sequences = []
        for i in range(sequences_per_class):
            # Vary sequence length and GC content slightly per taxon
            length = random.randint(400, 600)
            gc_content = 0.45 + (class_id * 0.02)  # Slight variation per taxon
            
            seq_str = generate_realistic_sequence(length, gc_content)
            
            record = SeqRecord(
                Seq(seq_str),
                id=f"{taxon['name']}_{i}",
                description=f"Sample sequence for {taxon['name']}"
            )
            sequences.append(record)
        
        # Save to FASTA
        fasta_file = class_dir / "sequences.fasta"
        SeqIO.write(sequences, fasta_file, "fasta")
        print(f"  Saved {len(sequences)} sequences to {fasta_file}")
        
        # Add to taxonomy map
        taxonomy_map[str(class_id)] = {
            "name": taxon["name"],
            "rank": taxon["rank"],
            "lineage": taxon["lineage"]
        }
    
    # Save taxonomy mapping
    taxonomy_file = output_path / "taxonomy.json"
    with open(taxonomy_file, 'w') as f:
        json.dump(taxonomy_map, f, indent=2)
    
    print(f"\n✓ Sample dataset created successfully!")
    print(f"  Location: {output_path}")
    print(f"  Total sequences: {len(TAXA) * sequences_per_class}")
    print(f"  Classes: {len(TAXA)}")
    print(f"  Taxonomy map: {taxonomy_file}")

if __name__ == '__main__':
    output_dir = "../data/training/sample_marine"
    sequences_per_class = 100  # Small dataset for quick training
    
    create_sample_dataset(output_dir, sequences_per_class)
