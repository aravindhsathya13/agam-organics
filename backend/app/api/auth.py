"""
Authentication API routes
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import UserSignup, UserLogin, Token, UserProfile
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, get_current_user
from app.db.database import get_db
from datetime import timedelta

router = APIRouter()


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignup):
    """Register a new user"""
    db = get_db()
    
    try:
        # Check if user already exists
        existing = db.table("users").select("id").eq("email", user.email).execute()
        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash the password
        hashed_password = get_password_hash(user.password)
        
        # Create user directly in database
        result = db.table("users").insert({
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone,
            "password_hash": hashed_password
        }).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        user_data = result.data[0]
        user_id = user_data["id"]
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user_id, "email": user.email})
        refresh_token = create_refresh_token(data={"sub": user_id, "email": user.email})
        
        return Token(access_token=access_token, refresh_token=refresh_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Signup failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user"""
    db = get_db()
    
    try:
        # Get user from database
        result = db.table("users").select("*").eq("email", credentials.email).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user_data = result.data[0]
        
        # Verify password
        if not verify_password(credentials.password, user_data.get("password_hash", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        user_id = user_data["id"]
        
        # Generate tokens
        access_token = create_access_token(data={"sub": user_id, "email": credentials.email})
        refresh_token = create_refresh_token(data={"sub": user_id, "email": credentials.email})
        
        return Token(access_token=access_token, refresh_token=refresh_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Login failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """Refresh access token"""
    access_token = create_access_token(
        data={"sub": current_user["user_id"], "email": current_user["email"]}
    )
    refresh_token = create_refresh_token(
        data={"sub": current_user["user_id"], "email": current_user["email"]}
    )
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile"""
    db = get_db()
    
    result = db.table("users").select("*").eq("id", current_user["user_id"]).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")
    
    return result.data[0]
