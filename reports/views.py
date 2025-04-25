# reports/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.html import escape
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Count
import logging

from .models import Report
from .forms import ReportForm
from products.models import Product

User = get_user_model()
logger = logging.getLogger(__name__)

@login_required
def report_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 자신의 상품은 신고할 수 없음
    if product.seller == request.user:
        messages.error(request, '자신의 상품은 신고할 수 없습니다.')
        return redirect('products:product_detail', product_id=product_id)
    
    # 이미 신고한 상품인지 확인
    if Report.objects.filter(reporter=request.user, target_product=product, status__in=['pending', 'approved']).exists():
        messages.warning(request, '이미 신고한 상품입니다.')
        return redirect('products:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            # XSS 방지
            detail = escape(form.cleaned_data.get('detail'))
            
            report = form.save(commit=False)
            report.reporter = request.user
            report.target_product = product
            report.detail = detail
            report.save()
            
            # 로깅
            logger.info(f"Product reported: '{product.title}' by user {request.user.username}")
            
            # 일정 횟수 이상 신고되면 상품 차단
            report_count = Report.objects.filter(
                target_product=product, 
                status__in=['pending', 'approved']
            ).count()
            
            if report_count >= 5:  # 5회 이상 신고되면 자동 차단
                product.status = 'blocked'
                product.save()
                logger.warning(f"Product automatically blocked: '{product.title}' due to {report_count} reports")
                messages.warning(request, '이 상품은 다수의 신고로 인해 차단되었습니다.')
            else:
                messages.success(request, '신고가 접수되었습니다.')
            
            return redirect('products:product_detail', product_id=product_id)
    else:
        form = ReportForm()
    
    return render(request, 'reports/report_form.html', {
        'form': form,
        'product': product,
        'report_type': 'product'
    })

@login_required
def report_user(request, user_id):
    user_to_report = get_object_or_404(User, id=user_id)
    
    # 자기 자신은 신고할 수 없음
    if user_to_report == request.user:
        messages.error(request, '자기 자신을 신고할 수 없습니다.')
        return redirect('accounts:profile')
    
    # 이미 신고한 사용자인지 확인
    if Report.objects.filter(reporter=request.user, target_user=user_to_report, status__in=['pending', 'approved']).exists():
        messages.warning(request, '이미 신고한 사용자입니다.')
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            # XSS 방지
            detail = escape(form.cleaned_data.get('detail'))
            
            report = form.save(commit=False)
            report.reporter = request.user
            report.target_user = user_to_report
            report.detail = detail
            report.save()
            
            # 로깅
            logger.info(f"User reported: '{user_to_report.username}' by user {request.user.username}")
            
            # 일정 횟수 이상 신고되면 사용자 휴면 처리
            report_count = Report.objects.filter(
                target_user=user_to_report, 
                status__in=['pending', 'approved']
            ).count()
            
            if report_count >= 5:  # 5회 이상 신고되면 자동 휴면
                user_to_report.is_dormant = True
                user_to_report.save()
                logger.warning(f"User automatically set to dormant: '{user_to_report.username}' due to {report_count} reports")
            
            messages.success(request, '신고가 접수되었습니다.')
            return redirect('products:product_list')
    else:
        form = ReportForm()
    
    return render(request, 'reports/report_form.html', {
        'form': form,
        'user_to_report': user_to_report,
        'report_type': 'user'
    })

@login_required
def my_reports(request):
    # 자신이 신고한 내역 조회
    reports = Report.objects.filter(reporter=request.user)
    
    return render(request, 'reports/my_reports.html', {
        'reports': reports
    })

# 관리자 전용 기능들
@login_required
def admin_report_list(request):
    if not request.user.is_staff:
        messages.error(request, '관리자만 접근할 수 있습니다.')
        return redirect('core:home')
    
    # 필터링
    status_filter = request.GET.get('status', 'pending')
    if status_filter == 'all':
        reports = Report.objects.all()
    else:
        reports = Report.objects.filter(status=status_filter)
    
    # 통계 정보
    stats = {
        'total': Report.objects.count(),
        'pending': Report.objects.filter(status='pending').count(),
        'approved': Report.objects.filter(status='approved').count(),
        'rejected': Report.objects.filter(status='rejected').count(),
    }
    
    return render(request, 'reports/admin_report_list.html', {
        'reports': reports,
        'status_filter': status_filter,
        'stats': stats
    })

@login_required
def admin_report_detail(request, report_id):
    if not request.user.is_staff:
        messages.error(request, '관리자만 접근할 수 있습니다.')
        return redirect('core:home')
    
    report = get_object_or_404(Report, id=report_id)
    
    return render(request, 'reports/admin_report_detail.html', {
        'report': report
    })

@login_required
def admin_report_action(request, report_id):
    if not request.user.is_staff:
        messages.error(request, '관리자만 접근할 수 있습니다.')
        return redirect('core:home')
    
    if request.method != 'POST':
        return redirect('reports:admin_report_list')
    
    report = get_object_or_404(Report, id=report_id)
    action = request.POST.get('action')
    
    if action not in ['approve', 'reject']:
        messages.error(request, '잘못된 요청입니다.')
        return redirect('reports:admin_report_detail', report_id=report_id)
    
    # 신고 처리
    report.status = 'approved' if action == 'approve' else 'rejected'
    report.processed_at = timezone.now()
    report.processed_by = request.user
    report.save()
    
    # 신고 승인 시 추가 조치
    if action == 'approve':
        if report.target_product:
            # 상품 차단
            report.target_product.status = 'blocked'
            report.target_product.save()
            logger.warning(f"Product blocked by admin: '{report.target_product.title}'")
        
        elif report.target_user:
            # 사용자 신고 횟수 증가 및 필요 시 휴면 처리
            report.target_user.report_count += 1
            if report.target_user.report_count >= 5:
                report.target_user.is_dormant = True
                logger.warning(f"User set to dormant by admin: '{report.target_user.username}'")
            report.target_user.save()
    
    messages.success(request, f'신고가 {report.get_status_display()}되었습니다.')
    return redirect('reports:admin_report_list')