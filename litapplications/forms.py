from django import forms

class DataIngestForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True}))