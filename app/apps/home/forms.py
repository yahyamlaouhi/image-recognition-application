from django import forms

class ImageForm(forms.Form):
    img = forms.ImageField()

class ImageForm_deep(forms.Form):
    img = forms.ImageField()