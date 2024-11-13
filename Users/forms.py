from django import forms
from Database.models import Airline, Airport

class taskAssignmentFilter(forms.Form):
    hideDone = forms.BooleanField(label="Hide done", required=False)

class createAirlineForm(forms.ModelForm):
    class Meta:
        model = Airline
        fields = ['name']

class createAirportForm(forms.ModelForm):
    class Meta:
        model = Airport
        fields = ['name', 'ICAO',  'city', 'county']