"""
Banner API endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from app.db.database import supabase

router = APIRouter()


class BannerResponse(BaseModel):
    """Banner response model"""
    id: str
    title: str
    subtitle: str | None
    image_url: str
    link_url: str | None
    button_text: str
    display_order: int


@router.get("/", response_model=List[BannerResponse])
async def get_banners():
    """Get all active banners ordered by display_order"""
    try:
        response = supabase.table("banners")\
            .select("*")\
            .eq("is_active", True)\
            .order("display_order")\
            .execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
