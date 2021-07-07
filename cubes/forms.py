from django import forms


class CubeBulkUpdateForm(forms.Form):
    bulk_content = forms.CharField(widget=forms.Textarea)


class CubeInspectionForm(forms.Form):
    cube_id = forms.CharField(max_length=100)
    set_ids = forms.CharField(required=False)
