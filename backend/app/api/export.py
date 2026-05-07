"""
Export API endpoints
"""
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
import io
import csv
import json

logger = logging.getLogger(__name__)

router = APIRouter()

# Import jobs from analysis module
from app.api.analysis import jobs


@router.get("/export/{job_id}")
async def export_results(job_id: str, format: str = 'csv'):
    """
    Export analysis results
    """
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    
    if job['status'] != 'completed':
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    results = job['results']
    
    if format == 'json':
        content = json.dumps(results, indent=2)
        media_type = 'application/json'
        filename = f'results_{job_id}.json'
        
    elif format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Taxon', 'Abundance', 'Confidence', 'Status', 'Rank', 'Lineage'])
        
        # Write data
        for taxon in results['taxonomicData']:
            writer.writerow([
                taxon['name'],
                taxon['abundance'],
                f"{taxon['confidence']*100:.1f}%",
                'Novel' if taxon['isNovel'] else 'Known',
                taxon.get('taxonomicRank', 'N/A'),
                ' > '.join(taxon.get('lineage', []))
            ])
        
        content = output.getvalue()
        media_type = 'text/csv'
        filename = f'results_{job_id}.csv'
        
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")
    
    return StreamingResponse(
        io.BytesIO(content.encode()),
        media_type=media_type,
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )
