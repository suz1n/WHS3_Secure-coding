# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('<int:product_id>/', views.product_detail, name='product_detail'),
    path('create/', views.product_create, name='product_create'),
    path('<int:product_id>/update/', views.product_update, name='product_update'),
    path('<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('my-products/', views.my_products, name='my_products'),
    path('<int:product_id>/change-status/', views.change_product_status, name='change_status'),
]

# products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.utils.html import escape
from django.contrib import messages
from .models import Product
from .forms import ProductForm
import logging
import re

# 로깅 설정
logger = logging.getLogger(__name__)

def home(request):
    products = Product.objects.filter(status='available').order_by('-created_at')
    return render(request, 'products/home.html', {'products': products})

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # XSS 방지를 위한 이스케이프 처리
            title = escape(form.cleaned_data.get('title'))
            description = escape(form.cleaned_data.get('description'))
            price = form.cleaned_data.get('price')
            image = form.cleaned_data.get('image')
            
            # 가격 유효성 검사
            if price <= 0 or price > 100000000:  # 1억원 상한선
                messages.error(request, "유효한 가격을 입력해주세요 (1원-1억원).")
                return render(request, 'products/create_product.html', {'form': form})
            
            # 이미지 파일 유효성 검사
            if image:
                # 파일 확장자 확인
                valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
                ext = image.name.split('.')[-1].lower()
                if ext not in valid_extensions:
                    messages.error(request, "JPG, PNG, GIF 형식의 이미지만 업로드 가능합니다.")
                    return render(request, 'products/create_product.html', {'form': form})
                
                # 파일 크기 제한 (5MB)
                if image.size > 5 * 1024 * 1024:
                    messages.error(request, "이미지 크기는 5MB 이하여야 합니다.")
                    return render(request, 'products/create_product.html', {'form': form})
            
            # 상품 저장
            product = form.save(commit=False)
            product.seller = request.user
            product.title = title
            product.description = description
            product.save()
            
            # 로깅
            logger.info(f"New product created: {title} by {request.user.username}")
            
            messages.success(request, "상품이 등록되었습니다.")
            return redirect('products:product_detail', product_id=product.id)
    else:
        form = ProductForm()
    
    return render(request, 'products/create_product.html', {'form': form})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 조회수 증가
    product.views += 1
    product.save()
    
    return render(request, 'products/product_detail.html', {'product': product})

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 권한 확인
    if request.user != product.seller:
        messages.error(request, "상품을 수정할 권한이 없습니다.")
        return redirect('products:product_detail', product_id=product.id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # XSS 방지를 위한 이스케이프 처리
            title = escape(form.cleaned_data.get('title'))
            description = escape(form.cleaned_data.get('description'))
            price = form.cleaned_data.get('price')
            
            # 가격 유효성 검사
            if price <= 0 or price > 100000000:  # 1억원 상한선
                messages.error(request, "유효한 가격을 입력해주세요 (1원-1억원).")
                return render(request, 'products/edit_product.html', {'form': form, 'product': product})
            
            # 상품 업데이트
            product = form.save(commit=False)
            product.title = title
            product.description = description
            product.save()
            
            # 로깅
            logger.info(f"Product updated: {title} by {request.user.username}")
            
            messages.success(request, "상품이 수정되었습니다.")
            return redirect('products:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'products/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # 권한 확인
    if request.user != product.seller and not request.user.is_staff:
        messages.error(request, "상품을 삭제할 권한이 없습니다.")
        return redirect('products:product_detail', product_id=product.id)
    
    if request.method == 'POST':
        # 로깅
        logger.info(f"Product deleted: {product.title} by {request.user.username}")
        
        # 상품 삭제
        product.delete()
        
        messages.success(request, "상품이 삭제되었습니다.")
        return redirect('products:home')
    
    return render(request, 'products/delete_product.html', {'product': product})

def search_products(request):
    query = request.GET.get('q', '')
    
    # XSS 방지를 위한 이스케이프 처리
    query = escape(query)
    
    # 유효성 검사
    if len(query) < 2:
        messages.info(request, "검색어는 최소 2자 이상 입력해주세요.")
        return redirect('products:home')
    
    # 검색 실행
    products = Product.objects.filter(
        Q(title__icontains=query) | 
        Q(description__icontains=query)
    ).filter(status='available').order_by('-created_at')
    
    # 로깅
    logger.info(f"Product search: {query} (results: {products.count()})")
    
    return render(request, 'products/search_results.html', {
        'products': products,
        'query': query
    })

@login_required
def my_products(request):
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'products/my_products.html', {'products': products})