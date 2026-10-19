"""
History API routes - Diagnosis history endpoints.
"""
from fastapi import APIRouter
from database.db import get_diagnosis_history, get_diagnosis_stats

router = APIRouter(prefix="/api/v1", tags=["History"])


@router.get("/history")
def get_history(limit: int = 50, offset: int = 0):
    """Returns paginated diagnosis history, most recent first."""
    records = get_diagnosis_history(limit=limit, offset=offset)
    return {"status": "success", "data": records}


@router.get("/history/stats")
def get_stats():
    """Returns aggregated diagnosis statistics."""
    stats = get_diagnosis_stats()
    return {"status": "success", "data": stats}
