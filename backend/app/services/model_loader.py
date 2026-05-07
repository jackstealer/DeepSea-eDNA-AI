"""
Model loader service for loading and managing deep learning models
"""
import logging
import torch
import json
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np

from app.models.deep_learning import DeepTaxaClassifier, NovelTaxaDetector, sequence_to_tensor
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelLoader:
    """
    Load and manage deep learning models
    """
    
    def __init__(self):
        self.device = settings.MODEL_DEVICE
        self.model_dir = Path(settings.MODEL_DIR)
        self.classifier = None
        self.novelty_detector = None
        self.taxonomy_map = None
        self.model_config = None
        
    async def load_default_model(self):
        """Load the default model"""
        model_name = settings.DEFAULT_MODEL
        await self.load_model(model_name)
        
    async def load_model(self, model_name: str):
        """
        Load a specific model
        
        Args:
            model_name: Name of the model directory
        """
        model_path = self.model_dir / model_name
        
        if not model_path.exists():
            logger.error(f"Model not found: {model_path}")
            raise FileNotFoundError(f"Model {model_name} not found")
        
        try:
            # Load model config
            config_file = model_path / "model_config.json"
            with open(config_file, 'r') as f:
                self.model_config = json.load(f)
            
            # Load taxonomy mapping
            taxonomy_file = model_path / "taxonomy_map.json"
            with open(taxonomy_file, 'r') as f:
                self.taxonomy_map = json.load(f)
            
            # Initialize classifier
            self.classifier = DeepTaxaClassifier(
                num_classes=self.model_config['num_classes'],
                embedding_dim=self.model_config['embedding_dim'],
                hidden_dim=self.model_config['hidden_dim'],
                num_conv_layers=self.model_config['num_conv_layers'],
                dropout=self.model_config['dropout']
            )
            
            # Load weights
            weights_file = model_path / "best_model.pth"
            checkpoint = torch.load(weights_file, map_location=self.device)
            self.classifier.load_state_dict(checkpoint['model_state_dict'])
            self.classifier.to(self.device)
            self.classifier.eval()
            
            # Load novelty detector if available
            novelty_path = model_path / "novelty" / "novelty_detector.pth"
            if novelty_path.exists():
                self.novelty_detector = NovelTaxaDetector()
                self.novelty_detector.load_state_dict(
                    torch.load(novelty_path, map_location=self.device)
                )
                self.novelty_detector.to(self.device)
                self.novelty_detector.eval()
            
            logger.info(f"Successfully loaded model: {model_name}")
            logger.info(f"  Classes: {self.model_config['num_classes']}")
            logger.info(f"  Device: {self.device}")
            
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
    
    def predict(self, sequences: List[str], batch_size: int = 32) -> List[Dict]:
        """
        Predict taxonomy for sequences
        
        Args:
            sequences: List of DNA sequences
            batch_size: Batch size for inference
            
        Returns:
            List of predictions with taxonomy and confidence
        """
        if self.classifier is None:
            raise RuntimeError("Model not loaded")
        
        results = []
        
        # Process in batches
        for i in range(0, len(sequences), batch_size):
            batch_sequences = sequences[i:i + batch_size]
            
            # Convert to tensors
            tensors = [
                sequence_to_tensor(seq, self.model_config['max_sequence_length'])
                for seq in batch_sequences
            ]
            batch_tensor = torch.stack(tensors).to(self.device)
            
            # Predict
            with torch.no_grad():
                logits, confidence = self.classifier(batch_tensor)
                probabilities = torch.softmax(logits, dim=1)
                predicted_classes = torch.argmax(logits, dim=1)
            
            # Check for novel taxa
            novelty_scores = None
            if self.novelty_detector is not None:
                with torch.no_grad():
                    novelty_scores = self.novelty_detector.get_novelty_score(
                        batch_tensor.float()
                    ).cpu().numpy()
            
            # Format results
            for j, seq in enumerate(batch_sequences):
                class_id = predicted_classes[j].item()
                conf = confidence[j].item()
                probs = probabilities[j].cpu().numpy()
                
                # Get taxonomy info
                taxonomy_info = self.taxonomy_map.get(str(class_id), {})
                
                # Determine if novel
                is_novel = False
                if novelty_scores is not None:
                    # High novelty score indicates potential novel taxon
                    is_novel = novelty_scores[j] > 0.5
                
                # If confidence is low, also mark as potentially novel
                if conf < 0.7:
                    is_novel = True
                
                result = {
                    'sequence': seq[:50] + '...' if len(seq) > 50 else seq,
                    'predicted_class': class_id,
                    'taxon_name': taxonomy_info.get('name', 'Unknown'),
                    'rank': taxonomy_info.get('rank', 'unknown'),
                    'lineage': taxonomy_info.get('lineage', []),
                    'confidence': float(conf),
                    'is_novel': is_novel,
                    'top_predictions': [
                        {
                            'class_id': idx,
                            'taxon_name': self.taxonomy_map.get(str(idx), {}).get('name', 'Unknown'),
                            'probability': float(probs[idx])
                        }
                        for idx in np.argsort(probs)[-3:][::-1]
                    ]
                }
                
                results.append(result)
        
        return results
    
    def is_loaded(self) -> bool:
        """Check if model is loaded"""
        return self.classifier is not None
    
    def cleanup(self):
        """Cleanup resources"""
        if self.classifier is not None:
            del self.classifier
            self.classifier = None
        
        if self.novelty_detector is not None:
            del self.novelty_detector
            self.novelty_detector = None
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        logger.info("Model resources cleaned up")
