from django import forms
from Authentication.models import User
from .models import Task, Report, FlightReport, PilotMessage
from django.forms import modelformset_factory
from django_select2.forms import Select2MultipleWidget

class ApproveForm(forms.Form):

    def __init__(self, *args, **kwargs):
        hasTemp = kwargs.pop('hasTemp', None)
        super(ApproveForm, self).__init__(*args, **kwargs)
        self.fields["pushNeeded"] = forms.BooleanField(required=False, label=" Plane needs push before takeoff / after landing ")
        if not hasTemp:
            self.fields["temp"] = forms.CharField(required=True, label=" Couldn't get the temperature, type it in ")

class TaskWorkerForm(forms.ModelForm):
    workers = forms.ModelMultipleChoiceField(queryset = User.objects.none(), widget = Select2MultipleWidget(), required = False)

    class Meta:
        model = Task
        fields = ["workers", "status"]
        widgets = {
            'status': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        airport = kwargs.pop('airport', None)
        super(TaskWorkerForm, self).__init__(*args, **kwargs)
        if airport:
            self.fields['workers'].queryset = User.objects.filter(worksforairport__airport=airport)
        self.fields['status'].initial = 'toDo'

TaskWorkerFormSet = modelformset_factory(Task, form=TaskWorkerForm, extra=0)

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['issue', 'message']
    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['issue'].queryset = Report.ISSUES_CHOICES

class ReportFlightForm(forms.ModelForm):
    class Meta:
        model = FlightReport
        fields = ['issue', 'message']
    def __init__(self, *args, **kwargs):
        super(ReportFlightForm, self).__init__(*args, **kwargs)
        self.fields['issue'].queryset = FlightReport.ISSUES_CHOICES

class GiveResponseForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['response']

class PilotWriteMessage(forms.ModelForm):
    class Meta:
        model = PilotMessage
        fields = ['message']
    def __init__(self, *args, **kwargs):
        super(PilotWriteMessage, self).__init__(*args, **kwargs)
        self.fields['ifAnswer'] = forms.BooleanField(required=False, label="Make message as answer ")