# users/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    intro = models.TextField(blank=True, null=True, help_text=_("User introduction"))
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    is_dormant = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.username

# products/models.py
from django.db import models
from django.conf import settings

class Product(models.Model):
    STATUS_CHOICES = (
        ('available', '판매중'),
        ('reserved', '예약중'),
        ('sold', '판매완료'),
        ('blocked', '차단됨'),
    )
    
    title = models.CharField(max_length=50)
    description = models.TextField()
    price = models.PositiveIntegerField()
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images/')
    
    def __str__(self):
        return self.title
        
# reports/models.py
from django.db import models
from django.conf import settings
from products.models import Product

class Report(models.Model):
    REASON_CHOICES = (
        ('prohibited', '금지된 상품'),
        ('counterfeit', '위조품/가품'),
        ('misleading', '상품 정보 불일치'),
        ('fraud', '사기 의심'),
        ('other', '기타'),
    )
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reporter')
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                   related_name='reported_user', null=True, blank=True)
    target_product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    detail = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    
# chat/models.py
from django.db import models
from django.conf import settings

class ChatRoom(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"ChatRoom {self.id}"

class Message(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"