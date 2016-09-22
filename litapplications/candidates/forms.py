from crispy_forms.helper import FormHelper
from crispy_forms.layout import BaseInput, Layout

from django import forms
from django.core.urlresolvers import reverse

from .models import Candidate, Note


class StylableSubmit(BaseInput):
    """
    The built-in Submit adds classes that don't look right in our context;
    we actually have to create our own input to get around this.
    """
    input_type = 'submit'

    def __init__(self, *args, **kwargs):
        self.field_classes = ''
        super(StylableSubmit, self).__init__(*args, **kwargs)



class UpdateNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('text',)



class CreateNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('text', 'unit', 'candidate', 'privileged')
        widgets = {
            'privileged': forms.HiddenInput(),
        }



class UpdateLibraryTypeForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ('library_type',)


    def __init__(self, *args, **kwargs):
        super(UpdateLibraryTypeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()

        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_action = reverse('candidates:update_libtype',
            kwargs={'pk': self.instance.id})
        self.helper.layout = Layout(
            'library_type',
            StylableSubmit('submit', 'update library type',
                css_class='btn btn-default')
        )

        self.fields['library_type'].label = ''
