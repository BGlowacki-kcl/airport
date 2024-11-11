from django.db import models
from Authentication.models import User

class Airport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    ICAO = models.CharField(max_length=3, unique=True)
    city = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    manager = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    def __str__(self):
        return self.name

class Airline(models.Model):
    name = models.CharField(max_length=100, unique=True)
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    def __str__(self):
        return self.name

class WorksForAirline(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.worker.username + " works for " + self.airline.name

class WorksForAirport(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.worker.username + " works for " + self.airport.name

class Plane(models.Model):
    company = models.CharField(max_length=20)
    model = models.CharField(max_length=10)
    rows = models.IntegerField()
    seatsInRow = models.IntegerField()
    seatConfiguration = models.CharField(max_length=5, blank=True, null=True)
    def __str__(self):
        return self.company + " " + self.model

class Fleet(models.Model):
    name = models.CharField(max_length=50, unique=True)
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    plane = models.ForeignKey(Plane, on_delete=models.CASCADE)
    production_year = models.IntegerField(null=True)
    def __str__(self):
        return self.plane.company + " " + self.plane.model + ": " + self.name + " -> " + self.airline.name

class CanFlyTo(models.Model): 
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='possible_destinations') 
    def __str__(self):
        return self.airline.name + " can fly to " + self.airport.ICAO

class CanFlyFrom(models.Model):
    airline = models.ForeignKey(Airline, on_delete=models.CASCADE)
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='possible_departure')  
    def __str__(self):
        return self.airline.name + " can fly from " + self.airport.ICAO

class Flight(models.Model):
    FLIGHT_STATUS = [("Before", "Before"), ("During", "During"), ("After", "After")]
    flightNumber = models.CharField(max_length=10)
    departureAirport = models.ForeignKey(Airport, on_delete=models.SET_NULL, null=True, related_name='departure')  
    arrivalAirport = models.ForeignKey(Airport, on_delete=models.SET_NULL, null=True, related_name='arrival')  
    departureTime = models.DateTimeField(null=True, blank=True)
    arrivalTime = models.DateTimeField(null=True, blank=True)
    pilot = models.ForeignKey(User, on_delete=models.SET_NULL, null=True) 
    plane = models.ForeignKey(Plane, on_delete=models.SET_NULL, null=True)
    airline = models.ForeignKey(Airline, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=10, choices=FLIGHT_STATUS, default="Before")
    price = models.IntegerField(null=True)
    def __str__(self):
        return self.flightNumber

class Ticket(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.SET_NULL, null=True, related_name='flight_ticket')  
    passenger = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='passenger_ticket') 
    seat = models.CharField(max_length=5)
    price = models.IntegerField(null=True, blank=True)
    def __str__(self):
        return self.flight.flightNumber + " for " + self.passenger.username