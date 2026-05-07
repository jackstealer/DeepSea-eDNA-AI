"""
Download diverse marine eDNA data from multiple taxonomic groups
"""
import os
import sys
import time
import logging
from pathlib import Path
from Bio import Entrez, SeqIO
import json
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set your email for NCBI
Entrez.email = "research@edna.project"

# Define diverse marine taxonomic groups
MARINE_GROUPS = {
    "Perciformes": "Perciformes[Organism] AND COI[Gene]",  # Perch-like fishes
    "Salmoniformes": "Salmoniformes[Organism] AND COI[Gene]",  # Salmon, trout
    "Clupeiformes": "Clupeiformes[Organism] AND COI[Gene]",  # Herrings, anchovies
    "Gadiformes": "Gadiformes[Organism] AND COI[Gene]",  # Cod, haddock
    "Pleuronectiformes": "Pleuronectiformes[Organism] AND COI[Gene]",  # Flatfishes
    "Decapoda": "Decapoda[Organism] AND COI[Gene]",  # Crabs, shrimp, lobsters
    "Bivalvia": "Bivalvia[Organism] AND COI[Gene]",  # Clams, oysters, mussels
    "Gastropoda": "Gastropoda[Organism] AND COI[Gene]",  # Snails, slugs
}


def download_group(group_name, query, max_sequences=500, min_length=400, max_length=800):
    """Download sequences for a specific taxonomic group"""
    logger.info(f"\nDownloading {group_name}...")
    
    # Search
    try:
        length_filter = f" AND {min_length}:{max_length}[SLEN]"
        full_query = query + length_filter
        
        handle = Entrez.esearch(
            db="nucleotide",
            term=full_query,
            retmax=max_sequences,
            usehistory="y"
        )
        record = Entrez.read(handle)
        handle.close()
        
        id_list = record["IdList"]
        logger.info(f"  Found {len(id_list)} sequences for {group_name}")
        
        if not id_list:
            return []
        
        # Fetch sequences in batches
        sequences = []
        batch_size = 100
        
        for i in tqdm(range(0, len(id_list), batch_size), desc=f"  Fetching {group_name}"):
            batch_ids = id_list[i:i + batch_size]
            time.sleep(0.34)  # Rate limiting
            
            try:
                handle = Entrez.efetch(
                    db="nucleotide",
                    id=batch_ids,
                    rettype="gb",
                    retmode="text"
                )
                batch_records = list(SeqIO.parse(handle, "genbank"))
                handle.close()
                sequences.extend(batch_records)
            except Exception as e:
                logger.error(f"  Error fetching batch: {e}")
                continue
        
        logger.info(f"  Downloaded {len(sequences)} sequences for {group_name}")
        return sequences
        
    except Exception as e:
        logger.error(f"  Error with {group_name}: {e}")
        return []


def main():
    output_dir = "../data/training/marine_diverse"
    os.makedirs(output_dir, exist_ok=True)
    
    taxonomy_map = {}
    
    for class_id, (group_name, query) in enumerate(MARINE_GROUPS.items()):
        sequences = download_group(group_name, query, max_sequences=500)
        
        if sequences:
            # Create class directory
            class_dir = os.path.join(output_dir, f"class_{class_id}")
            os.makedirs(class_dir, exist_ok=True)
            
            # Save sequences
            output_file = os.path.join(class_dir, "sequences.fasta")
            SeqIO.write(sequences, output_file, "fasta")
            
            # Add to taxonomy map
            taxonomy_map[str(class_id)] = {
                'name': group_name,
                'rank': 'order',
                'count': len(sequences)
            }
            
            logger.info(f"  Saved {len(sequences)} sequences to {class_dir}")
    
    # Save taxonomy mapping
    taxonomy_file = os.path.join(output_dir, "taxonomy.json")
    with open(taxonomy_file, 'w') as f:
        json.dump(taxonomy_map, f, indent=2)
    
    logger.info(f"\n{'='*80}")
    logger.info(f"Download Complete!")
    logger.info(f"{'='*80}")
    logger.info(f"Output directory: {output_dir}")
    logger.info(f"Total classes: {len(taxonomy_map)}")
    total_sequences = sum(info['count'] for info in taxonomy_map.values())
    logger.info(f"Total sequences: {total_sequences}")
    logger.info(f"\nClass distribution:")
    for class_id, info in taxonomy_map.items():
        logger.info(f"  Class {class_id} ({info['name']}): {info['count']} sequences")


if __name__ == '__main__':
    main()
