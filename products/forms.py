# products/forms.py
from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'description', 'price', 'category', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'price': forms.NumberInput(attrs={'min': 1, 'max': 100000000, 'step': 100})
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 2:
            raise forms.ValidationError('제목은 최소 2자 이상이어야 합니다.')
        return title
    
    def clean_description(self):
        description = self.cleaned_data.get('description')
        if len(description) < 10:
            raise forms.ValidationError('상품 설명은 최소 10자 이상이어야 합니다.')
        return description
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # 파일 확장자 확인
            valid_extensions = ['jpg', 'jpeg', 'png', 'gif']
            ext = image.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise forms.ValidationError('JPG, PNG, GIF 형식의 이미지만 업로드 가능합니다.')
            
            # 파일 크기 제한 (5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('이미지 크기는 5MB 이하여야 합니다.')
        return image