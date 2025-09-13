import sqlite3
import os
from django.conf import settings

# Conectar a la base de datos
db_path = settings.DATABASES['default']['NAME']
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar tabla
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pedidos_itempedido'")
table_exists = cursor.fetchone()
print(f"Tabla pedidos_itempedido existe: {bool(table_exists)}")

# Verificar columnas
if table_exists:
    cursor.execute("PRAGMA table_info(pedidos_itempedido)")
    columns = cursor.fetchall()
    print("\nColumnas de pedidos_itempedido:")
    for col in columns:
        print(f"  {col[1]} - {col[2]}")
    
    # Buscar la columna específica
    column_names = [col[1] for col in columns]
    has_column = 'descripcion_personalizada' in column_names
    print(f"\n¿descripcion_personalizada existe? {has_column}")

conn.close()