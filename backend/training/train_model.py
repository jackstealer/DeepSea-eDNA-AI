"""
Advanced Training Script for Deep Learning eDNA Classification Model
With Hyperparameter Tuning and Regularization
"""
import os
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Tuple, Dict
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split, WeightedRandomSampler
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts, ReduceLROnPlateau
import numpy as np
from tqdm import tqdm
import json
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, f1_score
import optuna
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.models.deep_learning import (
    DeepTaxaClassifier,
    NovelTaxaDetector,
    ModelTrainer,
    sequence_to_tensor
)
from app.services.sequence_processor import SequenceProcessor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class eDNADataset(Dataset):
    """
    PyTorch Dataset for eDNA sequences with data augmentation
    """
    def __init__(
        self,
        sequences: List[str],
        labels: List[int],
        max_length: int = 1000,
        augment: bool = False
    ):
        self.sequences = sequences
        self.labels = labels
        self.max_length = max_length
        self.augment = augment
        
    def __len__(self):
        return len(self.sequences)
    
    def augment_sequence(self, sequence: str) -> str:
        """
        Data augmentation for DNA sequences
        - Reverse complement
        - Random mutations (low probability)
        """
        if not self.augment or np.random.random() > 0.5:
            return sequence
        
        # Reverse complement
        if np.random.random() > 0.5:
            complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C', 'N': 'N'}
            sequence = ''.join([complement.get(base, 'N') for base in sequence[::-1]])
        
        # Random mutations (1% probability per base)
        if np.random.random() > 0.7:
            seq_list = list(sequence)
            num_mutations = max(1, int(len(seq_list) * 0.01))
            positions = np.random.choice(len(seq_list), num_mutations, replace=False)
            bases = ['A', 'C', 'G', 'T']
            for pos in positions:
                seq_list[pos] = np.random.choice(bases)
            sequence = ''.join(seq_list)
        
        return sequence
    
    def __getitem__(self, idx):
        sequence = self.sequences[idx]
        label = self.labels[idx]
        
        # Apply augmentation
        if self.augment:
            sequence = self.augment_sequence(sequence)
        
        # Convert sequence to tensor
        seq_tensor = sequence_to_tensor(sequence, self.max_length)
        label_tensor = torch.tensor(label, dtype=torch.long)
        
        return seq_tensor, label_tensor


def load_training_data(data_dir: str) -> Tuple[List[str], List[int], dict]:
    """
    Load training data from directory
    Expected format:
    - data_dir/
      - class_0/
        - sequences.fasta
      - class_1/
        - sequences.fasta
      - taxonomy.json (mapping of class IDs to taxonomy)
    """
    sequences = []
    labels = []
    taxonomy_map = {}
    
    # Load taxonomy mapping
    taxonomy_file = os.path.join(data_dir, 'taxonomy.json')
    if os.path.exists(taxonomy_file):
        with open(taxonomy_file, 'r') as f:
            taxonomy_map = json.load(f)
    
    # Load sequences from each class directory
    processor = SequenceProcessor()
    
    for class_dir in sorted(Path(data_dir).iterdir()):
        if not class_dir.is_dir() or class_dir.name.startswith('.'):
            continue
        
        try:
            class_id = int(class_dir.name.split('_')[1])
        except (ValueError, IndexError):
            logger.warning(f"Skipping directory {class_dir.name} - invalid format")
            continue
        
        # Find FASTA files in class directory
        for fasta_file in class_dir.glob('*.fasta'):
            try:
                records = processor.parse_file(str(fasta_file))
                for record in records:
                    sequences.append(str(record.seq))
                    labels.append(class_id)
            except Exception as e:
                logger.error(f"Error loading {fasta_file}: {e}")
    
    logger.info(f"Loaded {len(sequences)} sequences from {len(set(labels))} classes")
    return sequences, labels, taxonomy_map


def create_balanced_sampler(labels: List[int]) -> WeightedRandomSampler:
    """
    Create weighted sampler to handle class imbalance
    """
    class_counts = Counter(labels)
    class_weights = {cls: 1.0 / count for cls, count in class_counts.items()}
    sample_weights = [class_weights[label] for label in labels]
    
    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )
    
    return sampler


def calculate_class_weights(labels: List[int], device: str) -> torch.Tensor:
    """
    Calculate class weights for imbalanced datasets
    """
    class_counts = Counter(labels)
    total = len(labels)
    num_classes = len(class_counts)
    
    weights = torch.zeros(num_classes)
    for cls, count in class_counts.items():
        weights[cls] = total / (num_classes * count)
    
    return weights.to(device)


class EarlyStopping:
    """
    Early stopping to prevent overfitting
    """
    def __init__(self, patience: int = 10, min_delta: float = 0.0001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
        
    def __call__(self, val_loss: float) -> bool:
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0
        
        return self.early_stop


def evaluate_model(
    model: nn.Module,
    dataloader: DataLoader,
    device: str
) -> Dict:
    """
    Comprehensive model evaluation
    """
    model.eval()
    all_preds = []
    all_labels = []
    all_confidences = []
    
    with torch.no_grad():
        for batch_sequences, batch_labels in dataloader:
            batch_sequences = batch_sequences.to(device)
            batch_labels = batch_labels.to(device)
            
            logits, confidence = model(batch_sequences)
            _, predicted = torch.max(logits, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(batch_labels.cpu().numpy())
            all_confidences.extend(confidence.cpu().numpy())
    
    # Calculate metrics
    f1 = f1_score(all_labels, all_preds, average='weighted')
    
    # Classification report
    report = classification_report(
        all_labels,
        all_preds,
        output_dict=True,
        zero_division=0
    )
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    
    return {
        'f1_score': f1,
        'classification_report': report,
        'confusion_matrix': cm.tolist(),
        'predictions': all_preds,
        'labels': all_labels,
        'confidences': all_confidences
    }


def plot_training_history(history: Dict, output_dir: str):
    """
    Plot training curves
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Loss curves
    axes[0, 0].plot(history['train_loss'], label='Train Loss')
    axes[0, 0].plot(history['val_loss'], label='Val Loss')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].set_title('Training and Validation Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Accuracy curves
    axes[0, 1].plot(history['train_acc'], label='Train Acc')
    axes[0, 1].plot(history['val_acc'], label='Val Acc')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Accuracy (%)')
    axes[0, 1].set_title('Training and Validation Accuracy')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # F1 Score
    if 'val_f1' in history:
        axes[1, 0].plot(history['val_f1'], label='Val F1')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('F1 Score')
        axes[1, 0].set_title('Validation F1 Score')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
    
    # Learning rate
    if 'learning_rate' in history:
        axes[1, 1].plot(history['learning_rate'])
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Learning Rate')
        axes[1, 1].set_title('Learning Rate Schedule')
        axes[1, 1].set_yscale('log')
        axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'training_curves.png'), dpi=300)
    plt.close()


def plot_confusion_matrix(cm: np.ndarray, output_dir: str, class_names: List[str] = None):
    """
    Plot confusion matrix
    """
    plt.figure(figsize=(10, 8))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=class_names if class_names else range(len(cm)),
        yticklabels=class_names if class_names else range(len(cm))
    )
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=300)
    plt.close()


def train_classifier(
    data_dir: str,
    output_dir: str,
    epochs: int = 50,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    device: str = 'cpu',
    validation_split: float = 0.2,
    use_augmentation: bool = True,
    use_class_weights: bool = True,
    early_stopping_patience: int = 15,
    tune_hyperparameters: bool = False,
    use_cross_validation: bool = False,
    n_folds: int = 5
):
    """
    Train the taxonomic classifier with advanced techniques
    
    Features:
    - Data augmentation
    - Class imbalance handling
    - Early stopping
    - Learning rate scheduling
    - Dropout regularization
    - Weight decay (L2 regularization)
    - Gradient clipping
    - Model checkpointing
    - Comprehensive evaluation
    """
    logger.info("=" * 80)
    logger.info("Starting Advanced Model Training")
    logger.info("=" * 80)
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Load data
    logger.info("Loading training data...")
    sequences, labels, taxonomy_map = load_training_data(data_dir)
    num_classes = len(set(labels))
    
    logger.info(f"Dataset Statistics:")
    logger.info(f"  Total sequences: {len(sequences)}")
    logger.info(f"  Number of classes: {num_classes}")
    logger.info(f"  Sequence length range: {min(len(s) for s in sequences)}-{max(len(s) for s in sequences)}")
    
    # Class distribution
    class_counts = Counter(labels)
    logger.info(f"  Class distribution:")
    for cls, count in sorted(class_counts.items()):
        logger.info(f"    Class {cls}: {count} sequences ({count/len(labels)*100:.1f}%)")
    
    # Hyperparameter tuning
    if tune_hyperparameters:
        logger.info("\nPerforming hyperparameter tuning...")
        best_params = hyperparameter_tuning(
            sequences,
            labels,
            n_trials=50,
            device=device
        )
        
        # Update parameters
        embedding_dim = best_params['embedding_dim']
        hidden_dim = best_params['hidden_dim']
        num_conv_layers = best_params['num_conv_layers']
        dropout = best_params['dropout']
        learning_rate = best_params['learning_rate']
        batch_size = best_params['batch_size']
        weight_decay = best_params['weight_decay']
        
        # Save best parameters
        with open(os.path.join(output_dir, 'best_hyperparameters.json'), 'w') as f:
            json.dump(best_params, f, indent=2)
    else:
        # Default hyperparameters
        embedding_dim = 128
        hidden_dim = 256
        num_conv_layers = 3
        dropout = 0.3
        weight_decay = 1e-4
    
    # Cross-validation
    if use_cross_validation:
        logger.info(f"\nPerforming {n_folds}-fold cross-validation...")
        cv_results = train_with_cross_validation(
            sequences,
            labels,
            output_dir,
            n_folds=n_folds,
            epochs=epochs,
            batch_size=batch_size,
            learning_rate=learning_rate,
            device=device
        )
        return cv_results
    
    # Create dataset with augmentation
    logger.info(f"\nCreating datasets (augmentation: {use_augmentation})...")
    dataset = eDNADataset(sequences, labels, augment=use_augmentation)
    
    # Split into train and validation
    val_size = int(len(dataset) * validation_split)
    train_size = len(dataset) - val_size
    train_dataset, val_dataset = random_split(
        dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(42)
    )
    
    logger.info(f"  Training samples: {train_size}")
    logger.info(f"  Validation samples: {val_size}")
    
    # Create dataloaders with balanced sampling
    if use_class_weights:
        train_labels_subset = [labels[i] for i in train_dataset.indices]
        sampler = create_balanced_sampler(train_labels_subset)
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            sampler=sampler,
            num_workers=0,
            pin_memory=True if device == 'cuda' else False
        )
    else:
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=0,
            pin_memory=True if device == 'cuda' else False
        )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
        pin_memory=True if device == 'cuda' else False
    )
    
    # Initialize model
    logger.info(f"\nInitializing model...")
    logger.info(f"  Embedding dim: {embedding_dim}")
    logger.info(f"  Hidden dim: {hidden_dim}")
    logger.info(f"  Conv layers: {num_conv_layers}")
    logger.info(f"  Dropout: {dropout}")
    logger.info(f"  Device: {device}")
    
    model = DeepTaxaClassifier(
        num_classes=num_classes,
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        num_conv_layers=num_conv_layers,
        dropout=dropout
    ).to(device)
    
    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"  Total parameters: {total_params:,}")
    logger.info(f"  Trainable parameters: {trainable_params:,}")
    
    # Optimizer with weight decay (L2 regularization)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=learning_rate,
        weight_decay=weight_decay,
        betas=(0.9, 0.999)
    )
    
    # Learning rate scheduler
    scheduler = CosineAnnealingWarmRestarts(
        optimizer,
        T_0=10,
        T_mult=2,
        eta_min=1e-6
    )
    
    # Loss function with class weights
    if use_class_weights:
        class_weights = calculate_class_weights(labels, device)
        criterion = nn.CrossEntropyLoss(weight=class_weights, label_smoothing=0.1)
        logger.info(f"  Using weighted loss with label smoothing")
    else:
        criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    
    # Early stopping
    early_stopping = EarlyStopping(patience=early_stopping_patience, min_delta=0.0001)
    
    # Training loop
    logger.info(f"\nStarting training for {epochs} epochs...")
    logger.info("=" * 80)
    
    best_val_loss = float('inf')
    best_val_f1 = 0.0
    train_history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': [],
        'val_f1': [],
        'learning_rate': []
    }
    
    for epoch in range(epochs):
        logger.info(f"\nEpoch {epoch + 1}/{epochs}")
        logger.info("-" * 80)
        
        # Training phase
        model.train()
        train_loss = 0
        train_correct = 0
        train_total = 0
        
        train_pbar = tqdm(train_loader, desc="Training")
        for batch_sequences, batch_labels in train_pbar:
            batch_sequences = batch_sequences.to(device)
            batch_labels = batch_labels.to(device)
            
            optimizer.zero_grad()
            
            logits, confidence = model(batch_sequences)
            loss = criterion(logits, batch_labels)
            
            loss.backward()
            
            # Gradient clipping to prevent exploding gradients
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            
            train_loss += loss.item()
            _, predicted = torch.max(logits, 1)
            train_total += batch_labels.size(0)
            train_correct += (predicted == batch_labels).sum().item()
            
            # Update progress bar
            train_pbar.set_postfix({
                'loss': f'{loss.item():.4f}',
                'acc': f'{100 * train_correct / train_total:.2f}%'
            })
        
        train_loss /= len(train_loader)
        train_acc = 100 * train_correct / train_total
        
        # Validation phase
        model.eval()
        val_loss = 0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for batch_sequences, batch_labels in tqdm(val_loader, desc="Validation"):
                batch_sequences = batch_sequences.to(device)
                batch_labels = batch_labels.to(device)
                
                logits, confidence = model(batch_sequences)
                loss = criterion(logits, batch_labels)
                
                val_loss += loss.item()
                _, predicted = torch.max(logits, 1)
                val_total += batch_labels.size(0)
                val_correct += (predicted == batch_labels).sum().item()
        
        val_loss /= len(val_loader)
        val_acc = 100 * val_correct / val_total
        
        # Comprehensive evaluation
        eval_results = evaluate_model(model, val_loader, device)
        val_f1 = eval_results['f1_score']
        
        # Update learning rate
        scheduler.step()
        current_lr = optimizer.param_groups[0]['lr']
        
        # Save history
        train_history['train_loss'].append(train_loss)
        train_history['train_acc'].append(train_acc)
        train_history['val_loss'].append(val_loss)
        train_history['val_acc'].append(val_acc)
        train_history['val_f1'].append(val_f1)
        train_history['learning_rate'].append(current_lr)
        
        # Log metrics
        logger.info(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
        logger.info(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}% | Val F1: {val_f1:.4f}")
        logger.info(f"Learning Rate: {current_lr:.6f}")
        
        # Save best model based on F1 score
        if val_f1 > best_val_f1:
            best_val_f1 = val_f1
            best_val_loss = val_loss
            checkpoint_path = os.path.join(output_dir, 'best_model.pth')
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_acc': val_acc,
                'val_f1': val_f1,
                'hyperparameters': {
                    'embedding_dim': embedding_dim,
                    'hidden_dim': hidden_dim,
                    'num_conv_layers': num_conv_layers,
                    'dropout': dropout
                }
            }, checkpoint_path)
            logger.info(f"✓ Saved best model (F1: {val_f1:.4f})")
        
        # Early stopping check
        if early_stopping(val_loss):
            logger.info(f"\nEarly stopping triggered after {epoch + 1} epochs")
            break
        
        # Save checkpoint every 10 epochs
        if (epoch + 1) % 10 == 0:
            checkpoint_path = os.path.join(output_dir, f'checkpoint_epoch_{epoch+1}.pth')
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
            }, checkpoint_path)
    
    # Final evaluation
    logger.info("\n" + "=" * 80)
    logger.info("Training Complete!")
    logger.info("=" * 80)
    logger.info(f"Best Validation Loss: {best_val_loss:.4f}")
    logger.info(f"Best Validation F1: {best_val_f1:.4f}")
    
    # Load best model for final evaluation
    checkpoint = torch.load(os.path.join(output_dir, 'best_model.pth'))
    model.load_state_dict(checkpoint['model_state_dict'])
    
    final_eval = evaluate_model(model, val_loader, device)
    
    # Save results
    results = {
        'best_val_loss': best_val_loss,
        'best_val_f1': best_val_f1,
        'final_evaluation': {
            'f1_score': final_eval['f1_score'],
            'classification_report': final_eval['classification_report']
        },
        'training_history': train_history,
        'hyperparameters': {
            'embedding_dim': embedding_dim,
            'hidden_dim': hidden_dim,
            'num_conv_layers': num_conv_layers,
            'dropout': dropout,
            'learning_rate': learning_rate,
            'weight_decay': weight_decay,
            'batch_size': batch_size
        }
    }
    
    # Save results
    with open(os.path.join(output_dir, 'training_results.json'), 'w') as f:
        json.dump(results, f, indent=2)
    
    # Save training history
    with open(os.path.join(output_dir, 'training_history.json'), 'w') as f:
        json.dump(train_history, f, indent=2)
    
    # Save taxonomy mapping
    with open(os.path.join(output_dir, 'taxonomy_map.json'), 'w') as f:
        json.dump(taxonomy_map, f, indent=2)
    
    # Save model config
    config = {
        'num_classes': num_classes,
        'embedding_dim': embedding_dim,
        'hidden_dim': hidden_dim,
        'num_conv_layers': num_conv_layers,
        'dropout': dropout,
        'max_sequence_length': 1000,
    }
    with open(os.path.join(output_dir, 'model_config.json'), 'w') as f:
        json.dump(config, f, indent=2)
    
    # Plot training curves
    plot_training_history(train_history, output_dir)
    
    # Plot confusion matrix
    plot_confusion_matrix(
        np.array(final_eval['confusion_matrix']),
        output_dir,
        class_names=[taxonomy_map[str(i)]['name'] for i in range(num_classes)]
    )
    
    logger.info(f"\nAll results saved to {output_dir}")
    
    return results


def train_novelty_detector(
    data_dir: str,
    output_dir: str,
    epochs: int = 30,
    batch_size: int = 32,
    learning_rate: float = 0.001,
    device: str = 'cpu'
):
    """
    Train the novelty detection autoencoder
    """
    logger.info("Training novelty detector...")
    
    # Load known sequences (no labels needed)
    sequences, _, _ = load_training_data(data_dir)
    
    # Create dataset (use dummy labels)
    dataset = eDNADataset(sequences, [0] * len(sequences))
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True, num_workers=0)
    
    # Initialize model
    model = NovelTaxaDetector(embedding_dim=128, latent_dim=64).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    criterion = nn.MSELoss()
    
    # Training loop
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for batch_sequences, _ in tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}"):
            batch_sequences = batch_sequences.to(device)
            
            # Get embeddings (simplified - in practice would use pre-trained embeddings)
            embeddings = batch_sequences.float()
            
            optimizer.zero_grad()
            reconstructed, _ = model(embeddings)
            loss = criterion(reconstructed, embeddings)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
        
        avg_loss = total_loss / len(dataloader)
        logger.info(f"Epoch {epoch+1}, Loss: {avg_loss:.4f}")
    
    # Save model
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, 'novelty_detector.pth')
    torch.save(model.state_dict(), model_path)
    logger.info(f"Novelty detector saved to {model_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Train eDNA Classification Models with Advanced Techniques',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Data arguments
    parser.add_argument('--data_dir', type=str, required=True,
                       help='Training data directory')
    parser.add_argument('--output_dir', type=str, default='./ml_models',
                       help='Output directory for models')
    
    # Training arguments
    parser.add_argument('--epochs', type=int, default=100,
                       help='Number of training epochs')
    parser.add_argument('--batch_size', type=int, default=32,
                       help='Batch size for training')
    parser.add_argument('--lr', type=float, default=0.001,
                       help='Initial learning rate')
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu',
                       help='Device (cpu or cuda)')
    parser.add_argument('--val_split', type=float, default=0.2,
                       help='Validation split ratio')
    
    # Regularization arguments
    parser.add_argument('--augmentation', action='store_true', default=True,
                       help='Use data augmentation')
    parser.add_argument('--class_weights', action='store_true', default=True,
                       help='Use class weights for imbalanced data')
    parser.add_argument('--early_stopping', type=int, default=15,
                       help='Early stopping patience (epochs)')
    
    # Advanced options
    parser.add_argument('--tune_hyperparameters', action='store_true',
                       help='Perform hyperparameter tuning with Optuna')
    parser.add_argument('--cross_validation', action='store_true',
                       help='Use k-fold cross-validation')
    parser.add_argument('--n_folds', type=int, default=5,
                       help='Number of folds for cross-validation')
    parser.add_argument('--train_novelty', action='store_true',
                       help='Also train novelty detector')
    
    args = parser.parse_args()
    
    # Log configuration
    logger.info("Configuration:")
    for arg, value in vars(args).items():
        logger.info(f"  {arg}: {value}")
    
    # Train classifier
    results = train_classifier(
        data_dir=args.data_dir,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        device=args.device,
        validation_split=args.val_split,
        use_augmentation=args.augmentation,
        use_class_weights=args.class_weights,
        early_stopping_patience=args.early_stopping,
        tune_hyperparameters=args.tune_hyperparameters,
        use_cross_validation=args.cross_validation,
        n_folds=args.n_folds
    )
    
    # Train novelty detector if requested
    if args.train_novelty:
        logger.info("\n" + "=" * 80)
        logger.info("Training Novelty Detector")
        logger.info("=" * 80)
        novelty_output = os.path.join(args.output_dir, 'novelty')
        train_novelty_detector(
            data_dir=args.data_dir,
            output_dir=novelty_output,
            epochs=30,
            batch_size=args.batch_size,
            learning_rate=args.lr,
            device=args.device
        )
    
    logger.info("\n" + "=" * 80)
    logger.info("All Training Complete!")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()



def create_balanced_sampler(labels: List[int]) -> WeightedRandomSampler:
    """
    Create weighted sampler to handle class imbalance
    """
    class_counts = Counter(labels)
    class_weights = {cls: 1.0 / count for cls, count in class_counts.items()}
    sample_weights = [class_weights[label] for label in labels]
    
    sampler = WeightedRandomSampler(
        weights=sample_weights,
        num_samples=len(sample_weights),
        replacement=True
    )
    
    return sampler


def calculate_class_weights(labels: List[int], device: str) -> torch.Tensor:
    """
    Calculate class weights for imbalanced datasets
    """
    class_counts = Counter(labels)
    total = len(labels)
    num_classes = len(class_counts)
    
    weights = torch.zeros(num_classes)
    for cls, count in class_counts.items():
        weights[cls] = total / (num_classes * count)
    
    return weights.to(device)


class EarlyStopping:
    """
    Early stopping to prevent overfitting
    """
    def __init__(self, patience: int = 10, min_delta: float = 0.0001):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
        
    def __call__(self, val_loss: float) -> bool:
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0
        
        return self.early_stop


def evaluate_model(
    model: nn.Module,
    dataloader: DataLoader,
    device: str
) -> Dict:
    """
    Comprehensive model evaluation
    """
    model.eval()
    all_preds = []
    all_labels = []
    all_confidences = []
    
    with torch.no_grad():
        for batch_sequences, batch_labels in dataloader:
            batch_sequences = batch_sequences.to(device)
            batch_labels = batch_labels.to(device)
            
            logits, confidence = model(batch_sequences)
            _, predicted = torch.max(logits, 1)
            
            all_preds.extend(predicted.cpu().numpy())
            all_labels.extend(batch_labels.cpu().numpy())
            all_confidences.extend(confidence.cpu().numpy())
    
    # Calculate metrics
    f1 = f1_score(all_labels, all_preds, average='weighted')
    
    # Classification report
    report = classification_report(
        all_labels,
        all_preds,
        output_dict=True,
        zero_division=0
    )
    
    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds)
    
    return {
        'f1_score': f1,
        'classification_report': report,
        'confusion_matrix': cm.tolist(),
        'predictions': all_preds,
        'labels': all_labels,
        'confidences': all_confidences
    }


def plot_training_history(history: Dict, output_dir: str):
    """
    Plot training curves
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # Loss curves
    axes[0, 0].plot(history['train_loss'], label='Train Loss')
    axes[0, 0].plot(history['val_loss'], label='Val Loss')
    axes[0, 0].set_xlabel('Epoch')
    axes[0, 0].set_ylabel('Loss')
    axes[0, 0].set_title('Training and Validation Loss')
    axes[0, 0].legend()
    axes[0, 0].grid(True)
    
    # Accuracy curves
    axes[0, 1].plot(history['train_acc'], label='Train Acc')
    axes[0, 1].plot(history['val_acc'], label='Val Acc')
    axes[0, 1].set_xlabel('Epoch')
    axes[0, 1].set_ylabel('Accuracy (%)')
    axes[0, 1].set_title('Training and Validation Accuracy')
    axes[0, 1].legend()
    axes[0, 1].grid(True)
    
    # F1 Score
    if 'val_f1' in history:
        axes[1, 0].plot(history['val_f1'], label='Val F1')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('F1 Score')
        axes[1, 0].set_title('Validation F1 Score')
        axes[1, 0].legend()
        axes[1, 0].grid(True)
    
    # Learning rate
    if 'learning_rate' in history:
        axes[1, 1].plot(history['learning_rate'])
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Learning Rate')
        axes[1, 1].set_title('Learning Rate Schedule')
        axes[1, 1].set_yscale('log')
        axes[1, 1].grid(True)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'training_curves.png'), dpi=300)
    plt.close()


def plot_confusion_matrix(cm: np.ndarray, output_dir: str, class_names: List[str] = None):
    """
    Plot confusion matrix
    """
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=class_names if class_names else range(len(cm)),
        yticklabels=class_names if class_names else range(len(cm))
    )
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'confusion_matrix.png'), dpi=300)
    plt.close()


def hyperparameter_tuning(
    sequences: List[str],
    labels: List[int],
    n_trials: int = 50,
    device: str = 'cpu'
) -> Dict:
    """
    Hyperparameter tuning using Optuna
    """
    def objective(trial):
        # Hyperparameters to tune
        embedding_dim = trial.suggest_categorical('embedding_dim', [64, 128, 256])
        hidden_dim = trial.suggest_categorical('hidden_dim', [128, 256, 512])
        num_conv_layers = trial.suggest_int('num_conv_layers', 2, 4)
        dropout = trial.suggest_float('dropout', 0.1, 0.5)
        learning_rate = trial.suggest_loguniform('learning_rate', 1e-5, 1e-2)
        batch_size = trial.suggest_categorical('batch_size', [16, 32, 64])
        weight_decay = trial.suggest_loguniform('weight_decay', 1e-6, 1e-3)
        
        # Create dataset
        dataset = eDNADataset(sequences, labels, augment=True)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
        
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
        
        # Create model
        num_classes = len(set(labels))
        model = DeepTaxaClassifier(
            num_classes=num_classes,
            embedding_dim=embedding_dim,
            hidden_dim=hidden_dim,
            num_conv_layers=num_conv_layers,
            dropout=dropout
        ).to(device)
        
        # Optimizer with weight decay (L2 regularization)
        optimizer = torch.optim.AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay
        )
        
        # Loss with class weights
        class_weights = calculate_class_weights(labels, device)
        criterion = nn.CrossEntropyLoss(weight=class_weights)
        
        # Train for a few epochs
        num_epochs = 10
        best_val_loss = float('inf')
        
        for epoch in range(num_epochs):
            model.train()
            for batch_sequences, batch_labels in train_loader:
                batch_sequences = batch_sequences.to(device)
                batch_labels = batch_labels.to(device)
                
                optimizer.zero_grad()
                logits, _ = model(batch_sequences)
                loss = criterion(logits, batch_labels)
                loss.backward()
                optimizer.step()
            
            # Validation
            model.eval()
            val_loss = 0
            with torch.no_grad():
                for batch_sequences, batch_labels in val_loader:
                    batch_sequences = batch_sequences.to(device)
                    batch_labels = batch_labels.to(device)
                    logits, _ = model(batch_sequences)
                    loss = criterion(logits, batch_labels)
                    val_loss += loss.item()
            
            val_loss /= len(val_loader)
            best_val_loss = min(best_val_loss, val_loss)
            
            # Report intermediate value
            trial.report(val_loss, epoch)
            
            # Pruning
            if trial.should_prune():
                raise optuna.TrialPruned()
        
        return best_val_loss
    
    # Create study
    study = optuna.create_study(
        direction='minimize',
        pruner=optuna.pruners.MedianPruner()
    )
    
    logger.info(f"Starting hyperparameter tuning with {n_trials} trials...")
    study.optimize(objective, n_trials=n_trials, show_progress_bar=True)
    
    logger.info("Best hyperparameters:")
    for key, value in study.best_params.items():
        logger.info(f"  {key}: {value}")
    
    return study.best_params


def train_with_cross_validation(
    sequences: List[str],
    labels: List[int],
    output_dir: str,
    n_folds: int = 5,
    **kwargs
) -> Dict:
    """
    Train with k-fold cross-validation
    """
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
    fold_results = []
    
    for fold, (train_idx, val_idx) in enumerate(skf.split(sequences, labels)):
        logger.info(f"\nTraining Fold {fold + 1}/{n_folds}")
        
        # Split data
        train_sequences = [sequences[i] for i in train_idx]
        train_labels = [labels[i] for i in train_idx]
        val_sequences = [sequences[i] for i in val_idx]
        val_labels = [labels[i] for i in val_idx]
        
        # Train model
        fold_dir = os.path.join(output_dir, f'fold_{fold}')
        os.makedirs(fold_dir, exist_ok=True)
        
        result = train_single_fold(
            train_sequences,
            train_labels,
            val_sequences,
            val_labels,
            fold_dir,
            **kwargs
        )
        
        fold_results.append(result)
    
    # Aggregate results
    avg_metrics = {
        'val_acc': np.mean([r['val_acc'] for r in fold_results]),
        'val_f1': np.mean([r['val_f1'] for r in fold_results]),
        'val_loss': np.mean([r['val_loss'] for r in fold_results])
    }
    
    logger.info(f"\nCross-validation results:")
    logger.info(f"  Average Val Accuracy: {avg_metrics['val_acc']:.2f}%")
    logger.info(f"  Average Val F1: {avg_metrics['val_f1']:.4f}")
    logger.info(f"  Average Val Loss: {avg_metrics['val_loss']:.4f}")
    
    return avg_metrics


def train_single_fold(
    train_sequences: List[str],
    train_labels: List[int],
    val_sequences: List[str],
    val_labels: List[int],
    output_dir: str,
    **kwargs
) -> Dict:
    """
    Train a single fold
    """
    # Implementation similar to train_classifier but for a single fold
    # Returns validation metrics
    pass  # Placeholder
