"""
Bioinformatics sequence processing and quality control
"""
import logging
from typing import List, Dict, Tuple
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
import numpy as np
from collections import Counter

logger = logging.getLogger(__name__)


class SequenceProcessor:
    """
    Process and quality-filter DNA sequences from FASTA/FASTQ files
    """
    
    def __init__(self, min_length: int = 100, max_length: int = 2000, min_quality: float = 20.0):
        self.min_length = min_length
        self.max_length = max_length
        self.min_quality = min_quality
        
    def parse_file(self, file_path: str) -> List[SeqRecord]:
        """
        Parse FASTA or FASTQ file
        """
        try:
            # Detect file format
            if file_path.endswith(('.fasta', '.fa', '.fna', '.fas')):
                format_type = 'fasta'
            elif file_path.endswith(('.fastq', '.fq')):
                format_type = 'fastq'
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            sequences = list(SeqIO.parse(file_path, format_type))
            logger.info(f"Parsed {len(sequences)} sequences from {file_path}")
            return sequences
            
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            raise
    
    def quality_filter(self, sequences: List[SeqRecord]) -> List[SeqRecord]:
        """
        Filter sequences based on quality criteria
        """
        filtered = []
        stats = {
            'total': len(sequences),
            'too_short': 0,
            'too_long': 0,
            'low_quality': 0,
            'passed': 0
        }
        
        for record in sequences:
            seq_len = len(record.seq)
            
            # Length filter
            if seq_len < self.min_length:
                stats['too_short'] += 1
                continue
            if seq_len > self.max_length:
                stats['too_long'] += 1
                continue
            
            # Quality filter (for FASTQ)
            if hasattr(record, 'letter_annotations') and 'phred_quality' in record.letter_annotations:
                avg_quality = np.mean(record.letter_annotations['phred_quality'])
                if avg_quality < self.min_quality:
                    stats['low_quality'] += 1
                    continue
            
            filtered.append(record)
            stats['passed'] += 1
        
        logger.info(f"Quality filtering: {stats}")
        return filtered
    
    def remove_adapters(self, sequences: List[SeqRecord], adapters: List[str] = None) -> List[SeqRecord]:
        """
        Remove adapter sequences (simplified version)
        """
        if not adapters:
            # Common Illumina adapters
            adapters = [
                "AGATCGGAAGAGC",  # TruSeq adapter
                "CTGTCTCTTATACACATCT",  # Nextera adapter
            ]
        
        cleaned = []
        for record in sequences:
            seq_str = str(record.seq)
            
            # Check for adapters
            for adapter in adapters:
                if adapter in seq_str:
                    # Trim at adapter position
                    pos = seq_str.index(adapter)
                    seq_str = seq_str[:pos]
            
            # Create new record with cleaned sequence
            if len(seq_str) >= self.min_length:
                new_record = SeqRecord(
                    Seq(seq_str),
                    id=record.id,
                    description=record.description
                )
                cleaned.append(new_record)
        
        logger.info(f"Adapter removal: {len(sequences)} -> {len(cleaned)} sequences")
        return cleaned
    
    def dereplicate(self, sequences: List[SeqRecord]) -> Tuple[List[SeqRecord], Dict[str, int]]:
        """
        Remove duplicate sequences and track abundance
        """
        seq_dict = {}
        abundance = {}
        
        for record in sequences:
            seq_str = str(record.seq)
            if seq_str not in seq_dict:
                seq_dict[seq_str] = record
                abundance[seq_str] = 1
            else:
                abundance[seq_str] += 1
        
        unique_sequences = list(seq_dict.values())
        logger.info(f"Dereplication: {len(sequences)} -> {len(unique_sequences)} unique sequences")
        
        return unique_sequences, abundance
    
    def calculate_gc_content(self, sequence: str) -> float:
        """Calculate GC content percentage"""
        gc_count = sequence.upper().count('G') + sequence.upper().count('C')
        return (gc_count / len(sequence)) * 100 if len(sequence) > 0 else 0
    
    def get_sequence_stats(self, sequences: List[SeqRecord]) -> Dict:
        """
        Calculate statistics for sequence dataset
        """
        lengths = [len(seq.seq) for seq in sequences]
        gc_contents = [self.calculate_gc_content(str(seq.seq)) for seq in sequences]
        
        # Base composition
        all_bases = ''.join([str(seq.seq) for seq in sequences])
        base_counts = Counter(all_bases.upper())
        
        stats = {
            'total_sequences': len(sequences),
            'total_bases': sum(lengths),
            'length': {
                'min': min(lengths) if lengths else 0,
                'max': max(lengths) if lengths else 0,
                'mean': np.mean(lengths) if lengths else 0,
                'median': np.median(lengths) if lengths else 0,
                'std': np.std(lengths) if lengths else 0,
            },
            'gc_content': {
                'min': min(gc_contents) if gc_contents else 0,
                'max': max(gc_contents) if gc_contents else 0,
                'mean': np.mean(gc_contents) if gc_contents else 0,
            },
            'base_composition': {
                'A': base_counts.get('A', 0),
                'C': base_counts.get('C', 0),
                'G': base_counts.get('G', 0),
                'T': base_counts.get('T', 0),
                'N': base_counts.get('N', 0),
            }
        }
        
        return stats
    
    def process_pipeline(self, file_path: str) -> Tuple[List[SeqRecord], Dict[str, int], Dict]:
        """
        Complete processing pipeline
        """
        logger.info(f"Starting processing pipeline for {file_path}")
        
        # Parse file
        sequences = self.parse_file(file_path)
        
        # Quality filtering
        sequences = self.quality_filter(sequences)
        
        # Remove adapters
        sequences = self.remove_adapters(sequences)
        
        # Dereplicate
        unique_sequences, abundance = self.dereplicate(sequences)
        
        # Calculate statistics
        stats = self.get_sequence_stats(unique_sequences)
        
        logger.info("Processing pipeline complete")
        return unique_sequences, abundance, stats


class TaxonomyMapper:
    """
    Map sequences to taxonomic classifications
    """
    
    def __init__(self, taxonomy_db_path: str = None):
        self.taxonomy_db = taxonomy_db_path
        self.rank_hierarchy = ['kingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']
    
    def get_lineage(self, taxon_id: str) -> List[str]:
        """
        Get full taxonomic lineage for a taxon
        In production, this would query NCBI Taxonomy or similar database
        """
        # Placeholder - would connect to real taxonomy database
        return []
    
    def assign_taxonomy(self, sequence: str, predictions: Dict) -> Dict:
        """
        Assign taxonomy based on model predictions
        """
        taxonomy = {
            'taxon_name': predictions.get('taxon_name', 'Unknown'),
            'taxon_id': predictions.get('taxon_id', None),
            'confidence': predictions.get('confidence', 0.0),
            'rank': predictions.get('rank', 'species'),
            'lineage': predictions.get('lineage', []),
            'is_novel': predictions.get('is_novel', False),
        }
        
        return taxonomy
    
    def calculate_diversity_indices(self, abundance_data: Dict[str, int]) -> Dict:
        """
        Calculate biodiversity indices
        """
        abundances = list(abundance_data.values())
        total = sum(abundances)
        
        if total == 0:
            return {
                'shannon': 0.0,
                'simpson': 0.0,
                'richness': 0,
                'evenness': 0.0
            }
        
        # Shannon diversity: H = -Σ(pi * ln(pi))
        proportions = [a / total for a in abundances]
        shannon = -sum(p * np.log(p) for p in proportions if p > 0)
        
        # Simpson diversity: D = 1 - Σ(pi^2)
        simpson = 1 - sum(p ** 2 for p in proportions)
        
        # Species richness
        richness = len(abundances)
        
        # Pielou's evenness: J = H / ln(S)
        evenness = shannon / np.log(richness) if richness > 1 else 0
        
        return {
            'shannon': float(shannon),
            'simpson': float(simpson),
            'richness': richness,
            'evenness': float(evenness)
        }
