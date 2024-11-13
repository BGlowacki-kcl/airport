import datetime
import logging
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from Authentication.models import User
from Database.models import Flight, Ticket, Airline, Airport, WorksForAirline, CanFlyFrom, CanFlyTo
from Tasks.models import Approval, RegularTasks, Task, Report
from django.db.models import Q
from django.core.signing import Signer
from .forms import taskAssignmentFilter, createAirlineForm, createAirportForm
from .helpers import create_airline, create_airport

def dashboard(request):
    return render(request, "Users/dashboard.html")

# Passenger
def search_flights(request):
    signer = Signer()
    all_flights = Flight.objects.all()
    signed_flights = []
    request.session["seat"] = None
    for flight in all_flights:
        signed_flight_number = signer.sign(flight.flightNumber)
        signed_flights.append({
            'flight': flight,
            'signed_flight_number': signed_flight_number
        })
    context = {'flights': signed_flights}
    return render(request, "Users/passenger/search-flights.html", context=context)

def my_tickets(request):
    signer = Signer()
    all_tickets = Ticket.objects.filter(passenger=request.user).order_by('flight__departureTime')
    signed_tickets = []
    for ticket in all_tickets:
        signed_ticket_id = signer.sign(ticket.id)
        signed_tickets.append({
            'ticket': ticket,
            'signed_ticket_id': signed_ticket_id
        })
    context = {'tickets': signed_tickets}
    return render(request, "Users/passenger/my-tickets.html", context=context)

# Airport worker
def task_manager(request):
    airports = Airport.objects.filter(worksforairport__worker=request.user)
    selected_airport = request.session.get('selected_airport', None)
    tasks = Task.objects.none() # If one, don't let the user choose airport. Just show
    tasks_signed = []

    if request.method == 'POST':
        selected_airport = request.POST.get('choice')   
        request.session['selected_airport'] = selected_airport
        return redirect('Users:task-manager')

    if selected_airport:
        tasks = Task.objects.filter(workers=request.user, airport__name=selected_airport, ifHidden=False)
        signer = Signer()
        tasks_signed = []
        for task in tasks:
            signed_task_id = signer.sign(task.id)
            actionOn = "departure" if task.flight.departureAirport.name==selected_airport else "arrival" 
            coworkers = task.workers.exclude(id=request.user.id)
            all_reports = Report.objects.filter(worker=request.user, task=task).count()
            reports_unresponded = Report.objects.filter(worker=request.user, task=task, response=None).count()
            reports_responded = all_reports - reports_unresponded
            tasks_signed.append({
                "task": task,
                "signed_task_id": signed_task_id,
                "actionOn": actionOn,
                "coworkers": coworkers,
                "reports": all_reports,
                "reports_responded": reports_responded,
            })
    context = {'airports': airports, 'selected_airport': selected_airport, 'tasks': tasks_signed}
    return render(request, "Users/airport_worker/task-manager.html", context=context)

def flight_schedule(request):
    airports = Airport.objects.filter(worksforairport__worker=request.user)
    selected_airport = request.session.get('selected_airport_schedule')
    arrivals = Flight.objects.none()
    departures = Flight.objects.none()
    if request.method == 'POST':
        selected_airport = request.POST.get('choice')
        request.session['selected_airport_schedule'] = selected_airport
        return redirect("Users:flight-schedule")

    if selected_airport:
        arrivals = Flight.objects.filter(arrivalAirport__name=selected_airport).order_by('departureTime')
        departures = Flight.objects.filter(departureAirport__name=selected_airport).order_by('departureTime')
    arrivals_signed = []
    departures_signed = []
    signer = Signer()
    for arrival in arrivals:
        signed_flight_id = signer.sign(arrival.id)
        arrivals_signed.append({
            "flight": arrival,
            "signed_flight_id": signed_flight_id
        })
    for departure in departures:
        signed_flight_id = signer.sign(departure.id)
        departures_signed.append({
            "flight": departure,
            "signed_flight_id": signed_flight_id
        })
    context = {'airports': airports, 'selected_airport': selected_airport, 'arrivals': arrivals_signed, 'departures': departures_signed}
    return render(request, "Users/airport_worker/flight-schedule.html", context=context)

# Airport manager
def flight_approval(request):
    try:
        managedAirport = Airport.objects.get(manager=request.user)
    except (Airport.DoesNotExist):
        return create_airport(request, createAirportForm)
    toApprove = Approval.objects.filter((Q(arrivalApprove=True) & Q(flight__arrivalAirport=managedAirport)) | (Q(departureApprove=True) & Q(flight__departureAirport=managedAirport)))
    signer = Signer()
    toApprove_signed = []
    for approve in toApprove:
        signed_flight_id = signer.sign(approve.flight.id)
        toApprove_signed.append({
            'approve': approve,
            'signed_flight_id': signed_flight_id})
    context = {'toApprove': toApprove_signed, 'managedAirport': managedAirport}
    return render(request, "Users/airport_manager/flight-approval.html", context=context)

def task_assignment(request):
    myFilter = taskAssignmentFilter(request.GET or None)
    try:
        airport = Airport.objects.get(manager=request.user)
    except (Airport.DoesNotExist):
        return create_airport(request, createAirportForm)
    approvals = Approval.objects.filter((Q(flight__arrivalAirport=airport) & Q(arrivalApprove=False)) | (Q(flight__departureAirport=airport) & Q(departureApprove=False)))
    approvals_signed = []
    signer = Signer()
    for approval in approvals:
        signed_approval_id = signer.sign(approval.id)
        approvedOn = "Departure" if approval.flight.departureAirport == airport else "Arrival"
        load_workers = User.objects.filter(task__flight=approval.flight, task__name=RegularTasks.objects.get(name="load_luggage"), task__airport=airport)
        push_workers = User.objects.filter(task__flight=approval.flight, task__name=RegularTasks.objects.get(name="push"), task__airport=airport)
        deice_workers = User.objects.filter(task__flight=approval.flight, task__name=RegularTasks.objects.get(name="deice"), task__airport=airport)
        refuel_workers = User.objects.filter(task__flight=approval.flight, task__name=RegularTasks.objects.get(name="refuel"), task__airport=airport)
        workers = [load_workers, push_workers, deice_workers, refuel_workers]
        if approvedOn == "Departure":
            needsLoad  = True if approval.tasksToDoDeparture.contains(RegularTasks.objects.get(name="load_luggage")) else False
            needsPush  = True if approval.tasksToDoDeparture.contains(RegularTasks.objects.get(name="push")) else False
            needsDeice = True if approval.tasksToDoDeparture.contains(RegularTasks.objects.get(name="deice")) else False
            needsRefuel  = True if approval.tasksToDoDeparture.contains(RegularTasks.objects.get(name="refuel")) else False
        else:
            needsLoad  = True if approval.tasksToDoArrival.contains(RegularTasks.objects.get(name="load_luggage")) else False
            needsPush  = True if approval.tasksToDoArrival.contains(RegularTasks.objects.get(name="push")) else False
            needsDeice = True if approval.tasksToDoArrival.contains(RegularTasks.objects.get(name="deice")) else False
            needsRefuel  = True if approval.tasksToDoArrival.contains(RegularTasks.objects.get(name="refuel")) else False
        needs = [needsLoad, needsPush, needsDeice, needsRefuel]
        ready = True
        for i in range(4):
            if needs[i] == True and not workers[i]:
                ready = False
        loadTask = Task.objects.filter(name=RegularTasks.objects.get(name="load_luggage"), flight=approval.flight)
        pushTask = Task.objects.filter(name=RegularTasks.objects.get(name="load_luggage"), flight=approval.flight)
        deiceTask = Task.objects.filter(name=RegularTasks.objects.get(name="load_luggage"), flight=approval.flight)
        refuelTask = Task.objects.filter(name=RegularTasks.objects.get(name="load_luggage"), flight=approval.flight)
        if loadTask.exists(): 
            colorLoad = loadTask.first().status
        if pushTask.exists(): 
            colorPush = pushTask.first().status
        if deiceTask.exists(): 
            colorDeice = deiceTask.first().status
        if refuelTask.exists(): 
            colorRefuel = refuelTask.first().status
        
        approvals_signed.append({
            "approval": approval,
            "signed_approval_id": signed_approval_id,
            "approvedOn": approvedOn,
            "workers": {
                "load_luggage": load_workers,
                "push": push_workers,
                "deice": deice_workers,
                "refuel": refuel_workers
            },
            "ready": ready,
            "needs": {
                "needsLoad": needsLoad,
                "needsPush": needsPush,
                "needsRefuel": needsRefuel,
                "needsDeice": needsDeice
            },
            "color": {
                "load": getColor(colorLoad),
                "push": getColor(colorPush),
                "deice": getColor(colorDeice),
                "refuel": getColor(colorRefuel)
            }
        }) 
    if myFilter.is_valid():
        if myFilter.cleaned_data["hideDone"]:
            approvals_signed = [approval for approval in approvals_signed if not approval["ready"]]
    context = {"approvals": approvals_signed, "form": myFilter, "color": "blue"}
    return render(request, "Users/airport_manager/task-assignment.html", context=context)

def getColor(status):
    if status == "toDo":
        return "red"
    elif status == "inProgress":
        return "yellow"
    else:
        return "green"

def workers(request):
    try:
        airport = Airport.objects.get(manager=request.user)
    except Airport.DoesNotExist:
        return create_airport(request, createAirportForm)
    workers = User.objects.filter(worksforairport__airport=airport)
    workers_signed = []
    signer = Signer()
    for worker in workers:
        signed_user_id = signer.sign(worker.id)
        reports = Report.objects.filter(worker=worker, response=None).count()
        toDo = Task.objects.filter(workers=worker, status="toDo").count()
        inProgress = Task.objects.filter(workers=worker, status="inProgress").count()
        workers_signed.append({
            "signed_user_id": signed_user_id,
            "worker": worker,
            "reports": reports,
            "toDo": toDo,
            "inProgress": inProgress
        })
    context = {"workers": workers_signed}
    return render(request, "Users/airport_manager/workers.html", context=context)

# Airline manager
def flight_management(request):
    try:
        airline = Airline.objects.get(manager=request.user)
    except Airline.DoesNotExist:
        return create_airline(request, createAirlineForm)
    all_flights = Flight.objects.filter(airline=airline)
    signer = Signer()
    signed_flights = []
    for flight in all_flights:
        signed_flight_number = signer.sign(flight.flightNumber)
        signed_flights.append({
            'flight': flight,
            'signed_flight_number': signed_flight_number
        })
    context = {'flights': signed_flights}
    return render(request, "Users/airline_manager/flights-management.html", context=context)

def passengers(request):
    try:
        airline = Airline.objects.get(manager=request.user)
    except Airline.DoesNotExist:
        return create_airline(request, createAirlineForm)
    all_flights = Flight.objects.filter(airline=airline)
    all_tickets = Ticket.objects.filter(flight__in=all_flights)
    passengers = {}
    for ticket in all_tickets:   
        if ticket.passenger in passengers:
            passengers[ticket.passenger] += 1 
        else:
            passengers[ticket.passenger] = 1
    signer = Signer()
    signed_passengers = {
        passenger: {
            'count': count,
            'signed_username': signer.sign(passenger.username)
        }
        for passenger, count in passengers.items()
    }
    context = {'passengers': signed_passengers}
    return render(request, "Users/airline_manager/passengers.html", context=context)

def add_routes(request):
    airline = get_object_or_404(Airline, manager=request.user)

    all_airports = set(Airport.objects.all())
    to_airports = set(CanFlyTo.objects.filter(airline=airline).values_list('airport', flat=True))
    from_airports = set(CanFlyFrom.objects.filter(airline=airline).values_list('airport', flat=True))
    
    available_to_airports = all_airports - to_airports
    available_from_airports = all_airports - from_airports

    context = {
        'airline': airline,
        'to_airports': to_airports,
        'from_airports': from_airports,
        'available_to_airports': available_to_airports,
        'available_from_airports': available_from_airports,
    }
    return render(request, 'Users/airline_manager/add_routes.html', context)

# Pilot
def my_flights(request):
    pilot = request.user
    airlines = Airline.objects.filter(worksforairline__worker = pilot)
    flights = {}
    signer = Signer()
    for airline in airlines:
        flightsInAirline = Flight.objects.filter(airline=airline).order_by('-departureTime')
        flights[airline] = []
        for flight in flightsInAirline:
            if flight.status != 'After':
                signed_flight_id = signer.sign(flight.id)
                timeToFlight = timezone.now() - flight.departureTime
                if timeToFlight.total_seconds() > 0:
                    ifShouldDeparture = False
                else:
                    ifShouldDeparture = True
                if timeToFlight.days > 0:
                    timeText = f"{timeToFlight.days} days"
                elif timeToFlight.seconds >= 3600:
                    hours = timeToFlight.seconds // 3600
                    timeText = f"{hours} hours"
                else:
                    minutes = timeToFlight.seconds // 60
                    timeText = f"{minutes} minutes"
                flights[airline].append({
                    "flight": flight,
                    "signed_flight_id": signed_flight_id,
                    "time_to_flight": timeToFlight,
                    "time_text": timeText,
                    "if_should_departure": ifShouldDeparture,
                })
    context = {"flights": flights}
    return render(request, "Users/pilot/my-flights.html", context=context)

def flight_schedule_pilot(request):
    airlines = Airline.objects.filter(worksforairline__worker=request.user)
    selected_airline = request.session.get('selected_airline_schedule')
    flights = Flight.objects.none()
    if request.method == 'POST':
        selected_airline = request.POST.get('choice')
        request.session['selected_airline_schedule'] = selected_airline
    if selected_airline:
        flights = Flight.objects.filter(airline__name=selected_airline).order_by('departureTime')
    flights_signed = []
    signer = Signer()
    for flight in flights:
        signed_flight_id = signer.sign(flight.id)
        flights_signed.append({
            "flight": flight,
            "signed_flight_id": signed_flight_id
        })
    context = {'airlines': airlines, 'selected_airline': selected_airline, 'flights': flights_signed}
    return render(request, "Users/pilot/flight-schedule.html", context=context)

def profile(request):
    return render(request, "Users/profile.html")
