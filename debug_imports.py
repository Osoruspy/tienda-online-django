import sys
print("Módulos cargados relacionados con carrito:")
for module in sys.modules:
    if 'carrito' in module or 'pedidos' in module:
        print(f"  {module}")

print("\nBuscando importaciones problemáticas...")