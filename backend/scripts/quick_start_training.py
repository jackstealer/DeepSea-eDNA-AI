"""
Quick start script to download data and train a model
"""
import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_sample_data():
    """
    Download sample marine eDNA data from NCBI
    """
    logger.info("Downloading sample data from NCBI...")
    
    # Example queries for different marine organisms
    queries = [
        ("Copepoda", "Copepoda[Organism] AND COI[Gene] AND 400:700[SLEN]"),
        ("Amphipoda", "Amphipoda[Organism] AND COI[Gene] AND 400:700[SLEN]"),
        ("Decapoda", "Decapoda[Organism] AND COI[Gene] AND 400:700[SLEN]"),
        ("Euphausiacea", "Euphausiacea[Organism] AND COI[Gene] AND 400:700[SLEN]"),
        ("Mysida", "Mysida[Organism] AND COI[Gene] AND 400:700[SLEN]"),
    ]
    
    from download_ncbi_data import NCBIDataDownloader
    
    # You need to provide your email
    email = input("Enter your email for NCBI: ")
    api_key = input("Enter NCBI API key (optional, press Enter to skip): ").strip() or None
    
    downloader = NCBIDataDownloader(email, api_key)
    
    output_dir = Path("../data/training/marine_crustaceans")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    all_sequences = []
    
    for taxon_name, query in queries:
        logger.info(f"Downloading {taxon_name}...")
        
        try:
            # Search
            id_list = downloader.search_sequences(
                query=query,
                max_sequences=200,  # Small dataset for quick training
                min_length=400,
                max_length=700
            )
            
            if not id_list:
                logger.warning(f"No sequences found for {taxon_name}")
                continue
            
            # Fetch
            sequences = downloader.fetch_sequences(id_list[:200])
            all_sequences.extend(sequences)
            
            logger.info(f"Downloaded {len(sequences)} sequences for {taxon_name}")
            
        except Exception as e:
            logger.error(f"Error downloading {taxon_name}: {e}")
            continue
    
    if not all_sequences:
        logger.error("No sequences downloaded!")
        return False
    
    # Organize by taxonomy
    logger.info("Organizing sequences by taxonomy...")
    taxonomy_map = downloader.organize_by_taxonomy(
        all_sequences,
        str(output_dir),
        taxonomic_level='order'
    )
    
    logger.info(f"Downloaded {len(all_sequences)} total sequences")
    logger.info(f"Organized into {len(taxonomy_map)} classes")
    logger.info(f"Data saved to {output_dir}")
    
    return True


def train_model():
    """
    Train the model on downloaded data
    """
    logger.info("Starting model training...")
    
    import subprocess
    
    # Run training script
    cmd = [
        sys.executable,
        "../training/train_model.py",
        "--data_dir", "../data/training/marine_crustaceans",
        "--output_dir", "../ml_models/marine_model_v1",
        "--epochs", "30",
        "--batch_size", "16",
        "--device", "cuda" if os.system("nvidia-smi") == 0 else "cpu",
        "--augmentation",
        "--class_weights"
    ]
    
    result = subprocess.run(cmd, cwd=Path(__file__).parent)
    
    if result.returncode == 0:
        logger.info("Training completed successfully!")
        return True
    else:
        logger.error("Training failed!")
        return False


def main():
    """
    Main quick start workflow
    """
    logger.info("=" * 80)
    logger.info("Quick Start: Download Data and Train Model")
    logger.info("=" * 80)
    
    # Check if data already exists
    data_dir = Path("../data/training/marine_crustaceans")
    
    if data_dir.exists() and any(data_dir.iterdir()):
        logger.info("Training data already exists")
        use_existing = input("Use existing data? (y/n): ").lower() == 'y'
        
        if not use_existing:
            logger.info("Downloading new data...")
            if not download_sample_data():
                logger.error("Failed to download data")
                return
    else:
        logger.info("No existing data found, downloading...")
        if not download_sample_data():
            logger.error("Failed to download data")
            return
    
    # Train model
    logger.info("\nStarting training...")
    proceed = input("Proceed with training? (y/n): ").lower() == 'y'
    
    if proceed:
        if train_model():
            logger.info("\n" + "=" * 80)
            logger.info("Quick Start Complete!")
            logger.info("=" * 80)
            logger.info("Model saved to: ml_models/marine_model_v1")
            logger.info("\nTo use the model:")
            logger.info("1. Update backend/.env: DEFAULT_MODEL=marine_model_v1")
            logger.info("2. Start backend: python app/main.py")
            logger.info("3. Update frontend/.env: VITE_DEMO_MODE=false")
            logger.info("4. Start frontend: npm run dev")
        else:
            logger.error("Training failed")
    else:
        logger.info("Training skipped")


if __name__ == '__main__':
    main()
