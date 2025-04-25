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
        ('harassment', '괴롭힘/부적절한 행동'),
        ('other', '기타'),
    )
    
    STATUS_CHOICES = (
        ('pending', '처리 대기'),
        ('approved', '승인됨'),
        ('rejected', '거부됨'),
    )
    
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reports_filed')
    target_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                   related_name='reports_received', null=True, blank=True)
    target_product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    detail = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                     null=True, blank=True, related_name='processed_reports')
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        if self.target_product:
            return f"Report on product: {self.target_product.title}"
        elif self.target_user:
            return f"Report on user: {self.target_user.username}"
        return f"Report #{self.id}"
    
    def save(self, *args, **kwargs):
        # 한 번에 타겟 유저와 타겟 제품을 둘 다 설정할 수 없도록
        if self.target_user and self.target_product:
            raise ValueError("Cannot report both a user and a product in the same report")
        super().save(*args, **kwargs)