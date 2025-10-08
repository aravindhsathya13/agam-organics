"""
Checkout API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from app.db.database import get_db
from app.core.security import get_current_user
from app.core.config import settings
import uuid
from datetime import datetime
import razorpay
import asyncio
from httpx import ReadTimeout

router = APIRouter()

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY, settings.RAZORPAY_SECRET))


class CheckoutRequest(BaseModel):
    """Checkout request model"""
    address_id: str
    payment_method: str
    payment_details: dict = {}


class RazorpayOrderRequest(BaseModel):
    """Razorpay order creation request"""
    address_id: str


def generate_order_number() -> str:
    """Generate unique order number"""
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_suffix = str(uuid.uuid4())[:6].upper()
    return f"AO{timestamp}{random_suffix}"


def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """Verify Razorpay payment signature"""
    try:
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        razorpay_client.utility.verify_payment_signature(params_dict)
        return True
    except razorpay.errors.SignatureVerificationError:
        return False
    except Exception:
        return False


@router.post("/razorpay-order")
async def create_razorpay_order(
    request: RazorpayOrderRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create Razorpay order for online payment"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # Get cart items and calculate total
    cart_items = db.table("cart").select(
        "*, products(id, name, price, discount_price, stock)"
    ).eq("user_id", user_id).execute()
    
    if not cart_items.data:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Calculate total amount
    total_amount = 0.0
    for item in cart_items.data:
        product = item["products"]
        price = product["discount_price"] if product["discount_price"] else product["price"]
        total_amount += price * item["quantity"]
    
    # Convert to paise (Razorpay uses smallest currency unit)
    amount_paise = int(total_amount * 100)
    
    try:
        # Create Razorpay order using the official SDK
        razorpay_order = razorpay_client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "payment_capture": 1  # Auto capture payment
        })
        
        return {
            "success": True,
            "razorpay_key": settings.RAZORPAY_KEY,
            "amount": amount_paise,
            "currency": "INR",
            "razorpay_order_id": razorpay_order['id'],
            "total_amount": total_amount
        }
    except Exception as e:
        print(f"Razorpay order creation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create Razorpay order: {str(e)}"
        )


@router.post("/create-order")
async def create_order(
    checkout: CheckoutRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create order after payment/checkout"""
    db = get_db()
    user_id = current_user["user_id"]
    
    # Get cart items
    cart_items = db.table("cart").select(
        "*, products(id, name, price, discount_price, stock, image_url)"
    ).eq("user_id", user_id).execute()
    
    if not cart_items.data:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Verify address
    address = db.table("addresses").select("*").eq("id", checkout.address_id).eq("user_id", user_id).execute()
    
    if not address.data:
        raise HTTPException(status_code=404, detail="Address not found")
    
    # Verify online payment
    if not checkout.payment_details:
        raise HTTPException(status_code=400, detail="Payment details are required")

    # Verify Razorpay signature
    is_valid = verify_razorpay_signature(
        checkout.payment_details.get("razorpay_order_id"),
        checkout.payment_details.get("razorpay_payment_id"),
        checkout.payment_details.get("razorpay_signature")
    )
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid payment signature")
    payment_status = "paid"
    
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
        "status": "confirmed" if payment_status == "paid" else "pending",
        "payment_method": checkout.payment_method,
        "payment_status": payment_status,
        "total_amount": total_amount,
        "shipping_address": address.data[0]
    }
    
    # Retry logic for database operations
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            created_order = db.table("orders").insert(order_data).execute()
            order_id = created_order.data[0]["id"]
            break
        except ReadTimeout as e:
            print(f"Database timeout on attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                raise HTTPException(
                    status_code=504,
                    detail="Database operation timed out. Please try again."
                )
        except Exception as e:
            print(f"Error creating order: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create order: {str(e)}"
            )
    
    # Insert order items
    for item in order_items:
        item["order_id"] = order_id
        db.table("order_items").insert(item).execute()
        
        # Update product stock directly
        product_id = item["product_id"]
        quantity = item["quantity"]
        
        # Get current stock
        product = db.table("products").select("stock").eq("id", product_id).execute()
        if product.data:
            new_stock = product.data[0]["stock"] - quantity
            db.table("products").update({"stock": new_stock}).eq("id", product_id).execute()
    
    # Clear cart
    db.table("cart").delete().eq("user_id", user_id).execute()
    
    return {
        "success": True,
        "message": "Order created successfully",
        "order_id": order_id,
        "order_number": order_number
    }
