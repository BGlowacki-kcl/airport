from django import forms

class taskAssignmentFilter(forms.Form):
    hideDone = forms.BooleanField(label="Hide done", required=False)