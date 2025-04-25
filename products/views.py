# products/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.html import escape
from django.http import JsonResponse
from django.core.paginator import Paginator
import logging

from .models import Product, Category
from .forms import ProductForm
from reports.forms import ReportForm

logger = logging.getLogger(__name__)

def product_list(request):
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search', '')
    
    products = Product.objects.filter(status='available')
    
    # 카테고리 필터링
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # 검색 필터링
    if search_query:
        # XSS 방지
        search_query = escape(search_query)
        
        if len(search_query) < 2:
            messages.info(request, '검색어는 2글자 이상 입력해주세요.')
        else:
            products = products.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
            
            # 검색 로그
            logger.info(f"Product search: '{search_query}' - Results: {products.count()}")
    
    # 페이지네이션
    paginator = Paginator(products, 12)  # 페이지당 12개 상품
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 모든 카테고리 가져오기
    categories = Category.objects.all()
    
    return render(request, 'products/product_list.html', {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 삭제되거나 차단된 상품은 관리자나 판매자만 볼 수 있음
    if product.status == 'blocked' and not (request.user.is_staff or request.user == product.seller):
        messages.error(request, '이 상품은 차단되었습니다.')
        return redirect('products:product_list')
    
    # 조회수 증가 (중복 방지 로직)
    session_key = f'viewed_product_{product_id}'
    if not request.session.get(session_key, False):
        product.views += 1
        product.save()
        request.session[session_key] = True
    
    # 판매자의 다른 상품
    seller_other_products = Product.objects.filter(
        seller=product.seller, 
        status='available'
    ).exclude(id=product_id)[:4]
    
    # 신고 폼
    report_form = ReportForm()
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'seller_other_products': seller_other_products,
        'report_form': report_form
    })

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # XSS 방지
            title = escape(form.cleaned_data.get('title'))
            description = escape(form.cleaned_data.get('description'))
            
            product = form.save(commit=False)
            product.seller = request.user
            product.title = title
            product.description = description
            product.save()
            
            logger.info(f"New product created: '{title}' by {request.user.username}")
            messages.success(request, '상품이 등록되었습니다.')
            return redirect('products:product_detail', product_id=product.id)
    else:
        form = ProductForm()
    
    return render(request, 'products/product_form.html', {
        'form': form,
        'mode': 'create'
    })

@login_required
def product_update(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 권한 확인
    if product.seller != request.user and not request.user.is_staff:
        messages.error(request, '이 상품을 수정할 권한이 없습니다.')
        return redirect('products:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # XSS 방지
            title = escape(form.cleaned_data.get('title'))
            description = escape(form.cleaned_data.get('description'))
            
            product = form.save(commit=False)
            product.title = title
            product.description = description
            product.save()
            
            logger.info(f"Product updated: '{title}' by {request.user.username}")
            messages.success(request, '상품이 수정되었습니다.')
            return redirect('products:product_detail', product_id=product_id)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/product_form.html', {
        'form': form,
        'product': product,
        'mode': 'update'
    })

@login_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 권한 확인
    if product.seller != request.user and not request.user.is_staff:
        messages.error(request, '이 상품을 삭제할 권한이 없습니다.')
        return redirect('products:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        product_title = product.title
        product.delete()
        
        logger.info(f"Product deleted: '{product_title}' by {request.user.username}")
        messages.success(request, '상품이 삭제되었습니다.')
        return redirect('products:product_list')
    
    return render(request, 'products/product_confirm_delete.html', {'product': product})

@login_required
def my_products(request):
    products = Product.objects.filter(seller=request.user)
    
    # 상태별 필터링
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter != 'all':
        products = products.filter(status=status_filter)
    
    # 페이지네이션
    paginator = Paginator(products, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'products/my_products.html', {
        'page_obj': page_obj,
        'status_filter': status_filter
    })

@login_required
def change_product_status(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        
        # 권한 확인
        if product.seller != request.user and not request.user.is_staff:
            return JsonResponse({'error': '권한이 없습니다.'}, status=403)
        
        new_status = request.POST.get('status')
        if new_status in [s[0] for s in Product.STATUS_CHOICES]:
            product.status = new_status
            product.save()
            
            logger.info(f"Product status changed: '{product.title}' to '{new_status}' by {request.user.username}")
            return JsonResponse({'success': True, 'status': new_status})
        
        return JsonResponse({'error': '잘못된 상태값입니다.'}, status=400)
    
    return JsonResponse({'error': '잘못된 요청입니다.'}, status=405)