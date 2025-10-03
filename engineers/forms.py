from django import forms
from .models import Engineer

class EngineerProfileForm(forms.ModelForm):
    class Meta:
        model = Engineer
        fields = ["education", "certifications", "licenses", "profile_photo", "portfolio", "bio"]

        widgets = {
            "education": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your education"}),
            "certifications": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your certifications"}),
            "licenses": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter your licenses"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Write a short bio"}),
        }
