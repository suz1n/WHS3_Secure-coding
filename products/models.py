# products/models.py
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
import os

def product_image_path(instance, filename):
    # 파일명 보안을 위한 난수화 처리
    from uuid import uuid4
    ext = filename.split('.')[-1]
    filename = f"{uuid4().hex}.{ext}"
    return os.path.join('product_images', filename)

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Product(models.Model):
    STATUS_CHOICES = (
        ('available', '판매중'),
        ('reserved', '예약중'),
        ('sold', '판매완료'),
        ('blocked', '차단됨'),
    )
    
    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(100000000)])
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to=product_image_path)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        # 상품 삭제 시 이미지 함께 삭제
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)