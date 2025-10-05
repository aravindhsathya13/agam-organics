"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date


# User Models
class UserSignup(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str
    phone: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_anniversary: Optional[date] = None
    created_at: datetime


class UserProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_anniversary: Optional[date] = None


# Address Models
class AddressCreate(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    pincode: str
    is_default: bool = False


class AddressResponse(AddressCreate):
    id: str
    user_id: str


# Product Models
class ProductBase(BaseModel):
    name: str
    description: str
    category: str
    price: float
    discount_price: Optional[float] = None
    stock: int
    unit: str  # kg, grams, pack
    image_url: Optional[str] = None
    additional_images: Optional[List[str]] = []


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: str
    rating: float = 0.0
    review_count: int = 0
    created_at: datetime


class ProductList(BaseModel):
    products: List[ProductResponse]
    total: int
    page: int
    page_size: int


# Cart Models
class CartItemAdd(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    id: str
    product_id: str
    product_name: str
    product_image: Optional[str]
    price: float
    quantity: int
    subtotal: float


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    total_price: float
    total_savings: float = 0.0
    final_total: float


# Order Models
class OrderCreate(BaseModel):
    address_id: str
    payment_method: str  # cod, online
    items: List[dict]  # Will contain cart items


class OrderItemResponse(BaseModel):
    product_id: str
    product_name: str
    product_image: Optional[str] = None
    quantity: int
    price: float
    subtotal: float


class OrderResponse(BaseModel):
    id: str
    order_number: str
    status: str  # pending, confirmed, shipped, delivered, cancelled
    payment_method: str
    payment_status: str  # pending, completed, failed
    total_amount: float
    items: List[OrderItemResponse]
    shipping_address: dict
    created_at: datetime
    updated_at: datetime


# Review Models
class ReviewCreate(BaseModel):
    product_id: str
    rating: int = Field(..., ge=1, le=5)
    title: str
    comment: str
    images: Optional[List[str]] = []


class ReviewResponse(BaseModel):
    id: str
    product_id: str
    user_id: str
    user_name: str
    rating: int
    title: str
    comment: str
    images: Optional[List[str]]
    created_at: datetime
    helpful_count: int = 0


class ReviewList(BaseModel):
    reviews: List[ReviewResponse]
    total: int
    average_rating: float
