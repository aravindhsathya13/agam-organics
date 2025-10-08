"""
Orders API routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.models.schemas import OrderCreate, OrderResponse, OrderItemResponse
from app.db.database import get_db
from app.core.security import get_current_user
import uuid
from datetime import datetime

router = APIRouter()


def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4())[:6].upper()
    return f"AO{timestamp}{random_suffix}"


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    """Create a new order from cart"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # Get cart items
    cart_items = db.table("cart").select(
        "*, products(id, name, price, discount_price, stock)"
    ).eq("user_id", user_id).execute()
    
    if not cart_items.data:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Verify address
    address = db.table("addresses").select("*").eq("id", order.address_id).eq("user_id", user_id).execute()
    
    if not address.data:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Calculate total and prepare order items
    total_amount = 0.0
    order_items = []
    
    for item in cart_items.data:
        product = item["products"]
        
        # Check stock
        if product["stock"] < item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {product['name']}"
            )
        
        price = product["discount_price"] if product["discount_price"] else product["price"]
        subtotal = price * item["quantity"]
        total_amount += subtotal
        
        order_items.append({
            "product_id": product["id"],
            "product_name": product["name"],
            "quantity": item["quantity"],
            "price": price,
            "subtotal": subtotal
        })
    
    # Create order
    order_number = generate_order_number()
    
    order_data = {
        "order_number": order_number,
        "user_id": user_id,
        "status": "pending",
        "payment_method": order.payment_method,
        "payment_status": "pending" if order.payment_method == "online" else "cod",
        "total_amount": total_amount,
        "shipping_address": address.data[0]
    }
    
    created_order = db.table("orders").insert(order_data).execute()
    order_id = created_order.data[0]["id"]
    
    # Insert order items
    for item in order_items:
        item["order_id"] = order_id
        db.table("order_items").insert(item).execute()
        
        # Update product stock
        db.rpc("decrement_stock", {
            "product_id": item["product_id"],
            "quantity": item["quantity"]
        }).execute()
    
    # Clear cart
    db.table("cart").delete().eq("user_id", user_id).execute()
    
    # Return created order
    return await get_order(order_id, current_user)


@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(current_user: dict = Depends(get_current_user)):
    """Get all orders for current user"""
    db = get_db()
    user_id = current_user["user_id"]
    
    orders = db.table("orders").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    
    result = []
    for order in orders.data:
        # Get order items
        items = db.table("order_items").select("*").eq("order_id", order["id"]).execute()
        
        order["items"] = [OrderItemResponse(**item) for item in items.data]
        result.append(OrderResponse(**order))
    
    return result


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Get order by ID"""
    db = get_db()
    user_id = current_user["user_id"]
    
    try:
        order = db.table("orders").select("*").eq("id", order_id).eq("user_id", user_id).execute()
        
        if not order.data:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order_data = order.data[0]
        
        # Get user phone as fallback if address doesn't have phone
        user_data = db.table("users").select("phone").eq("id", user_id).execute()
        user_phone = user_data.data[0].get('phone') if user_data.data else None
        
        # Add phone to shipping_address if not present
        if order_data.get('shipping_address') and not order_data['shipping_address'].get('phone'):
            order_data['shipping_address']['phone'] = user_phone
        
        # Get order items with product images
        try:
            # Try with join first - get image from products table
            items = db.table("order_items").select("*, products(image_url)").eq("order_id", order_id).execute()
            print(f"[DEBUG] Fetched {len(items.data)} order items with join")
        except Exception as join_error:
            print(f"Join query failed: {join_error}, falling back to basic query")
            # Fallback to basic query without join
            items = db.table("order_items").select("*").eq("order_id", order_id).execute()
        
        # Process items to include product image
        processed_items = []
        for item in items.data:
            item_dict = dict(item)
            print(f"[DEBUG] Processing item: {item_dict.get('product_name', 'Unknown')}")
            
            # Extract image from nested products object if available
            if 'products' in item_dict and item_dict['products']:
                product_image = item_dict['products'].get('image_url')
                item_dict['product_image'] = product_image
                print(f"[DEBUG] Product image from join: {product_image}")
            else:
                # If join failed, try to fetch product image separately
                try:
                    product_id = item_dict.get('product_id')
                    if product_id:
                        product_data = db.table("products").select("image_url").eq("id", product_id).execute()
                        if product_data.data and product_data.data[0].get('image_url'):
                            item_dict['product_image'] = product_data.data[0]['image_url']
                            print(f"[DEBUG] Product image from separate query: {product_data.data[0]['image']}")
                        else:
                            print(f"[DEBUG] No product image found for product_id: {product_id}")
                except Exception as img_error:
                    print(f"[DEBUG] Error fetching product image: {img_error}")
            
            # Remove nested products object
            if 'products' in item_dict:
                del item_dict['products']
            
            processed_items.append(OrderItemResponse(**item_dict))
        
        order_data["items"] = processed_items
        print(f"[DEBUG] Returning order with {len(processed_items)} items")
        
        return OrderResponse(**order_data)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting order {order_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error retrieving order: {str(e)}")


@router.put("/{order_id}/cancel")
async def cancel_order(order_id: str, current_user: dict = Depends(get_current_user)):
    """Cancel an order"""
    db = get_db()
    user_id = current_user["user_id"]
    
    order = db.table("orders").select("*").eq("id", order_id).eq("user_id", user_id).execute()
    
    if not order.data:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.data[0]["status"] in ["shipped", "delivered", "cancelled"]:
        raise HTTPException(status_code=400, detail="Cannot cancel this order")
    
    # Update order status
    db.table("orders").update({"status": "cancelled"}).eq("id", order_id).execute()
    
    # Restore product stock
    items = db.table("order_items").select("*").eq("order_id", order_id).execute()
    
    for item in items.data:
        db.rpc("increment_stock", {
            "product_id": item["product_id"],
            "quantity": item["quantity"]
        }).execute()
    
    return {"message": "Order cancelled successfully"}
