from django import forms

from .models.committees import Committee


class UpdateNotesForm(forms.ModelForm):
    class Meta:
        model = Committee
        fields = ('notes',)



class UpdateNumbersForm(forms.ModelForm):
    class Meta:
        model = Committee
        fields = ('min_appointees', 'max_appointees')


class CommitteeCreateForm(forms.ModelForm):
    class Meta:
        model = Committee
        fields = ('short_code', 'long_name', 'charge', 'unit')

    def __init__(self, *args, **kwargs):
        super(CommitteeCreateForm, self).__init__(*args, **kwargs)
        self.fields['long_name'].help_text = 'Full name of committee'
        self.fields['charge'].help_text = 'Link to committee charge (optional)'
        self.fields['unit'].help_text = \
            'To which ALA unit does this committee belong?'
