"""
Test deep learning models
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import torch
from app.models.deep_learning import (
    DeepTaxaClassifier,
    NovelTaxaDetector,
    sequence_to_tensor,
    batch_sequences
)


def test_sequence_to_tensor():
    """Test sequence encoding"""
    sequence = "ACGTACGTACGT"
    tensor = sequence_to_tensor(sequence, max_length=20)
    
    assert tensor.shape == (20,)
    assert tensor.dtype == torch.long
    assert all(tensor[:12] > 0)  # First 12 should be encoded
    assert all(tensor[12:] == 0)  # Rest should be padding
    print("✓ Sequence to tensor conversion works")


def test_batch_sequences():
    """Test batch conversion"""
    sequences = ["ACGT", "TGCA", "GGCC"]
    batch = batch_sequences(sequences, max_length=10)
    
    assert batch.shape == (3, 10)
    print("✓ Batch sequence conversion works")


def test_classifier_forward():
    """Test classifier forward pass"""
    model = DeepTaxaClassifier(
        num_classes=5,
        embedding_dim=64,
        hidden_dim=128,
        num_conv_layers=2,
        dropout=0.3
    )
    
    # Create dummy input
    batch_size = 4
    seq_length = 100
    x = torch.randint(0, 5, (batch_size, seq_length))
    
    # Forward pass
    logits, confidence = model(x)
    
    assert logits.shape == (batch_size, 5)
    assert confidence.shape == (batch_size, 1)
    assert torch.all((confidence >= 0) & (confidence <= 1))
    print("✓ Classifier forward pass works")


def test_novelty_detector():
    """Test novelty detector"""
    model = NovelTaxaDetector(embedding_dim=64, latent_dim=32)
    
    # Create dummy input
    batch_size = 4
    embedding_dim = 64
    x = torch.randn(batch_size, embedding_dim)
    
    # Forward pass
    reconstructed, latent = model(x)
    
    assert reconstructed.shape == (batch_size, embedding_dim)
    assert latent.shape == (batch_size, 32)
    
    # Test novelty score
    novelty_scores = model.get_novelty_score(x)
    assert novelty_scores.shape == (batch_size,)
    assert torch.all(novelty_scores >= 0)
    print("✓ Novelty detector works")


def test_model_parameters():
    """Test model has trainable parameters"""
    model = DeepTaxaClassifier(num_classes=10)
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    assert total_params > 0
    assert trainable_params > 0
    assert total_params == trainable_params
    print(f"✓ Model has {total_params:,} trainable parameters")


if __name__ == '__main__':
    print("Testing Deep Learning Models...")
    print("=" * 50)
    
    test_sequence_to_tensor()
    test_batch_sequences()
    test_classifier_forward()
    test_novelty_detector()
    test_model_parameters()
    
    print("=" * 50)
    print("All tests passed! ✓")
