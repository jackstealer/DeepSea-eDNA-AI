"""
Deep Learning Models for eDNA Sequence Classification
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple
import numpy as np


class DNAEmbedding(nn.Module):
    """
    DNA Sequence Embedding Layer
    Converts DNA sequences to numerical embeddings
    """
    def __init__(self, vocab_size: int = 5, embedding_dim: int = 128):
        super(DNAEmbedding, self).__init__()
        # A, C, G, T, N (unknown)
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        
    def forward(self, x):
        return self.embedding(x)


class ConvolutionalBlock(nn.Module):
    """
    Convolutional block for sequence feature extraction
    """
    def __init__(self, in_channels: int, out_channels: int, kernel_size: int = 3):
        super(ConvolutionalBlock, self).__init__()
        self.conv = nn.Conv1d(in_channels, out_channels, kernel_size, padding=kernel_size//2)
        self.bn = nn.BatchNorm1d(out_channels)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        x = self.relu(x)
        x = self.dropout(x)
        return x


class AttentionLayer(nn.Module):
    """
    Self-attention mechanism for sequence analysis
    """
    def __init__(self, hidden_dim: int):
        super(AttentionLayer, self).__init__()
        self.attention = nn.MultiheadAttention(hidden_dim, num_heads=8, batch_first=True)
        self.norm = nn.LayerNorm(hidden_dim)
        
    def forward(self, x):
        attn_output, _ = self.attention(x, x, x)
        return self.norm(x + attn_output)


class DeepTaxaClassifier(nn.Module):
    """
    Deep Learning Model for Taxonomic Classification
    Architecture: Embedding -> CNN -> Attention -> Classification
    """
    def __init__(
        self,
        num_classes: int,
        embedding_dim: int = 128,
        hidden_dim: int = 256,
        num_conv_layers: int = 3,
        dropout: float = 0.3
    ):
        super(DeepTaxaClassifier, self).__init__()
        
        # DNA Embedding
        self.embedding = DNAEmbedding(vocab_size=5, embedding_dim=embedding_dim)
        
        # Convolutional layers for local pattern extraction
        self.conv_layers = nn.ModuleList([
            ConvolutionalBlock(
                embedding_dim if i == 0 else hidden_dim,
                hidden_dim,
                kernel_size=3 + 2*i  # Increasing kernel sizes
            )
            for i in range(num_conv_layers)
        ])
        
        # Attention layers for long-range dependencies
        self.attention = AttentionLayer(hidden_dim)
        
        # Global pooling
        self.global_pool = nn.AdaptiveMaxPool1d(1)
        
        # Classification head
        self.classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim // 2, num_classes)
        )
        
        # Confidence estimation head
        self.confidence_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
        
    def forward(self, x):
        # Embedding: (batch, seq_len) -> (batch, seq_len, embedding_dim)
        x = self.embedding(x)
        
        # Transpose for Conv1d: (batch, embedding_dim, seq_len)
        x = x.transpose(1, 2)
        
        # Convolutional layers
        for conv in self.conv_layers:
            x = conv(x)
        
        # Transpose back for attention: (batch, seq_len, hidden_dim)
        x = x.transpose(1, 2)
        
        # Attention
        x = self.attention(x)
        
        # Transpose for pooling: (batch, hidden_dim, seq_len)
        x = x.transpose(1, 2)
        
        # Global pooling: (batch, hidden_dim, 1) -> (batch, hidden_dim)
        x = self.global_pool(x).squeeze(-1)
        
        # Classification
        logits = self.classifier(x)
        confidence = self.confidence_head(x)
        
        return logits, confidence


class NovelTaxaDetector(nn.Module):
    """
    Autoencoder-based model for detecting novel taxa
    Uses reconstruction error as novelty score
    """
    def __init__(self, embedding_dim: int = 128, latent_dim: int = 64):
        super(NovelTaxaDetector, self).__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(embedding_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, latent_dim)
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(128, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, embedding_dim)
        )
        
    def forward(self, x):
        latent = self.encoder(x)
        reconstructed = self.decoder(latent)
        return reconstructed, latent
    
    def get_novelty_score(self, x):
        """Calculate reconstruction error as novelty score"""
        reconstructed, _ = self.forward(x)
        mse = F.mse_loss(reconstructed, x, reduction='none').mean(dim=1)
        return mse


class EnsembleModel(nn.Module):
    """
    Ensemble of multiple models for robust predictions
    """
    def __init__(self, models: List[nn.Module], weights: List[float] = None):
        super(EnsembleModel, self).__init__()
        self.models = nn.ModuleList(models)
        self.weights = weights if weights else [1.0 / len(models)] * len(models)
        
    def forward(self, x):
        outputs = []
        confidences = []
        
        for model, weight in zip(self.models, self.weights):
            logits, conf = model(x)
            outputs.append(logits * weight)
            confidences.append(conf * weight)
        
        ensemble_logits = torch.stack(outputs).sum(dim=0)
        ensemble_confidence = torch.stack(confidences).mean(dim=0)
        
        return ensemble_logits, ensemble_confidence


def sequence_to_tensor(sequence: str, max_length: int = 1000) -> torch.Tensor:
    """
    Convert DNA sequence string to tensor
    A=1, C=2, G=3, T=4, N/other=0
    """
    mapping = {'A': 1, 'C': 2, 'G': 3, 'T': 4}
    
    # Convert to uppercase and map to integers
    encoded = [mapping.get(base.upper(), 0) for base in sequence]
    
    # Pad or truncate to max_length
    if len(encoded) < max_length:
        encoded += [0] * (max_length - len(encoded))
    else:
        encoded = encoded[:max_length]
    
    return torch.tensor(encoded, dtype=torch.long)


def batch_sequences(sequences: List[str], max_length: int = 1000) -> torch.Tensor:
    """Convert list of sequences to batched tensor"""
    tensors = [sequence_to_tensor(seq, max_length) for seq in sequences]
    return torch.stack(tensors)


class ModelTrainer:
    """
    Training utilities for deep learning models
    """
    def __init__(
        self,
        model: nn.Module,
        device: str = 'cpu',
        learning_rate: float = 0.001
    ):
        self.model = model.to(device)
        self.device = device
        self.optimizer = torch.optim.AdamW(model.parameters(), lr=learning_rate)
        self.scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', patience=5, factor=0.5
        )
        
    def train_epoch(self, dataloader, criterion):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_sequences, batch_labels in dataloader:
            batch_sequences = batch_sequences.to(self.device)
            batch_labels = batch_labels.to(self.device)
            
            self.optimizer.zero_grad()
            
            logits, confidence = self.model(batch_sequences)
            loss = criterion(logits, batch_labels)
            
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(logits, 1)
            total += batch_labels.size(0)
            correct += (predicted == batch_labels).sum().item()
        
        accuracy = 100 * correct / total
        avg_loss = total_loss / len(dataloader)
        
        return avg_loss, accuracy
    
    def validate(self, dataloader, criterion):
        """Validate the model"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch_sequences, batch_labels in dataloader:
                batch_sequences = batch_sequences.to(self.device)
                batch_labels = batch_labels.to(self.device)
                
                logits, confidence = self.model(batch_sequences)
                loss = criterion(logits, batch_labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(logits, 1)
                total += batch_labels.size(0)
                correct += (predicted == batch_labels).sum().item()
        
        accuracy = 100 * correct / total
        avg_loss = total_loss / len(dataloader)
        
        return avg_loss, accuracy
    
    def save_checkpoint(self, path: str, epoch: int, loss: float):
        """Save model checkpoint"""
        torch.save({
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'loss': loss,
        }, path)
    
    def load_checkpoint(self, path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        return checkpoint['epoch'], checkpoint['loss']
