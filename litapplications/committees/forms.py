from django import forms

from .models import Committee


class UpdateNotesForm(forms.ModelForm):
    class Meta:
        model = Committee
        fields = ('notes',)



class UpdateNumbersForm(forms.ModelForm):
    class Meta:
        model = Committee
        fields = ('min_appointees', 'max_appointees')
