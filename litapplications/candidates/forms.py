from django import forms

from .models import Candidate


class UpdateNotesForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ('notes',)
