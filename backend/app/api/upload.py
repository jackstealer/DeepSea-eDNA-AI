"""
File upload API endpoints
"""
import logging
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import aiofiles

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """
    Upload eDNA sequence files and return file paths for analysis
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    uploaded_files = []
    file_paths = []
    
    for file in files:
        # Validate file extension
        if not any(file.filename.endswith(ext) for ext in ['.fasta', '.fastq', '.fa', '.fq', '.fas', '.fna']):
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file format: {file.filename}. Accepted formats: .fasta, .fastq, .fa, .fq, .fas, .fna"
            )
        
        # Generate unique filename to avoid conflicts
        import uuid
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / unique_filename
        
        try:
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                
                # Validate file size (100MB default)
                max_size = 100 * 1024 * 1024  # 100MB
                if len(content) > max_size:
                    raise HTTPException(
                        status_code=400,
                        detail=f"File too large: {file.filename}. Maximum size: 100MB"
                    )
                
                await f.write(content)
            
            uploaded_files.append({
                'filename': file.filename,
                'path': str(file_path),
                'size': len(content)
            })
            file_paths.append(str(file_path))
            
            logger.info(f"Uploaded file: {file.filename} ({len(content)} bytes) -> {file_path}")
            
        except Exception as e:
            logger.error(f"Error uploading {file.filename}: {e}")
            # Clean up partial upload
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=str(e))
    
    return {
        'message': f'Successfully uploaded {len(uploaded_files)} files',
        'files': uploaded_files,
        'file_paths': file_paths  # Return paths for analysis
    }
