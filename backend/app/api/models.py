"""
Model management API endpoints
"""
import logging
from fastapi import APIRouter, HTTPException
from pathlib import Path

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/models")
async def list_models():
    """
    List available models
    """
    model_dir = Path(settings.MODEL_DIR)
    
    if not model_dir.exists():
        return {'models': []}
    
    models = []
    for model_path in model_dir.iterdir():
        if model_path.is_dir():
            config_file = model_path / 'model_config.json'
            if config_file.exists():
                models.append({
                    'name': model_path.name,
                    'path': str(model_path)
                })
    
    return {'models': models}


@router.get("/models/{model_name}")
async def get_model_info(model_name: str):
    """
    Get model information
    """
    model_path = Path(settings.MODEL_DIR) / model_name
    
    if not model_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")
    
    import json
    
    config_file = model_path / 'model_config.json'
    taxonomy_file = model_path / 'taxonomy_map.json'
    
    info = {'name': model_name}
    
    if config_file.exists():
        with open(config_file, 'r') as f:
            info['config'] = json.load(f)
    
    if taxonomy_file.exists():
        with open(taxonomy_file, 'r') as f:
            taxonomy = json.load(f)
            info['num_classes'] = len(taxonomy)
            info['classes'] = list(taxonomy.values())
    
    return info
