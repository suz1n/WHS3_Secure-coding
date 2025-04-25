# reports/urls.py
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('product/<int:product_id>/', views.report_product, name='report_product'),
    path('user/<int:user_id>/', views.report_user, name='report_user'),
    path('my-reports/', views.my_reports, name='my_reports'),
    
    # 관리자 기능
    path('admin/', views.admin_report_list, name='admin_report_list'),
    path('admin/<int:report_id>/', views.admin_report_detail, name='admin_report_detail'),
    path('admin/<int:report_id>/action/', views.admin_report_action, name='admin_report_action'),
]

# reports/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import escape
from django.http import JsonResponse
from .models import Report
from .forms import ReportForm
from products.models import Product
from django.contrib.auth import get_user_model
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

User = get_user_model()

@login_required
def report_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 자신의 상품에 대한 신고 방지
    if product.seller == request.user:
        messages.error(request, "자신의 상품은 신고할 수 없습니다.")
        return redirect('products:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data.get('reason')
            detail = escape(form.cleaned_data.get('detail'))
            
            # 신고 저장
            report = Report(
                reporter=request.user,
                target_product=product,
                reason=reason,
                detail=detail
            )
            report.save()
            
            # 로깅
            logger.info(f"Product reported: {product.title} (ID: {product.id}) by {request.user.username}")
            
            messages.success(request, "신고가 접수되었습니다.")
            
            # 신고가 일정 횟수 이상이면 상품 차단
            report_count = Report.objects.filter(target_product=product).count()
            if report_count >= 5:  # 예시: 5회 이상 신고 시 차단
                product.status = 'blocked'
                product.save()
                logger.warning(f"Product blocked due to multiple reports: {product.title} (ID: {product.id})")
            
            return redirect('products:product_detail', product_id=product_id)
    else:
        form = ReportForm()
    
    return render(request, 'reports/report_product.html', {
        'form': form,
        'product': product
    })

@login_required
def report_user(request, user_id):
    user_to_report = get_object_or_404(User, id=user_id)
    
    # 자기 자신에 대한 신고 방지
    if user_to_report == request.user:
        messages.error(request, "자기 자신은 신고할 수 없습니다.")
        return redirect('products:home')
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            reason = form.cleaned_data.get('reason')
            detail = escape(form.cleaned_data.get('detail'))
            
            # 신고 저장
            report = Report(
                reporter=request.user,
                target_user=user_to_report,
                reason=reason,
                detail=detail
            )
            report.save()
            
            # 로깅
            logger.info(f"User reported: {user_to_report.username} (ID: {user_to_report.id}) by {request.user.username}")
            
            messages.success(request, "신고가 접수되었습니다.")
            
            # 신고가 일정 횟수 이상이면 사용자 휴면 처리
            report_count = Report.objects.filter(target_user=user_to_report).count()
            if report_count >= 5:  # 예시: 5회 이상 신고 시 휴면
                user_to_report.is_dormant = True
                user_to_report.save()
                logger.warning(f"User set to dormant due to multiple reports: {user_to_report.username} (ID: {user_to_report.id})")
            
            return redirect('products:home')
    else:
        form = ReportForm()
    
    return render(request, 'reports/report_user.html', {
        'form': form,
        'user_to_report': user_to_report
    })