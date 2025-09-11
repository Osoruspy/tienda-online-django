from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)
    slug = models.SlugField(max_length=100, unique=True)
    activa = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('productos:por_categoria', args=[self.slug])

class Producto(models.Model):
    ESTADO_CHOICES = (
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('agotado', 'Agotado'),
    )
    
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_oferta = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    sku = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    imagen_principal = models.ImageField(upload_to='productos/', null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    destacado = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return f"{self.nombre} - ${self.precio}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('productos:detalle', args=[self.slug])
    
    def en_oferta(self):
        return self.precio_oferta is not None and self.precio_oferta < self.precio
    
    def precio_actual(self):
        return self.precio_oferta if self.en_oferta() else self.precio
    
    def disponible(self):
        return self.stock > 0 and self.estado == 'activo'

class ImagenProducto(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='productos/galeria/')
    orden = models.PositiveIntegerField(default=0)
    es_principal = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['orden']
    
    def __str__(self):
        return f"Imagen de {self.producto.nombre}"

class Inventario(models.Model):
    producto = models.OneToOneField(Producto, on_delete=models.CASCADE, related_name='inventario')
    stock_minimo = models.PositiveIntegerField(default=5)
    stock_maximo = models.PositiveIntegerField(default=100)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Inventario de {self.producto.nombre}"
    
    def necesita_reabastecimiento(self):
        return self.producto.stock <= self.stock_minimo