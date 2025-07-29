from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import ProductReview
from django import forms

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username']

    def __init__(self, *args, **kwargs):
            super(UserForm, self).__init__(*args, **kwargs)
            self.fields['username'].widget.attrs.update({'placeholder': 'John Doe'})
            self.fields['password1'].widget.attrs.update({'placeholder': '●●●●●●●●'})
            self.fields['password2'].widget.attrs.update({'placeholder': '●●●●●●●●'})


class ReviewForm(ModelForm):
    rating = forms.FloatField(
        min_value=0.0,
        max_value=5.0,
        error_messages={
            'min_value': "Rating cannot be lower than 0",
            'max_value': "Rating cannot be higher than 5",
        }
    )

    class Meta:
        model = ProductReview
        fields = ['title', 'rating', 'body']
        widgets = {
            'rating': forms.HiddenInput(),
        }