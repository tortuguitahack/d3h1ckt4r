from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Tambar Express - Sistema de Gestión Empresarial")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class ProductCategory(str, Enum):
    VINOS = "vinos"
    CERVEZAS = "cervezas"
    LICORES = "licores"
    WHISKEY = "whiskey"
    VODKA = "vodka"
    RON = "ron"
    OTROS = "otros"

class OrderStatus(str, Enum):
    PENDIENTE = "pendiente"
    CONFIRMADO = "confirmado"
    EN_PREPARACION = "en_preparacion"
    EN_ENTREGA = "en_entrega"
    ENTREGADO = "entregado"
    CANCELADO = "cancelado"

class PaymentMethod(str, Enum):
    EFECTIVO = "efectivo"
    QR = "qr"
    TIGO_MONEY = "tigo_money"
    BANCO = "banco"
    TARJETA = "tarjeta"

# Models
class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    cost_price: float  # Precio de adquisición
    sale_price: float  # Precio de venta
    margin: float  # Margen de ganancia calculado
    stock: int
    min_stock: int = 10  # Stock mínimo para alertas
    supplier: Optional[str] = None
    expiry_date: Optional[str] = None  # Fecha de caducidad
    category: ProductCategory
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    cost_price: float
    sale_price: float
    stock: int
    min_stock: int = 10
    supplier: Optional[str] = None
    expiry_date: Optional[str] = None
    category: ProductCategory
    image_url: Optional[str] = None

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    total_purchases: float = 0.0
    loyalty_points: int = 0
    preferred_products: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None

class OrderItem(BaseModel):
    product_id: str
    product_name: str
    quantity: int
    unit_price: float
    total_price: float

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    customer_name: str
    customer_phone: str
    items: List[OrderItem]
    subtotal: float
    iva: float  # 13% IVA boliviano
    it: float   # 3% IT boliviano
    total: float
    status: OrderStatus = OrderStatus.PENDIENTE
    payment_method: Optional[PaymentMethod] = None
    delivery_address: Optional[str] = None
    delivery_fee: float = 0.0
    notes: Optional[str] = None
    qr_code: Optional[str] = None  # QR para pago
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    delivered_at: Optional[datetime] = None

class OrderCreate(BaseModel):
    customer_id: str
    items: List[dict]  # {"product_id": str, "quantity": int}
    delivery_address: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    notes: Optional[str] = None

class WhatsAppMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phone: str
    message: str
    is_incoming: bool = True
    response: Optional[str] = None
    command: Optional[str] = None
    processed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SocialMediaPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    platform: str  # facebook, instagram, tiktok, whatsapp
    content: str
    image_url: Optional[str] = None
    product_id: Optional[str] = None
    engagement: dict = {}  # likes, shares, comments
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DashboardStats(BaseModel):
    total_products: int
    low_stock_alerts: int
    total_orders: int
    pending_orders: int
    today_sales: float
    monthly_sales: float
    total_customers: int
    whatsapp_messages: int

# Helper functions
def calculate_taxes(subtotal: float):
    iva = subtotal * 0.13  # 13% IVA
    it = subtotal * 0.03   # 3% IT
    return iva, it

def calculate_margin(cost_price: float, sale_price: float):
    return ((sale_price - cost_price) / cost_price * 100) if cost_price > 0 else 0

# API Routes

@api_router.get("/")
async def root():
    return {"message": "Tambar Express API - Sistema de Gestión Empresarial"}

# Dashboard
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    total_products = await db.products.count_documents({})
    low_stock_alerts = await db.products.count_documents({"$expr": {"$lt": ["$stock", "$min_stock"]}})
    total_orders = await db.orders.count_documents({})
    pending_orders = await db.orders.count_documents({"status": "pendiente"})
    total_customers = await db.customers.count_documents({})
    whatsapp_messages = await db.whatsapp_messages.count_documents({})
    
    # Today's sales
    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    today_end = datetime.combine(today, datetime.max.time()).replace(tzinfo=timezone.utc)
    
    today_orders = await db.orders.find({
        "created_at": {"$gte": today_start, "$lte": today_end},
        "status": {"$ne": "cancelado"}
    }).to_list(1000)
    today_sales = sum(order.get("total", 0) for order in today_orders)
    
    # Monthly sales (current month)
    monthly_orders = await db.orders.find({
        "created_at": {"$gte": datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)},
        "status": {"$ne": "cancelado"}
    }).to_list(1000)
    monthly_sales = sum(order.get("total", 0) for order in monthly_orders)
    
    return DashboardStats(
        total_products=total_products,
        low_stock_alerts=low_stock_alerts,
        total_orders=total_orders,
        pending_orders=pending_orders,
        today_sales=today_sales,
        monthly_sales=monthly_sales,
        total_customers=total_customers,
        whatsapp_messages=whatsapp_messages
    )

# Products
@api_router.get("/products", response_model=List[Product])
async def get_products():
    products = await db.products.find().to_list(1000)
    return [Product(**product) for product in products]

@api_router.post("/products", response_model=Product)
async def create_product(product: ProductCreate):
    product_dict = product.dict()
    product_dict["margin"] = calculate_margin(product.cost_price, product.sale_price)
    product_obj = Product(**product_dict)
    await db.products.insert_one(product_obj.dict())
    return product_obj

@api_router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product: ProductCreate):
    product_dict = product.dict()
    product_dict["margin"] = calculate_margin(product.cost_price, product.sale_price)
    await db.products.update_one({"id": product_id}, {"$set": product_dict})
    updated_product = await db.products.find_one({"id": product_id})
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**updated_product)

@api_router.get("/products/low-stock")
async def get_low_stock_products():
    products = await db.products.find({"$expr": {"$lt": ["$stock", "$min_stock"]}}).to_list(1000)
    return [Product(**product) for product in products]

# Customers
@api_router.get("/customers", response_model=List[Customer])
async def get_customers():
    customers = await db.customers.find().to_list(1000)
    return [Customer(**customer) for customer in customers]

@api_router.post("/customers", response_model=Customer)
async def create_customer(customer: CustomerCreate):
    customer_obj = Customer(**customer.dict())
    await db.customers.insert_one(customer_obj.dict())
    return customer_obj

# Orders
@api_router.get("/orders", response_model=List[Order])
async def get_orders():
    orders = await db.orders.find().sort("created_at", -1).to_list(1000)
    return [Order(**order) for order in orders]

@api_router.post("/orders", response_model=Order)
async def create_order(order: OrderCreate):
    # Get customer
    customer = await db.customers.find_one({"id": order.customer_id})
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Calculate order totals
    order_items = []
    subtotal = 0
    
    for item in order.items:
        product = await db.products.find_one({"id": item["product_id"]})
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item['product_id']} not found")
        
        if product["stock"] < item["quantity"]:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for {product['name']}")
        
        item_total = product["sale_price"] * item["quantity"]
        order_items.append(OrderItem(
            product_id=item["product_id"],
            product_name=product["name"],
            quantity=item["quantity"],
            unit_price=product["sale_price"],
            total_price=item_total
        ))
        subtotal += item_total
        
        # Update stock
        await db.products.update_one(
            {"id": item["product_id"]}, 
            {"$inc": {"stock": -item["quantity"]}}
        )
    
    iva, it = calculate_taxes(subtotal)
    total = subtotal + iva + it + order.delivery_fee if hasattr(order, 'delivery_fee') else subtotal + iva + it
    
    # Generate QR code for payment (simulated)
    qr_code = f"qr_payment_{uuid.uuid4().hex[:8]}_{int(total)}"
    
    order_obj = Order(
        customer_id=order.customer_id,
        customer_name=customer["name"],
        customer_phone=customer["phone"],
        items=order_items,
        subtotal=subtotal,
        iva=iva,
        it=it,
        total=total,
        delivery_address=order.delivery_address,
        payment_method=order.payment_method,
        notes=order.notes,
        qr_code=qr_code
    )
    
    await db.orders.insert_one(order_obj.dict())
    
    # Update customer loyalty points (1 point per 10 Bs)
    points = int(total / 10)
    await db.customers.update_one(
        {"id": order.customer_id},
        {"$inc": {"total_purchases": total, "loyalty_points": points}}
    )
    
    return order_obj

@api_router.put("/orders/{order_id}/status")
async def update_order_status(order_id: str, status: OrderStatus):
    update_data = {"status": status.value}
    if status == OrderStatus.ENTREGADO:
        update_data["delivered_at"] = datetime.now(timezone.utc)
    
    await db.orders.update_one({"id": order_id}, {"$set": update_data})
    updated_order = await db.orders.find_one({"id": order_id})
    if not updated_order:
        raise HTTPException(status_code=404, detail="Order not found")
    return Order(**updated_order)

# WhatsApp Simulation
@api_router.get("/whatsapp/messages", response_model=List[WhatsAppMessage])
async def get_whatsapp_messages():
    messages = await db.whatsapp_messages.find().sort("created_at", -1).limit(50).to_list(50)
    return [WhatsAppMessage(**msg) for msg in messages]

@api_router.post("/whatsapp/send")
async def send_whatsapp_message(phone: str, message: str):
    msg = WhatsAppMessage(
        phone=phone,
        message=message,
        is_incoming=False,
        processed=True
    )
    await db.whatsapp_messages.insert_one(msg.dict())
    return {"status": "sent", "message": "Mensaje enviado via WhatsApp Business"}

@api_router.post("/whatsapp/process")
async def process_whatsapp_command(phone: str, message: str):
    # Simulate incoming WhatsApp message
    msg = WhatsAppMessage(phone=phone, message=message)
    
    response = ""
    command = ""
    
    # Process commands
    if message.startswith("/"):
        parts = message.split()
        command = parts[0]
        
        if command == "/stock" and len(parts) > 1:
            product_name = " ".join(parts[1:])
            product = await db.products.find_one({"name": {"$regex": product_name, "$options": "i"}})
            if product:
                response = f"📦 Stock de {product['name']}: {product['stock']} unidades\n💰 Precio: Bs. {product['sale_price']}"
            else:
                response = f"❌ Producto '{product_name}' no encontrado"
        
        elif command == "/pedido":
            response = "🛒 Para hacer un pedido, use: /pedido [producto] [cantidad]\nEjemplo: /pedido Cerveza Pilsener 6"
        
        elif command == "/reporte" and len(parts) > 1:
            report_type = parts[1]
            if report_type == "ventas":
                today_orders = await db.orders.count_documents({
                    "created_at": {"$gte": datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)}
                })
                response = f"📊 Reporte de Ventas de Hoy:\n🛍️ Pedidos: {today_orders}\n💰 Ingresos: Calculando..."
            else:
                response = "📊 Reportes disponibles:\n- /reporte ventas\n- /reporte inventario"
        
        elif command == "/menu":
            response = """🍺 TAMBAR EXPRESS - MENÚ DE COMANDOS
            
📦 INVENTARIO:
/stock [producto] - Consultar stock
/productos - Ver catálogo completo

🛒 PEDIDOS:
/pedido [producto] [cantidad] - Hacer pedido
/mis_pedidos - Ver mis pedidos

📊 REPORTES:
/reporte ventas - Ventas del día
/reporte inventario - Estado de inventario

📞 CONTACTO:
/contacto - Información de contacto
/horarios - Horarios de atención"""
        
        else:
            response = "❓ Comando no reconocido. Escriba /menu para ver comandos disponibles."
    
    else:
        response = f"¡Hola! 👋 Bienvenido a Tambar Express.\nEscriba /menu para ver los comandos disponibles."
    
    msg.response = response
    msg.command = command
    msg.processed = True
    
    await db.whatsapp_messages.insert_one(msg.dict())
    return {"response": response, "command": command}

# Social Media
@api_router.get("/social-media/posts", response_model=List[SocialMediaPost])
async def get_social_media_posts():
    posts = await db.social_media_posts.find().sort("created_at", -1).to_list(100)
    return [SocialMediaPost(**post) for post in posts]

@api_router.post("/social-media/create-ad")
async def create_social_media_ad(platform: str, product_id: Optional[str] = None):
    content = ""
    image_url = ""
    
    if product_id:
        product = await db.products.find_one({"id": product_id})
        if product:
            content = f"""🔥 ¡OFERTA ESPECIAL! 🔥
            
{product['name']}
💰 Solo Bs. {product['sale_price']}
📦 Stock limitado: {product['stock']} unidades

🚚 Delivery gratis en La Paz
📱 Pedidos por WhatsApp: 70000000

#TambarExpress #Licoreria #Bolivia #Delivery"""
            image_url = product.get("image_url", "")
    else:
        content = """🍺 TAMBAR EXPRESS 🥃
        
¡La mejor licorería de Bolivia!
🚚 Delivery 24/7
💳 Aceptamos todos los métodos de pago
📱 Pedidos por WhatsApp

#TambarExpress #Licoreria #Bolivia"""
    
    post = SocialMediaPost(
        platform=platform,
        content=content,
        image_url=image_url,
        product_id=product_id,
        engagement={"likes": 0, "shares": 0, "comments": 0}
    )
    
    await db.social_media_posts.insert_one(post.dict())
    
    return {
        "status": "success",
        "message": f"Anuncio creado para {platform}",
        "post": post
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()