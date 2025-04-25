# reports/forms.py
from django import forms
from .models import Report

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['reason', 'detail']
        widgets = {
            'detail': forms.Textarea(attrs={'rows': 5, 'placeholder': '신고 사유에 대한 상세 내용을 입력해주세요.'}),
        }
    
    def clean_detail(self):
        detail = self.cleaned_data.get('detail')
        if len(detail) < 10:
            raise forms.ValidationError('신고 상세 내용은 최소 10자 이상 작성해주세요.')
        return detail