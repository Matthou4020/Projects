from django import forms
from . import util

class SearchForm(forms.Form):
    q = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Search Encyclopedia'
            })
        , label=''
    )

class TitleForm(forms.Form):
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Title of your page'
        }), label=''
    )
    is_edit = forms.BooleanField(
        widget=forms.HiddenInput(), 
        required=False)
    
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        is_edit = cleaned_data.get('is_edit')
        if not is_edit and title in util.list_entries():
            raise forms.ValidationError("This title already exists.")

        elif is_edit:
            if title in util.list_entries():
                return cleaned_data


class NewPageForm(forms.Form):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'id': 'page_text',
            'placeholder': 'Text',
            'rows': 4,
            'cols': 50
        }), label=''
    )

