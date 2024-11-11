import random
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.core.signing import Signer, BadSignature
from Authentication.models import User
from Tasks.models import FlightReport, Approval, RegularTasks, Task, Report
from .models import Airport, Ticket, Flight, Airline
from Tasks.views import createApproval
from .forms import ChangeSeatForm, UpdateFlightForm, AddFlightForm
import json

def pay_page(request):
    flightId = request.session.get('flightId')
    flight = Flight.objects.get(flightNumber=flightId)
    price = flight.price
    context = {"price" : price}
    return render(request, 'Database/ticket/pay-page.html', context=context)

def transaction_unsuccesfull(request, paid):
    username = request.user.username
    add_budget(username, paid)
    return render(request, 'Database/ticket/transaction-unsuccesfull.html')

def transaction_succesfull(request, flight, paid):
    seat = request.session.get('seat')
    leftMoney = int(paid) - flight.price 
    username=request.user.username
    create_ticket(username=username, flight=flight, seat=seat)
    add_budget(username=username, amount=leftMoney)
    context = {"leftMoney" : leftMoney}
    return render(request, 'Database/ticket/transaction-succesfull.html', context=context)

def create_ticket(username, flight, seat):
    ticket = Ticket.objects.create(flight=flight, passenger=User.objects.get(username=username), seat=seat, price=flight.price)

def add_budget(username, amount):
    one_user = User.objects.get(username=username)
    one_user.budget = one_user.budget + int(amount)
    one_user.save()

def process_payment_form(request):
    flightId = request.session.get('flightId')
    flight = Flight.objects.get(flightNumber=flightId)
    price = int(flight.price)
    paid = int(request.POST.get('amount'))
    request.session['paid'] = paid
    if paid >= price:
        return transaction_succesfull(request, flight=flight, paid=paid)
    else:
        return transaction_unsuccesfull(request, paid=paid)
    
def unsign_ticket(signature):
    signer = Signer()
    try:
        ticketId = signer.unsign(signature)   
        ticket = Ticket.objects.get(id=ticketId)
        return ticket
    except (BadSignature, Ticket.DoesNotExist):
        return None

def delete_ticket(request, ticketId):
    ticket = unsign_ticket(ticketId)
    if ticket is None:
        return render(request, "Users/restricted-access.html")
    if ticket.passenger != request.user:
        return redirect('Users:my-tickets') # add notification that you can't delte this ticket
    request.session['ticketId'] = ticket.id
    context = {'ticket': ticket}
    return render(request, 'Database/ticket/delete-ticket.html', context=context)

def deleted_ticket(request):
    ticketId = request.session.get('ticketId')
    try:
        ticket = Ticket.objects.get(id=ticketId)
    except Ticket.DoesNotExist:
        return redirect('Users:my-tickets')# add notification that this ticket has been already deleted
    moneyReturned = int(ticket.price * 0.8)
    add_budget(username=request.user.username, amount=moneyReturned)
    ticket.delete()
    context = {'price':moneyReturned}
    return render(request, 'Database/ticket/deleted-ticket.html', context=context)

def delete_flight_man(request):
    flightId = request.session.get('flight-del')
    flightToDelete = Flight.objects.get(flightNumber=flightId)
    flightToDelete.delete()
    return redirect('Users:flight-management')

def create_flight(request):
    try:
        airline = Airline.objects.get(manager=request.user)
    except Airline.DoesNotExist:
        return render(request, 'Users/resticted-access.html')
    form = AddFlightForm(manager=request.user) 
    if request.method == 'POST':
        form = AddFlightForm(request.POST, manager=request.user)
        if form.is_valid():
            flight = form.save(commit=False)
            flight.airline = airline
            refuel = form.cleaned_data.get('refuel', False)
            flight.save()
            createApproval(flight, refuel)
            return redirect('Users:flight-management')
    context = {'form':form}
    return render(request, 'Database/flight/create-flight.html', context=context)

def one_pas_man(request, username):
    signer = Signer()
    try:
        username_unsigned = signer.unsign(username)   
        passenger = User.objects.get(username=username_unsigned)
    except (BadSignature, Ticket.DoesNotExist):
        return render(request, "Users/restricted-access.html")
    request.session['passenger-username'] = username_unsigned
    tickets = Ticket.objects.filter(passenger=passenger, flight__airline__manager=request.user)
    tickets_signed = []
    for ticket in tickets:
        signed_ticket_id = signer.sign(ticket.id)
        tickets_signed.append({
            'ticket': ticket,
            'signed_ticket_id': signed_ticket_id
        })
    context = {"tickets": tickets_signed, 'passenger': passenger}
    return render(request, 'Database/ticket/one-pas-man.html', context=context)

def man_edit_pas(request, ticketId):
    ticket = unsign_ticket(ticketId)
    if ticket is None:
        return render(request, "Users/restricted-access.html")
    request.session['ticket-to-update'] = ticket.id
    form = ChangeSeatForm(instance=ticket)
    if request.method == 'POST':
        form = ChangeSeatForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            signer = Signer()
            arg_username = signer.sign(ticket.passenger.username)
            return redirect(reverse('Database:one-passenger-man', args=[arg_username]))
    flights = Flight.objects.filter(departureAirport=ticket.flight.departureAirport, arrivalAirport=ticket.flight.arrivalAirport)   #oliwusia
    flight_list = list(flights)
    if ticket.flight in flight_list:
        flight_list.remove(ticket.flight)
    flights_with_difference = []
    previous_price = ticket.price
    signer = Signer()
    for flight in flight_list:
        price_difference = flight.price - previous_price
        signed_flight_number = signer.sign(flight.flightNumber)
        flights_with_difference.append((flight, price_difference, signed_flight_number))
    context = {'ticket': ticket, 'form': form, 'flights':flights_with_difference}
    return render(request, 'Database/ticket/edit-ticket.html', context=context)

def reschedule_man(request, flightNumber):
    newFlight = unsign_flight(flightNumber)
    if newFlight is None:
        return render(request, "Users/restricted-access.html")
    ticketToUpdateId = request.session.get('ticket-to-update')
    ticketToUpdate = Ticket.objects.get(id=ticketToUpdateId)
    priceDifference = ticketToUpdate.price - newFlight.price
    passenger = User.objects.get(username=ticketToUpdate.passenger.username)
    passenger.budget -= priceDifference # Notification 
    passenger.save()
    ticketToUpdate.flight = newFlight
    ticketToUpdate.save()
    return redirect('Users:passengers')

def man_delete_pas(request, ticketId):
    ticket = unsign_ticket(ticketId)
    if ticket is None:
        return render(request, "Users/restricted-access.html")
    ticket.delete()
    return redirect('Users:passengers')

def unsign_flight(signature):
    signer = Signer()
    try:
        flightNumber = signer.unsign(signature)   
        flight = Flight.objects.get(flightNumber=flightNumber)
        return flight
    except (BadSignature, Flight.DoesNotExist):
        return None

def one_flight_man(request, flightId):
    flight = unsign_flight(flightId)
    if flight is None:
        return render(request, "Users/restricted-access.html")
    request.session['flight-del'] = flight.flightNumber
    depAirport = flight.departureAirport
    arrAirport = flight.arrivalAirport
    form = UpdateFlightForm(instance=flight, manager=request.user)
    if request.method  == "POST":
        form = UpdateFlightForm(request.POST, instance=flight, manager=request.user)
        if form.is_valid():
            newFlight = form.save(commit=False)
            approval = Approval.objects.get(flight=flight)
            if newFlight.arrivalAirport != arrAirport:
                approval.arrivalApprove = True
                approval.tasksToDoArrival.set(RegularTasks.objects.none())
                approval.tasksToDoArrival.set([RegularTasks.objects.get(name='load_luggage')])
                approval.save()
                Task.objects.filter(flight=flight, airport=depAirport).delete()
            if newFlight.departureAirport != depAirport:
                approval.departureApprove = True
                approval.tasksToDoDeparture.set(RegularTasks.objects.none())
                approval.tasksToDoDeparture.set([RegularTasks.objects.get(name='load_luggage')])
                approval.save()
                Task.objects.filter(flight=flight, airport=depAirport).delete()
            refuel = form.cleaned_data.get('refuel', False)
            if refuel:
                approval.tasksToDoDeparture.add(RegularTasks.objects.get(name='refuel'))
            newFlight.save()
            # Success message
            return redirect("Users:flight-management")
    context = {'form':form}
    return render(request, 'Database/flight/view-flight-man.html', context=context)

def one_flight_pas(request, flightId):
    flight = unsign_flight(flightId)
    if flight is None:
        return render(request, "Users/restricted-access.html")
    seat = request.session.get('seat')
    tickets = Ticket.objects.filter(flight=flight)
    seatsOccupied = list(tickets.values_list('seat', flat=True))
    if not seat:
        seat = find_random_seat(flight.id, seatsOccupied)
        request.session['seat'] = seat
    request.session['flightId'] = flight.flightNumber
    context = {'flight': flight, 'seat': seat}
    return render(request, 'Database/flight/view-flight-pas.html', context=context)

import string

def find_random_seat(flightId, seatsOccupied):
    flight = Flight.objects.get(id=flightId)
    rows = flight.plane.rows
    seatsInRow = flight.plane.seatsInRow
    alphabet = string.ascii_uppercase[:seatsInRow]
    availableSeats = []
    for x in range(1, rows + 1):
        for y in alphabet:
            curSeat = str(x) + str(y)
            if curSeat not in seatsOccupied:
                availableSeats.append(curSeat)
    return random.choice(availableSeats) 

def choose_seat(request):
    flight = Flight.objects.get(flightNumber=request.session.get('flightId'))
    rows = flight.plane.rows
    seatsInRow = flight.plane.seatsInRow
    seatConfiguration = flight.plane.seatConfiguration
    plane = flight.plane
    tickets = Ticket.objects.filter(flight=flight)
    seatsOccupied = list(tickets.values_list('seat', flat=True))
    margins = len(seatConfiguration) - 1
    initialSeat = request.session.get('seat')
    if not initialSeat:
        initialSeat = find_random_seat(flight.id, seatsOccupied)
    context = {"rows": rows, "seatsInRow": seatsInRow, "seatConfiguration": seatConfiguration, "plane": plane, "seatsOccupied": json.dumps(seatsOccupied), "margins": margins, "initialSeat": initialSeat}
    return render(request, "Database/ticket/choose-seat.html", context=context)

def flight_details(request, flightId):
    signer = Signer()
    try:
        unsigned_flightId = signer.unsign(flightId)
        flight = Flight.objects.get(id=unsigned_flightId)
    except Flight.DoesNotExist:
        return render(request, "Users/restricted-access.html")
    request.session['flightId'] = flight.id
    numOfReports = FlightReport.objects.filter(flight=flight).count()
    context = {"flight": flight, "reportNums": numOfReports}
    return render(request, "Database/flight/flight-details.html", context=context)

def change_flight_status(request, flightId):
    signer = Signer()
    flightId_unsigned = signer.unsign(flightId)
    flight = Flight.objects.get(id=flightId_unsigned)
    if flight.status == "Before":
        flight.status = "During"
    else:
        flight.status = "After"
    flight.save()
    return redirect("Users:my-flights")

def save_seat_to_session(request):
    seat = request.POST.get("seat")
    request.session["seat"] = seat
    signer = Signer()
    flightId = request.session.get("flightId")
    flightId_signed = signer.sign(flightId)
    return redirect(reverse("Database:one-flight-pas", args=[flightId_signed]))