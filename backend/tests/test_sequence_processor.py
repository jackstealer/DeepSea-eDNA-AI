"""
Test sequence processing
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq
from app.services.sequence_processor import SequenceProcessor, TaxonomyMapper


def test_quality_filter():
    """Test quality filtering"""
    processor = SequenceProcessor(min_length=100, max_length=500)
    
    # Create test sequences
    sequences = [
        SeqRecord(Seq("A" * 50), id="short"),  # Too short
        SeqRecord(Seq("A" * 200), id="good"),  # Good
        SeqRecord(Seq("A" * 600), id="long"),  # Too long
        SeqRecord(Seq("A" * 150), id="good2"), # Good
    ]
    
    filtered = processor.quality_filter(sequences)
    
    assert len(filtered) == 2
    assert all(100 <= len(seq.seq) <= 500 for seq in filtered)
    print("✓ Quality filtering works")


def test_dereplicate():
    """Test dereplication"""
    processor = SequenceProcessor()
    
    # Create sequences with duplicates
    sequences = [
        SeqRecord(Seq("ACGT"), id="seq1"),
        SeqRecord(Seq("ACGT"), id="seq2"),  # Duplicate
        SeqRecord(Seq("TGCA"), id="seq3"),
        SeqRecord(Seq("ACGT"), id="seq4"),  # Duplicate
    ]
    
    unique, abundance = processor.dereplicate(sequences)
    
    assert len(unique) == 2
    assert abundance["ACGT"] == 3
    assert abundance["TGCA"] == 1
    print("✓ Dereplication works")


def test_gc_content():
    """Test GC content calculation"""
    processor = SequenceProcessor()
    
    # 50% GC content
    seq1 = "ACGT"
    gc1 = processor.calculate_gc_content(seq1)
    assert gc1 == 50.0
    
    # 100% GC content
    seq2 = "GGCC"
    gc2 = processor.calculate_gc_content(seq2)
    assert gc2 == 100.0
    
    # 0% GC content
    seq3 = "AATT"
    gc3 = processor.calculate_gc_content(seq3)
    assert gc3 == 0.0
    
    print("✓ GC content calculation works")


def test_sequence_stats():
    """Test sequence statistics"""
    processor = SequenceProcessor()
    
    sequences = [
        SeqRecord(Seq("ACGT" * 25), id="seq1"),  # 100 bp
        SeqRecord(Seq("TGCA" * 50), id="seq2"),  # 200 bp
        SeqRecord(Seq("GGCC" * 37), id="seq3"),  # 148 bp
    ]
    
    stats = processor.get_sequence_stats(sequences)
    
    assert stats['total_sequences'] == 3
    assert stats['length']['min'] == 100
    assert stats['length']['max'] == 200
    assert 'base_composition' in stats
    print("✓ Sequence statistics calculation works")


def test_diversity_indices():
    """Test diversity index calculation"""
    mapper = TaxonomyMapper()
    
    # Test data
    abundance = {
        'Species A': 100,
        'Species B': 50,
        'Species C': 25,
        'Species D': 25
    }
    
    indices = mapper.calculate_diversity_indices(abundance)
    
    assert 'shannon' in indices
    assert 'simpson' in indices
    assert 'richness' in indices
    assert 'evenness' in indices
    
    assert indices['richness'] == 4
    assert 0 <= indices['simpson'] <= 1
    assert indices['shannon'] > 0
    
    print("✓ Diversity indices calculation works")
    print(f"  Shannon: {indices['shannon']:.3f}")
    print(f"  Simpson: {indices['simpson']:.3f}")
    print(f"  Richness: {indices['richness']}")
    print(f"  Evenness: {indices['evenness']:.3f}")


if __name__ == '__main__':
    print("Testing Sequence Processing...")
    print("=" * 50)
    
    test_quality_filter()
    test_dereplicate()
    test_gc_content()
    test_sequence_stats()
    test_diversity_indices()
    
    print("=" * 50)
    print("All tests passed! ✓")
