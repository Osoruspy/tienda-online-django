import os
import django
from django.core.files import File

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tienda.settings')
django.setup()

from productos.models import Categoria, Producto, Inventario
from django.contrib.auth import get_user_model

Usuario = get_user_model()

def crear_datos_prueba():
    print("Creando datos de prueba...")
    
    # Crear categorías
    categorias_data = [
        {'nombre': 'Electrónicos', 'descripcion': 'Dispositivos electrónicos y gadgets'},
        {'nombre': 'Ropa', 'descripcion': 'Ropa para hombre, mujer y niños'},
        {'nombre': 'Hogar', 'descripcion': 'Productos para el hogar'},
        {'nombre': 'Deportes', 'descripcion': 'Artículos deportivos'},
        {'nombre': 'Libros', 'descripcion': 'Libros de todo tipo'},
    ]
    
    categorias = {}
    for cat_data in categorias_data:
        categoria, created = Categoria.objects.get_or_create(
            nombre=cat_data['nombre'],
            defaults=cat_data
        )
        categorias[cat_data['nombre']] = categoria
        print(f"Categoría {'creada' if created else 'existente'}: {categoria.nombre}")
    
    # Crear productos de ejemplo
    productos_data = [
        {
            'nombre': 'Smartphone Samsung Galaxy S23',
            'descripcion': 'El último smartphone de Samsung con cámara de 108MP y 256GB de almacenamiento',
            'precio': 899.99,
            'precio_oferta': 799.99,
            'categoria': categorias['Electrónicos'],
            'sku': 'SM-GS23-001',
            'stock': 25,
            'estado': 'activo',
            'destacado': True
        },
        {
            'nombre': 'Laptop HP Pavilion',
            'descripcion': 'Laptop con procesador Intel i7, 16GB RAM, 512GB SSD',
            'precio': 1299.99,
            'categoria': categorias['Electrónicos'],
            'sku': 'HP-PAV-002',
            'stock': 15,
            'estado': 'activo',
            'destacado': True
        },
        {
            'nombre': 'Camiseta Nike Dry-Fit',
            'descripcion': 'Camiseta deportiva de alta calidad, tecnología dry-fit',
            'precio': 39.99,
            'precio_oferta': 29.99,
            'categoria': categorias['Ropa'],
            'sku': 'NK-DF-003',
            'stock': 50,
            'estado': 'activo',
            'destacado': False
        },
        {
            'nombre': 'Zapatillas Adidas Running',
            'descripcion': 'Zapatillas ideales para running, cómodas y ligeras',
            'precio': 89.99,
            'categoria': categorias['Deportes'],
            'sku': 'AD-RUN-004',
            'stock': 30,
            'estado': 'activo',
            'destacado': True
        },
        {
            'nombre': 'Sartén Antiadherente',
            'descripcion': 'Sartén de 28cm con revestimiento antiadherente de calidad',
            'precio': 49.99,
            'categoria': categorias['Hogar'],
            'sku': 'SAT-AN-005',
            'stock': 40,
            'estado': 'activo',
            'destacado': False
        },
        {
            'nombre': 'El Señor de los Anillos - Trilogía',
            'descripcion': 'La famosa trilogía de J.R.R. Tolkien en edición especial',
            'precio': 59.99,
            'precio_oferta': 49.99,
            'categoria': categorias['Libros'],
            'sku': 'LOTR-006',
            'stock': 0,  # Producto agotado
            'estado': 'agotado',
            'destacado': False
        },
        {
            'nombre': 'Auriculares Sony WH-1000XM4',
            'descripcion': 'Auriculares inalámbricos con cancelación de ruido',
            'precio': 349.99,
            'categoria': categorias['Electrónicos'],
            'sku': 'SONY-WH-007',
            'stock': 8,
            'estado': 'activo',
            'destacado': True
        },
        {
            'nombre': 'Balón de Fútbol Adidas',
            'descripcion': 'Balón oficial tamaño 5, ideal para competencias',
            'precio': 29.99,
            'categoria': categorias['Deportes'],
            'sku': 'AD-FB-008',
            'stock': 20,
            'estado': 'activo',
            'destacado': False
        }
    ]
    
    for prod_data in productos_data:
        producto, created = Producto.objects.get_or_create(
            sku=prod_data['sku'],
            defaults=prod_data
        )
        print(f"Producto {'creado' if created else 'existente'}: {producto.nombre}")
        
        # Crear inventario automáticamente
        if created:
            Inventario.objects.create(
                producto=producto,
                stock_minimo=5,
                stock_maximo=100
            )
    
    print("¡Datos de prueba creados exitosamente!")

if __name__ == '__main__':
    crear_datos_prueba()