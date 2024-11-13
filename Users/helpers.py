from django.shortcuts import redirect, render
from Database.models import Airline, Airport, CanFlyFrom, CanFlyTo

def create_airline(request, form):      
    form = form
    if request.method == 'POST':
        form = form(request.POST)
        if form.is_valid():
            airline = form.save(commit=False)
            airline.manager = request.user
            airline.save()
            request.session['created_airline_id'] = airline.id
            return redirect('Users:add-routes')
    return render(request, 'Users/airline_manager/create_airline.html', context={'form': form})

def create_airport(request, form):      
    form = form
    if request.method == 'POST':
        form = form(request.POST)
        if form.is_valid():
            airport = form.save(commit=False)
            airport.manager = request.user
            airport.save()
            request.session['created_airport_id'] = airport.id
            return redirect('Users:dashboard')
    return render(request, 'Users/airport_manager/create_airport.html', context={'form': form})

