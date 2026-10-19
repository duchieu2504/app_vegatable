"""
Encyclopedia API routes - Disease knowledge base endpoints.
"""
from fastapi import APIRouter, Request
from services.admin_service import (
    get_encyclopedia_data,
    get_or_create_disease_details,
    update_disease_details,
)

router = APIRouter(prefix="/api/v1", tags=["Encyclopedia"])


@router.get("/encyclopedia")
def get_encyclopedia():
    """Returns the full hierarchical encyclopedia data grouped by plant."""
    data = get_encyclopedia_data()
    return {"status": "success", "data": data}


@router.get("/encyclopedia/{disease_id}")
async def get_disease_detail(
    disease_id: str, request: Request, name: str = "", force_ai: bool = False
):
    """Returns detailed information for a specific disease, auto-generating via AI if needed."""
    host_url = str(request.base_url).rstrip('/')
    data = await get_or_create_disease_details(disease_id, name, host_url, force_ai)
    return {"status": "success", "data": data}


@router.put("/encyclopedia/{disease_id}")
async def update_disease_detail(disease_id: str, data: dict):
    """Manually update disease encyclopedia details."""
    updated_data = update_disease_details(disease_id, data)
    return {"status": "success", "data": updated_data}
