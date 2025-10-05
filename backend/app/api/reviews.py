"""
Product Reviews API routes
"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from app.models.schemas import ReviewCreate, ReviewResponse, ReviewList
from app.db.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewCreate, current_user: dict = Depends(get_current_user)):
    """Create a product review"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # Verify product exists
    product = db.table("products").select("id").eq("id", review.product_id).execute()
    
    if not product.data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if user already reviewed this product
    existing = db.table("reviews").select("id").eq("product_id", review.product_id).eq("user_id", user_id).execute()
    
    if existing.data:
        raise HTTPException(status_code=400, detail="You have already reviewed this product")
    
    # Get user info
    user = db.table("users").select("full_name").eq("id", user_id).execute()
    
    # Create review
    review_data = review.model_dump()
    review_data["user_id"] = user_id
    
    result = db.table("reviews").insert(review_data).execute()
    
    # Update product rating
    await update_product_rating(review.product_id)
    
    # Prepare response
    review_response = result.data[0]
    review_response["user_name"] = user.data[0]["full_name"]
    
    return ReviewResponse(**review_response)


@router.get("/{product_id}", response_model=ReviewList)
async def get_product_reviews(
    product_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50)
):
    """Get reviews for a product"""
    db = get_db()
    
    # Get reviews with user info
    offset = (page - 1) * page_size
    
    reviews = db.table("reviews").select(
        "*, users(full_name)"
    ).eq("product_id", product_id).order("created_at", desc=True).range(
        offset, offset + page_size - 1
    ).execute()
    
    # Get total count
    count = db.table("reviews").select("id", count="exact").eq("product_id", product_id).execute()
    
    # Calculate average rating
    all_reviews = db.table("reviews").select("rating").eq("product_id", product_id).execute()
    
    if all_reviews.data:
        avg_rating = sum([r["rating"] for r in all_reviews.data]) / len(all_reviews.data)
    else:
        avg_rating = 0.0
    
    # Format response
    review_list = []
    for review in reviews.data:
        review["user_name"] = review["users"]["full_name"]
        del review["users"]
        review_list.append(ReviewResponse(**review))
    
    return ReviewList(
        reviews=review_list,
        total=count.count or 0,
        average_rating=round(avg_rating, 2)
    )


@router.put("/{review_id}/helpful")
async def mark_review_helpful(review_id: str, current_user: dict = Depends(get_current_user)):
    """Mark a review as helpful"""
    db = get_db()
    
    review = db.table("reviews").select("helpful_count").eq("id", review_id).execute()
    
    if not review.data:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Increment helpful count
    new_count = review.data[0]["helpful_count"] + 1
    db.table("reviews").update({"helpful_count": new_count}).eq("id", review_id).execute()
    
    return {"message": "Review marked as helpful"}


@router.delete("/{review_id}")
async def delete_review(review_id: str, current_user: dict = Depends(get_current_user)):
    """Delete own review"""
    db = get_db()
    user_id = current_user["user_id"]
    
    review = db.table("reviews").select("product_id").eq("id", review_id).eq("user_id", user_id).execute()
    
    if not review.data:
        raise HTTPException(status_code=404, detail="Review not found")
    
    product_id = review.data[0]["product_id"]
    
    # Delete review
    db.table("reviews").delete().eq("id", review_id).execute()
    
    # Update product rating
    await update_product_rating(product_id)
    
    return {"message": "Review deleted"}


async def update_product_rating(product_id: str):
    """Update product rating and review count"""
    db = get_db()
    
    # Get all reviews for product
    reviews = db.table("reviews").select("rating").eq("product_id", product_id).execute()
    
    if reviews.data:
        avg_rating = sum([r["rating"] for r in reviews.data]) / len(reviews.data)
        review_count = len(reviews.data)
    else:
        avg_rating = 0.0
        review_count = 0
    
    # Update product
    db.table("products").update({
        "rating": round(avg_rating, 2),
        "review_count": review_count
    }).eq("id", product_id).execute()
