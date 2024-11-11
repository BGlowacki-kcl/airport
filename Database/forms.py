from .models import Flight, Airline, Plane, Airport, Ticket
from django import forms
from Authentication.models import User, Role

class ChangeSeatForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['seat']

class BaseFlightForm(forms.ModelForm):
    refuel = forms.BooleanField(label="The plane needs re-fuelling", required=False)

    class Meta:
        model = Flight
        fields = ['flightNumber', 'departureTime', 'departureAirport', 'arrivalTime', 'arrivalAirport', 'pilot', 'plane', 'price']
    
    def __init__(self, *args, **kwargs):
        manager = kwargs.pop('manager', None)
        super().__init__(*args, **kwargs)
        
        if manager:
            # Get the airline managed by the logged-in user
            try:
                managed_airline = Airline.objects.get(manager=manager)
            except Airline.DoesNotExist:
                managed_airline = None

            if managed_airline:
                # Filter users to only show pilots working for the manager's airline
                pilot_role = Role.objects.get(name='pilot')
                self.fields['pilot'].queryset = User.objects.filter(
                    worksforairline__airline=managed_airline,
                    role=pilot_role
                )
                self.fields['arrivalAirport'].queryset = Airport.objects.filter(possible_destinations__airline=managed_airline)
                self.fields['departureAirport'].queryset = Airport.objects.filter(possible_departure__airline=managed_airline)
                self.fields['plane'].queryset = Plane.objects.filter(fleet__airline=managed_airline)
            else:
                self.fields['pilot'].queryset = User.objects.none()
                self.fields['departureAirport'].queryset = User.objects.none()
                self.fields['arrivalAirport'].queryset = User.objects.none()
                self.fields['plane'].queryset = User.objects.none()

class AddFlightForm(BaseFlightForm):
    pass

class UpdateFlightForm(BaseFlightForm):
    pass
