"""
Convert PyTorch model to HDF5 format
"""
import torch
import h5py
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.models.deep_learning import DeepTaxaClassifier


def convert_pytorch_to_h5(model_dir: str, output_path: str):
    """
    Convert PyTorch model to HDF5 format
    
    Args:
        model_dir: Directory containing the PyTorch model
        output_path: Path to save the HDF5 file
    """
    print(f"Loading PyTorch model from {model_dir}...")
    
    # Load model configuration
    config_path = Path(model_dir) / "model_config.json"
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Initialize model
    model = DeepTaxaClassifier(
        num_classes=config['num_classes'],
        embedding_dim=config['embedding_dim'],
        hidden_dim=config['hidden_dim'],
        num_conv_layers=config['num_conv_layers'],
        dropout=config['dropout']
    )
    
    # Load trained weights
    checkpoint_path = Path(model_dir) / "best_model.pth"
    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    print(f"Converting to HDF5 format...")
    
    # Create HDF5 file
    with h5py.File(output_path, 'w') as h5file:
        # Save model configuration
        config_group = h5file.create_group('config')
        for key, value in config.items():
            config_group.attrs[key] = value
        
        # Save training metadata
        metadata_group = h5file.create_group('metadata')
        metadata_group.attrs['val_loss'] = checkpoint.get('val_loss', 0.0)
        metadata_group.attrs['val_acc'] = checkpoint.get('val_acc', 0.0)
        metadata_group.attrs['val_f1'] = checkpoint.get('val_f1', 0.0)
        metadata_group.attrs['epoch'] = checkpoint.get('epoch', 0)
        
        # Save model weights
        weights_group = h5file.create_group('weights')
        
        for name, param in model.state_dict().items():
            # Convert tensor to numpy array
            param_data = param.cpu().numpy()
            
            # Create dataset for this parameter
            # Skip compression for scalar values
            if param_data.ndim == 0 or param_data.size == 1:
                weights_group.create_dataset(name, data=param_data)
            else:
                weights_group.create_dataset(
                    name,
                    data=param_data,
                    compression='gzip',
                    compression_opts=9
                )
            
            print(f"  Saved: {name} - Shape: {param_data.shape}")
        
        # Save taxonomy mapping if available
        taxonomy_path = Path(model_dir) / "taxonomy_map.json"
        if taxonomy_path.exists():
            with open(taxonomy_path, 'r') as f:
                taxonomy_map = json.load(f)
            
            taxonomy_group = h5file.create_group('taxonomy')
            for class_id, info in taxonomy_map.items():
                class_group = taxonomy_group.create_group(f'class_{class_id}')
                for key, value in info.items():
                    if isinstance(value, (list, dict)):
                        class_group.attrs[key] = json.dumps(value)
                    else:
                        class_group.attrs[key] = str(value)
    
    print(f"\n✓ Model successfully converted to HDF5!")
    print(f"  Output: {output_path}")
    
    # Print file size
    file_size = Path(output_path).stat().st_size / (1024 * 1024)
    print(f"  Size: {file_size:.2f} MB")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert PyTorch model to HDF5')
    parser.add_argument('--model_dir', type=str, default='../ml_models/marine_model',
                       help='Directory containing PyTorch model')
    parser.add_argument('--output', type=str, default='../ml_models/marine_model/model.h5',
                       help='Output HDF5 file path')
    
    args = parser.parse_args()
    
    convert_pytorch_to_h5(args.model_dir, args.output)


if __name__ == '__main__':
    main()
