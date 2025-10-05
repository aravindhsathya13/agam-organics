"""
User Profile API routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.models.schemas import UserProfile, UserProfileUpdate, AddressCreate, AddressResponse
from app.db.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.get("/", response_model=UserProfile)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get user profile"""
    db = get_db()
    
    result = db.table("users").select("*").eq("id", current_user["user_id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return result.data[0]


@router.put("/", response_model=UserProfile)
async def update_profile(profile_update: UserProfileUpdate, current_user: dict = Depends(get_current_user)):
    """Update user profile"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # Prepare update data (only non-None values)
    update_data = {k: v for k, v in profile_update.model_dump().items() if v is not None}
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")
    
    # Update profile
    result = db.table("users").update(update_data).eq("id", user_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return result.data[0]


# Address management
@router.get("/addresses", response_model=List[AddressResponse])
async def get_addresses(current_user: dict = Depends(get_current_user)):
    """Get all user addresses"""
    db = get_db()
    
    result = db.table("addresses").select("*").eq("user_id", current_user["user_id"]).execute()
    
    return result.data


@router.post("/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
async def create_address(address: AddressCreate, current_user: dict = Depends(get_current_user)):
    """Create new address"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # If this is set as default, unset other defaults
    if address.is_default:
        db.table("addresses").update({"is_default": False}).eq("user_id", user_id).execute()
    
    address_data = address.model_dump()
    address_data["user_id"] = user_id
    
    result = db.table("addresses").insert(address_data).execute()
    
    return result.data[0]


@router.put("/addresses/{address_id}", response_model=AddressResponse)
async def update_address(
    address_id: str,
    address: AddressCreate,
    current_user: dict = Depends(get_current_user)
):
    """Update address"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # Verify address belongs to user
    existing = db.table("addresses").select("*").eq("id", address_id).eq("user_id", user_id).execute()
    
    if not existing.data:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # If setting as default, unset other defaults
    if address.is_default:
        db.table("addresses").update({"is_default": False}).eq("user_id", user_id).execute()
    
    result = db.table("addresses").update(address.model_dump()).eq("id", address_id).execute()
    
    return result.data[0]


@router.delete("/addresses/{address_id}")
async def delete_address(address_id: str, current_user: dict = Depends(get_current_user)):
    """Delete address"""
    db = get_db()
    user_id = current_user["user_id"]
    
    result = db.table("addresses").delete().eq("id", address_id).eq("user_id", user_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Address not found")
    
    return {"message": "Address deleted"}
