#!/usr/bin/env python3
"""
Script para agregar datos de prueba al sistema Tambar Express
"""
import asyncio
import os
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import uuid

# Load environment
from dotenv import load_dotenv
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Sample data
SAMPLE_PRODUCTS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Cerveza Pilsener 330ml",
        "description": "Cerveza nacional boliviana, botella de vidrio 330ml",
        "cost_price": 3.50,
        "sale_price": 6.00,
        "margin": 71.43,
        "stock": 48,
        "min_stock": 20,
        "supplier": "Cervecería Boliviana Nacional",
        "category": "cervezas",
        "image_url": "https://images.unsplash.com/photo-1608270586620-248524c67de9?w=300",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Vino Kohlberg Tinto",
        "description": "Vino tinto boliviano de Tarija, cosecha 2022",
        "cost_price": 45.00,
        "sale_price": 75.00,
        "margin": 66.67,
        "stock": 12,
        "min_stock": 5,
        "supplier": "Bodegas Kohlberg",
        "category": "vinos",
        "image_url": "https://images.unsplash.com/photo-1506377247377-2a5b3b417ebb?w=300",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Singani Casa Real",
        "description": "Singani boliviano premium, botella 750ml",
        "cost_price": 65.00,
        "sale_price": 95.00,
        "margin": 46.15,
        "stock": 8,
        "min_stock": 10,
        "supplier": "Casa Real",
        "category": "licores",
        "image_url": "https://images.unsplash.com/photo-1569529465841-dfecdab7503b?w=300",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Whisky Johnnie Walker Red",
        "description": "Whisky escocés Red Label, 750ml",
        "cost_price": 120.00,
        "sale_price": 180.00,
        "margin": 50.00,
        "stock": 6,
        "min_stock": 8,
        "supplier": "Importadora Boliviana",
        "category": "whiskey",
        "image_url": "https://images.unsplash.com/photo-1527281400683-1aae777175f8?w=300",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Vodka Smirnoff",
        "description": "Vodka premium importado, 750ml",
        "cost_price": 85.00,
        "sale_price": 130.00,
        "margin": 52.94,
        "stock": 15,
        "min_stock": 10,
        "supplier": "Importadora Premium",
        "category": "vodka",
        "image_url": "https://images.unsplash.com/photo-1551538827-9c037cb4f32a?w=300",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Ron Bacardi Superior",
        "description": "Ron blanco caribeño, 750ml",
        "cost_price": 70.00,
        "sale_price": 110.00,
        "margin": 57.14,
        "stock": 9,
        "min_stock": 12,
        "supplier": "Distribuidora Caribe",
        "category": "ron",
        "image_url": "https://images.unsplash.com/photo-1514362545857-3bc16c4c7d1b?w=300",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Cerveza Corona Extra",
        "description": "Cerveza mexicana importada, 355ml",
        "cost_price": 8.00,
        "sale_price": 14.00,
        "margin": 75.00,
        "stock": 24,
        "min_stock": 15,
        "supplier": "Importadora México",
        "category": "cervezas",
        "image_url": "https://images.unsplash.com/photo-1608032664297-6195e2a39e30?w=300",
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Pisco Control C",
        "description": "Pisco peruano premium, 750ml",
        "cost_price": 55.00,
        "sale_price": 85.00,
        "margin": 54.55,
        "stock": 7,
        "min_stock": 10,
        "supplier": "Importadora Perú",
        "category": "licores",
        "image_url": "https://images.unsplash.com/photo-1582821456916-1a4e2c9b5f86?w=300",
        "created_at": datetime.now(timezone.utc)
    }
]

SAMPLE_CUSTOMERS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Carlos Mendoza",
        "phone": "59170001234",
        "email": "carlos@email.com",
        "address": "Zona Sur, La Paz",
        "total_purchases": 450.50,
        "loyalty_points": 45,
        "preferred_products": ["Cerveza Pilsener 330ml", "Vino Kohlberg Tinto"],
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "María García",
        "phone": "59170005678",
        "email": "maria@email.com", 
        "address": "Sopocachi, La Paz",
        "total_purchases": 320.00,
        "loyalty_points": 32,
        "preferred_products": ["Whisky Johnnie Walker Red"],
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Roberto Silva",
        "phone": "59170009999",
        "email": "roberto@email.com",
        "address": "Centro, La Paz",
        "total_purchases": 180.75,
        "loyalty_points": 18,
        "preferred_products": ["Singani Casa Real", "Ron Bacardi Superior"],
        "created_at": datetime.now(timezone.utc)
    }
]

SAMPLE_WHATSAPP_MESSAGES = [
    {
        "id": str(uuid.uuid4()),
        "phone": "59170001234",
        "message": "/menu",
        "is_incoming": True,
        "response": """🍺 TAMBAR EXPRESS - MENÚ DE COMANDOS
            
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
/horarios - Horarios de atención""",
        "command": "/menu",
        "processed": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "phone": "59170005678",
        "message": "/stock Cerveza Pilsener",
        "is_incoming": True,
        "response": "📦 Stock de Cerveza Pilsener 330ml: 48 unidades\n💰 Precio: Bs. 6.0",
        "command": "/stock",
        "processed": True,
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "phone": "59170009999",
        "message": "Hola, buenos días",
        "is_incoming": True,
        "response": "¡Hola! 👋 Bienvenido a Tambar Express.\nEscriba /menu para ver los comandos disponibles.",
        "command": None,
        "processed": True,
        "created_at": datetime.now(timezone.utc)
    }
]

SAMPLE_SOCIAL_POSTS = [
    {
        "id": str(uuid.uuid4()),
        "platform": "facebook",
        "content": """🔥 ¡OFERTA ESPECIAL! 🔥

Singani Casa Real
💰 Solo Bs. 95.0
📦 Stock limitado: 8 unidades

🚚 Delivery gratis en La Paz
📱 Pedidos por WhatsApp: 70000000

#TambarExpress #Licoreria #Bolivia #Delivery""",
        "image_url": "https://images.unsplash.com/photo-1569529465841-dfecdab7503b?w=300",
        "product_id": None,
        "engagement": {"likes": 15, "shares": 3, "comments": 2},
        "created_at": datetime.now(timezone.utc)
    },
    {
        "id": str(uuid.uuid4()),
        "platform": "instagram",
        "content": """🍺 TAMBAR EXPRESS 🥃

¡La mejor licorería de Bolivia!
🚚 Delivery 24/7
💳 Aceptamos todos los métodos de pago
📱 Pedidos por WhatsApp

#TambarExpress #Licoreria #Bolivia""",
        "image_url": "",
        "product_id": None,
        "engagement": {"likes": 28, "shares": 5, "comments": 7},
        "created_at": datetime.now(timezone.utc)
    }
]

async def seed_database():
    """Insertar datos de prueba en la base de datos"""
    
    print("🌱 Iniciando inserción de datos de prueba...")
    
    # Clear existing data
    await db.products.delete_many({})
    await db.customers.delete_many({})
    await db.whatsapp_messages.delete_many({})
    await db.social_media_posts.delete_many({})
    print("🗑️ Datos anteriores eliminados")
    
    # Insert products
    await db.products.insert_many(SAMPLE_PRODUCTS)
    print(f"📦 {len(SAMPLE_PRODUCTS)} productos insertados")
    
    # Insert customers
    await db.customers.insert_many(SAMPLE_CUSTOMERS)
    print(f"👥 {len(SAMPLE_CUSTOMERS)} clientes insertados")
    
    # Insert WhatsApp messages
    await db.whatsapp_messages.insert_many(SAMPLE_WHATSAPP_MESSAGES)
    print(f"💬 {len(SAMPLE_WHATSAPP_MESSAGES)} mensajes de WhatsApp insertados")
    
    # Insert social media posts
    await db.social_media_posts.insert_many(SAMPLE_SOCIAL_POSTS)
    print(f"📱 {len(SAMPLE_SOCIAL_POSTS)} publicaciones de redes sociales insertadas")
    
    print("✅ Datos de prueba insertados exitosamente!")
    print("\n📊 Resumen:")
    print(f"   • Productos: {len(SAMPLE_PRODUCTS)}")
    print(f"   • Clientes: {len(SAMPLE_CUSTOMERS)}")
    print(f"   • Mensajes WhatsApp: {len(SAMPLE_WHATSAPP_MESSAGES)}")
    print(f"   • Posts Redes Sociales: {len(SAMPLE_SOCIAL_POSTS)}")

if __name__ == "__main__":
    asyncio.run(seed_database())