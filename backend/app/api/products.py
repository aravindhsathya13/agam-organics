"""
Products API routes
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from app.models.schemas import ProductResponse, ProductList
from app.db.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.get("/", response_model=ProductList)
async def get_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = Query("created_at", regex="^(price|price_desc|rating|created_at|name)$"),
    order: Optional[str] = Query("desc", regex="^(asc|desc)$")
):
    """Get all products with pagination and filters"""
    db = get_db()
    
    # Build query
    query = db.table("products").select("*", count="exact")
    
    # Apply filters
    if category:
        query = query.eq("category", category)
    
    if search:
        query = query.ilike("name", f"%{search}%")
    
    # Apply sorting
    # For price sorting, we need to get all products first and sort in Python
    # because we need to use discount_price when available, otherwise price
    needs_python_sort = sort_by in ["price", "price_desc"]
    
    if not needs_python_sort:
        if sort_by == "name":
            query = query.order("name", desc=False)
        elif sort_by == "rating":
            query = query.order("rating", desc=True)
        else:
            # Default: created_at descending
            query = query.order("created_at", desc=True)
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.range(offset, offset + page_size - 1)
    
    result = query.execute()
    
    # Sort by price in Python if needed
    if needs_python_sort:
        products = result.data
        # Get effective price (discount_price if available, otherwise price)
        def get_effective_price(product):
            return product.get('discount_price') or product.get('price', 0)
        
        # Sort by effective price
        products.sort(key=get_effective_price, reverse=(sort_by == "price_desc"))
        result.data = products
    
    return ProductList(
        products=result.data,
        total=result.count or 0,
        page=page,
        page_size=page_size
    )


@router.get("/categories")
async def get_categories():
    """Get all unique product categories"""
    db = get_db()
    
    result = db.table("products").select("category").execute()
    
    categories = list(set([item["category"] for item in result.data]))
    
    return {"categories": categories}


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get product by ID"""
    db = get_db()
    
    result = db.table("products").select("*").eq("id", product_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return result.data[0]


@router.get("/similar/{product_id}")
async def get_similar_products(product_id: str, limit: int = Query(4, ge=1, le=10)):
    """Get similar products based on category"""
    db = get_db()
    
    # Get current product category
    product = db.table("products").select("category").eq("id", product_id).execute()
    
    if not product.data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    category = product.data[0]["category"]
    
    # Get similar products
    result = db.table("products").select("*").eq("category", category).neq("id", product_id).limit(limit).execute()
    
    return {"products": result.data}
