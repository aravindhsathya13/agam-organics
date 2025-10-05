"""
Shopping Cart API routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from app.models.schemas import CartItemAdd, CartItemUpdate, CartResponse, CartItemResponse
from app.db.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.get("/", response_model=CartResponse)
async def get_cart(current_user: dict = Depends(get_current_user)):
    """Get user's shopping cart"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # Get cart items with product details
    result = db.table("cart").select(
        "*, products(id, name, price, discount_price, image_url)"
    ).eq("user_id", user_id).execute()
    
    items = []
    subtotal = 0.0
    total_savings = 0.0
    
    for item in result.data:
        product = item["products"]
        original_price = product["price"]
        discounted_price = product["discount_price"] if product["discount_price"] else product["price"]
        item_subtotal = discounted_price * item["quantity"]
        
        # Calculate savings
        if product["discount_price"]:
            item_savings = (original_price - discounted_price) * item["quantity"]
            total_savings += item_savings
        
        items.append(CartItemResponse(
            id=item["id"],
            product_id=product["id"],
            product_name=product["name"],
            product_image=product["image_url"],
            price=discounted_price,
            quantity=item["quantity"],
            subtotal=item_subtotal
        ))
        
        subtotal += item_subtotal
    
    return CartResponse(
        items=items,
        total_items=len(items),
        total_price=subtotal,
        total_savings=total_savings,
        final_total=subtotal
    )


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_to_cart(item: CartItemAdd, current_user: dict = Depends(get_current_user)):
    """Add item to cart"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # Check if product exists
    product = db.table("products").select("id, stock").eq("id", item.product_id).execute()
    
    if not product.data:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.data[0]["stock"] < item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Check if item already in cart
    existing = db.table("cart").select("*").eq("user_id", user_id).eq("product_id", item.product_id).execute()
    
    if existing.data:
        # Update quantity
        new_quantity = existing.data[0]["quantity"] + item.quantity
        db.table("cart").update({"quantity": new_quantity}).eq("id", existing.data[0]["id"]).execute()
    else:
        # Add new item
        db.table("cart").insert({
            "user_id": user_id,
            "product_id": item.product_id,
            "quantity": item.quantity
        }).execute()
    
    return {"message": "Item added to cart"}


@router.put("/update/{cart_item_id}")
async def update_cart_item(
    cart_item_id: str,
    update: CartItemUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update cart item quantity"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # Verify cart item belongs to user
    cart_item = db.table("cart").select("*").eq("id", cart_item_id).eq("user_id", user_id).execute()
    
    if not cart_item.data:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    # Check product stock
    product = db.table("products").select("stock").eq("id", cart_item.data[0]["product_id"]).execute()
    
    if product.data[0]["stock"] < update.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Update quantity
    db.table("cart").update({"quantity": update.quantity}).eq("id", cart_item_id).execute()
    
    return {"message": "Cart updated"}


@router.delete("/remove/{cart_item_id}")
async def remove_from_cart(cart_item_id: str, current_user: dict = Depends(get_current_user)):
    """Remove item from cart"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # Verify and delete
    result = db.table("cart").delete().eq("id", cart_item_id).eq("user_id", user_id).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    return {"message": "Item removed from cart"}


@router.delete("/clear")
async def clear_cart(current_user: dict = Depends(get_current_user)):
    """Clear all items from cart"""
    db = get_db()
    user_id = current_user["user_id"]
    
    db.table("cart").delete().eq("user_id", user_id).execute()
    
    return {"message": "Cart cleared"}
