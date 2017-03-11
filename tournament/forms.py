from django import forms
from django.forms import ModelForm, ValidationError
from .models import Variable, Entry, Coefficient

#Form to update a coefficient
class CoefficientForm(ModelForm):
    class Meta:
        model = Coefficient
        fields = ['value']

#Form to upload a csv file
class UploadForm(forms.Form):
    uploaded_file = forms.FileField(required = True)

    def clean(self):
        if not self.cleaned_data['uploaded_file'] or not self.cleaned_data['uploaded_file'].name.endswith('.csv'):
            raise ValidationError('Either you did not choose a file or the file is not a CSV')
        else:
            return self.cleaned_data
