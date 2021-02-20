from django import forms


class CubeBulkUpdateForm(forms.Form):
    bulk_content = forms.CharField(widget=forms.Textarea)
