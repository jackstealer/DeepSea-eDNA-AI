"""
Download real-world eDNA sequences from NCBI GenBank
"""
import os
import sys
import time
import argparse
import logging
from pathlib import Path
from typing import List, Dict
from Bio import Entrez, SeqIO
from Bio.SeqRecord import SeqRecord
import json
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NCBIDataDownloader:
    """
    Download sequences from NCBI GenBank with taxonomy information
    """
    
    def __init__(self, email: str, api_key: str = None):
        """
        Initialize NCBI downloader
        
        Args:
            email: Your email (required by NCBI)
            api_key: NCBI API key (optional, increases rate limit)
        """
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key
        self.delay = 0.34 if api_key else 0.34  # Respect NCBI rate limits
        
    def search_sequences(
        self,
        query: str,
        max_sequences: int = 10000,
        min_length: int = 100,
        max_length: int = 2000
    ) -> List[str]:
        """
        Search for sequence IDs matching query
        
        Args:
            query: NCBI search query (e.g., "marine[organism] AND COI[gene]")
            max_sequences: Maximum number of sequences to retrieve
            min_length: Minimum sequence length
            max_length: Maximum sequence length
            
        Returns:
            List of GenBank IDs
        """
        logger.info(f"Searching NCBI with query: {query}")
        
        # Add length filters to query
        length_filter = f" AND {min_length}:{max_length}[SLEN]"
        full_query = query + length_filter
        
        try:
            handle = Entrez.esearch(
                db="nucleotide",
                term=full_query,
                retmax=max_sequences,
                usehistory="y"
            )
            record = Entrez.read(handle)
            handle.close()
            
            id_list = record["IdList"]
            logger.info(f"Found {len(id_list)} sequences")
            
            return id_list
            
        except Exception as e:
            logger.error(f"Error searching NCBI: {e}")
            raise
    
    def fetch_sequences(
        self,
        id_list: List[str],
        batch_size: int = 100
    ) -> List[SeqRecord]:
        """
        Fetch sequences in batches
        
        Args:
            id_list: List of GenBank IDs
            batch_size: Number of sequences per batch
            
        Returns:
            List of SeqRecord objects
        """
        sequences = []
        
        for i in tqdm(range(0, len(id_list), batch_size), desc="Downloading sequences"):
            batch_ids = id_list[i:i + batch_size]
            
            try:
                time.sleep(self.delay)  # Rate limiting
                
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
                logger.error(f"Error fetching batch {i}: {e}")
                continue
        
        logger.info(f"Downloaded {len(sequences)} sequences")
        return sequences
    
    def extract_taxonomy(self, record: SeqRecord) -> Dict:
        """
        Extract taxonomic information from GenBank record
        
        Args:
            record: SeqRecord object
            
        Returns:
            Dictionary with taxonomy information
        """
        taxonomy = {
            'organism': 'Unknown',
            'taxonomy': [],
            'taxon_id': None,
            'lineage': []
        }
        
        if 'organism' in record.annotations:
            taxonomy['organism'] = record.annotations['organism']
        
        if 'taxonomy' in record.annotations:
            taxonomy['taxonomy'] = record.annotations['taxonomy']
            taxonomy['lineage'] = record.annotations['taxonomy']
        
        # Extract taxon ID from features
        for feature in record.features:
            if feature.type == 'source':
                if 'db_xref' in feature.qualifiers:
                    for xref in feature.qualifiers['db_xref']:
                        if xref.startswith('taxon:'):
                            taxonomy['taxon_id'] = xref.split(':')[1]
        
        return taxonomy
    
    def organize_by_taxonomy(
        self,
        sequences: List[SeqRecord],
        output_dir: str,
        taxonomic_level: str = 'order'
    ) -> Dict:
        """
        Organize sequences by taxonomic classification
        
        Args:
            sequences: List of SeqRecord objects
            output_dir: Output directory
            taxonomic_level: Level to organize by (order, family, genus, species)
            
        Returns:
            Taxonomy mapping dictionary
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Group sequences by taxonomy
        taxonomy_groups = {}
        taxonomy_map = {}
        class_id = 0
        
        level_index = {
            'phylum': 0,
            'class': 1,
            'order': 2,
            'family': 3,
            'genus': 4,
            'species': 5
        }
        
        idx = level_index.get(taxonomic_level, 2)
        
        for record in tqdm(sequences, desc="Organizing sequences"):
            taxonomy = self.extract_taxonomy(record)
            
            # Get taxonomic group at specified level
            if len(taxonomy['taxonomy']) > idx:
                taxon = taxonomy['taxonomy'][idx]
            else:
                taxon = taxonomy['organism']
            
            if taxon not in taxonomy_groups:
                taxonomy_groups[taxon] = []
                taxonomy_map[str(class_id)] = {
                    'name': taxon,
                    'rank': taxonomic_level,
                    'lineage': taxonomy['taxonomy'],
                    'organism': taxonomy['organism']
                }
                class_id += 1
            
            taxonomy_groups[taxon].append(record)
        
        # Save sequences to files
        for class_id, (taxon, records) in enumerate(taxonomy_groups.items()):
            class_dir = os.path.join(output_dir, f"class_{class_id}")
            os.makedirs(class_dir, exist_ok=True)
            
            output_file = os.path.join(class_dir, "sequences.fasta")
            SeqIO.write(records, output_file, "fasta")
            
            logger.info(f"Saved {len(records)} sequences for {taxon}")
        
        # Save taxonomy mapping
        taxonomy_file = os.path.join(output_dir, "taxonomy.json")
        with open(taxonomy_file, 'w') as f:
            json.dump(taxonomy_map, f, indent=2)
        
        logger.info(f"Created {len(taxonomy_groups)} taxonomic classes")
        return taxonomy_map


def main():
    parser = argparse.ArgumentParser(description='Download eDNA sequences from NCBI')
    parser.add_argument('--email', type=str, required=True, help='Your email address')
    parser.add_argument('--api_key', type=str, help='NCBI API key (optional)')
    parser.add_argument('--query', type=str, required=True, help='NCBI search query')
    parser.add_argument('--output', type=str, default='./data/training', help='Output directory')
    parser.add_argument('--max_sequences', type=int, default=10000, help='Maximum sequences')
    parser.add_argument('--min_length', type=int, default=100, help='Minimum sequence length')
    parser.add_argument('--max_length', type=int, default=2000, help='Maximum sequence length')
    parser.add_argument('--taxonomic_level', type=str, default='order', 
                       choices=['phylum', 'class', 'order', 'family', 'genus', 'species'],
                       help='Taxonomic level for classification')
    
    args = parser.parse_args()
    
    # Initialize downloader
    downloader = NCBIDataDownloader(args.email, args.api_key)
    
    # Search for sequences
    id_list = downloader.search_sequences(
        query=args.query,
        max_sequences=args.max_sequences,
        min_length=args.min_length,
        max_length=args.max_length
    )
    
    if not id_list:
        logger.error("No sequences found")
        return
    
    # Fetch sequences
    sequences = downloader.fetch_sequences(id_list)
    
    if not sequences:
        logger.error("Failed to download sequences")
        return
    
    # Organize by taxonomy
    taxonomy_map = downloader.organize_by_taxonomy(
        sequences,
        args.output,
        args.taxonomic_level
    )
    
    logger.info(f"Download complete! Data saved to {args.output}")
    logger.info(f"Total sequences: {len(sequences)}")
    logger.info(f"Taxonomic classes: {len(taxonomy_map)}")


if __name__ == '__main__':
    main()
