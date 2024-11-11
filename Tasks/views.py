import datetime
from django.shortcuts import redirect, render
from django.urls import reverse
from .models import Approval, RegularTasks, Report, Task, FlightReport, PilotConversation, PilotMessage
from Database.models import Airport, Flight
from django.core.signing import Signer, BadSignature
from django.http import HttpResponse
import requests
from .forms import ApproveForm, TaskWorkerFormSet, ReportForm, TaskWorkerForm, GiveResponseForm, ReportFlightForm, PilotWriteMessage
from Authentication.models import User

def flight_to_approve(request, flightId):
    signer = Signer()
    try:
        flightId_unsigned = signer.unsign(flightId)   
        flight = Flight.objects.get(id=flightId_unsigned)
        approval = Approval.objects.get(flight=flight)
    except (BadSignature, Flight.DoesNotExist, Approval.DoesNotExist):
        return render(request, "Users/restricted-access.html")
    airport = Airport.objects.get(manager=request.user)
    ifDeparture = True if flight.departureAirport == airport else False
    couldGetTemperature = True
    temperature = 0
    if ifDeparture:
        temperature = temp(airport.city)
        if temperature is None:
            couldGetTemperature = False 
        else:
            if temperature <= 5:
                approval.tasksToDoDeparture.add(RegularTasks.objects.get(name="deice"))  # Deice
    form = ApproveForm(hasTemp=couldGetTemperature)
    if request.method == "POST":
        form = ApproveForm(request.POST, hasTemp=couldGetTemperature)
        if form.is_valid():
            ifPush = form.cleaned_data["pushNeeded"]
            if ifPush and ifDeparture:
                approval.tasksToDoDeparture.add(RegularTasks.objects.get(name="push"))
            elif ifPush and not ifDeparture:
                approval.tasksToDoArrival.add(RegularTasks.objects.get(name="push"))
            if ifDeparture:
                approval.departureApprove = False # Not needed anymore
            else:
                approval.arrivalApprove = False
            if not couldGetTemperature and ifDeparture:
                tempReceived = form.cleaned_data["temp"]
                if tempReceived <= 5:
                    approval.tasksToDoDeparture.add(RegularTasks.objects.get(name="deice"))
            approval.save()
            if ifDeparture:
                for task in approval.tasksToDoDeparture.all():
                    Task.objects.create(name=task, flight=approval.flight, airport=airport, status="toDo", ifHidden=False)
            else:
                for task in approval.tasksToDoArrival.all():
                    Task.objects.create(name=task, flight=approval.flight, airport=airport, status="toDo", ifHidden=False)
            return redirect("Users:flight-approval")
    context = {"approve": approval, "form":form, "hasTemp": couldGetTemperature, "temp": temperature, "ifDeparture": ifDeparture}
    return render(request, 'Tasks/flight-to-approve.html', context=context)

# Remember to delete approval if both fields are False and all tasks are assigned
# Check what happens if airport city is wrong and cannot get temperature. If you can put the temperature on your own machine
# What if I set a cold city. Does it add deice 

def temp(city):
    url = f"http://api.openweathermap.org/data/2.5/weather"
    api_key = "a611201ea22e22bc8d470ddeab473750"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'main' in data:
        return data['main']['temp']
    else:
        return None

def createApproval(flight, refuel):
    load_task = RegularTasks.objects.get(name='load_luggage')
    refuel_task = RegularTasks.objects.get(name='refuel')
    approval = Approval(flight=flight, arrivalApprove=True, departureApprove=True)
    approval.save()
    approval.tasksToDoArrival.set([load_task])
    approval.tasksToDoDeparture.set([load_task])
    if refuel:
        approval.tasksToDoDeparture.add(refuel_task)

def flight_to_assign(request, approvalId):
    signer = Signer()
    try:
        approvalId_unsigned = signer.unsign(approvalId)
        approval = Approval.objects.get(id=approvalId_unsigned)
    except (Approval.DoesNotExist):
        return render(request, "Users/restricted-access.html")
    airport = Airport.objects.get(manager=request.user)
    if approval.flight.arrivalAirport == airport:
        tasks = Task.objects.filter(flight=approval.flight, name__in=approval.tasksToDoArrival.all(), airport=airport)
    else:
        tasks = Task.objects.filter(flight=approval.flight, name__in=approval.tasksToDoDeparture.all(), airport=airport)
    if request.method == 'POST':
        formset = TaskWorkerFormSet(request.POST, queryset=tasks, form_kwargs={'airport': airport})
        if formset.is_valid():
            formset.save()
            return redirect('Users:task-assignment') 
    else:
        formset = TaskWorkerFormSet(queryset=tasks, form_kwargs={'airport': airport})
    context = {"approval": approval, "formset": formset}
    return render(request, 'Tasks/flight-to-assign.html', context=context)

def unsign_task(taskId_signed):
    signer = Signer()
    try:
        taskId_unsigned = signer.unsign(taskId_signed)
        task = Task.objects.get(id=taskId_unsigned)
        return task
    except (Task.DoesNotExist, BadSignature):
        return None

def task_done(request, taskId):
    task = unsign_task(taskId)
    if task is None:
        return render(request, "Users/restricted-access.html")
    if task.status == "toDo":
        task.status = "inProgress"
    elif task.status == "inProgress":
        task.status = "done"
    else:
        task.ifHidden = True
    task.save()
    return redirect('Users:task-manager')

def task_report(request, taskId):
    task = unsign_task(taskId)
    if task is None:
        return render(request, "Users/restricted-access.html")
    worker = request.user
    reports = Report.objects.filter(worker=worker, task=task)
    form = ReportForm()
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.worker = worker
            report.task = task
            report.date = datetime.datetime.now()
            report.save()
            return redirect("Users:task-manager")
    context = {"form": form, "task": task, "reports": reports}
    return render(request, "Tasks/report-task.html", context=context)

def view_worker(request, workerId):
    signer = Signer()
    try:
        workerId_unsigned = signer.unsign(workerId)
        worker = User.objects.get(id=workerId_unsigned)
    except (BadSignature, User.DoesNotExist):
        return render(request, "Users/restricted-access.html")
    airport = Airport.objects.get(manager=request.user)
    tasksToDo = Task.objects.filter(workers=worker, status="toDo")
    tasksInProgress = Task.objects.filter(workers=worker, status="inProgress")
    reports = Report.objects.filter(worker=worker, response=None)
    reports_signed = []
    for report in reports:
        signed_report_id = signer.sign(report.id)
        reports_signed.append({
            "signed_report_id": signed_report_id,
            "report": report,
        })
    tasksInProgress_signed = []
    for task in tasksInProgress:
        signed_task_id = signer.sign(task.id)
        approvedOn = "Departure" if task.flight.departureAirport == airport else "Arrival"
        coworkers = task.workers.exclude(pk=worker.pk)
        tasksInProgress_signed.append({
            "task": task,
            "signed_task_id": signed_task_id,
            "approvedOn": approvedOn,
            "coworkers": coworkers
        })
    tasksToDo_signed = []
    for task in tasksToDo:
        signed_task_id = signer.sign(task.id)
        approvedOn = "Departure" if task.flight.departureAirport == airport else "Arrival"
        coworkers = task.workers.exclude(pk=worker.pk)
        tasksToDo_signed.append({
            "task": task,
            "signed_task_id": signed_task_id,
            "approvedOn": approvedOn,
            "coworkers": coworkers
        })
    context = {"reports": reports_signed, "tasksInProgress": tasksInProgress_signed, "tasksToDo": tasksToDo_signed, "myWorker": worker}
    return render(request, "Tasks/view-worker.html", context=context)

def change_one_assignment_normal(request, taskId):
    task = unsign_task(taskId)
    if task is None:
        return render(request, 'Users:restricted-access.html')
    form = TaskWorkerForm(instance=task, airport = task.airport)
    if request.method == 'POST':
        form = TaskWorkerForm(request.POST, instance=task, airport=task.airport)
        if form.is_valid():
            form.save()
            return redirect("Users:workers")
    context = {"form": form}
    return render(request, "Tasks/change-one-flight.html", context=context)

def change_one_assignment(request, reportId):
    signer = Signer()
    try:
        reportId_unsigned = signer.unsign(reportId)
        report = Report.objects.get(id=reportId_unsigned)
    except (BadSignature, Report.DoesNotExist):
        return render(request, "Users/restricted-access.html")
    task = report.task
    airport = task.airport
    initial_workers = set(task.workers.all())
    form = TaskWorkerForm(instance=task, airport=airport)
    if request.method == 'POST':
        form = TaskWorkerForm(request.POST, instance=task, airport=airport)
        if form.is_valid():
            end_task = form.save()
            end_workers = set(end_task.workers.all())
            worker = report.worker
            removed_workers = initial_workers - end_workers
            added_workers = end_workers - initial_workers
            added = ""
            removed = ""
            if worker in removed_workers: # The person who created report was deleted
                report.delete()
            else:
                if removed_workers:
                    removed_workers_list = [str(worker) for worker in removed_workers]
                    removed = f"Coworkers deleted: {', '.join(removed_workers_list)}"
                if added_workers:
                    added_workers_list = [str(worker) for worker in added_workers]
                    added = f"Coworkers added: {', '.join(added_workers_list)}"
                if added=="" and removed=="":
                    report.response = "No changes made!"
                else:
                    between = " | " if not added=="" and not removed=="" else " "
                    report.response = added + between + removed
                report.responseDate = datetime.datetime.now()
                report.save()
            return redirect("Users:workers")
    context = {"form": form}
    return render(request, "Tasks/change-one-flight.html", context=context)

def send_response(request, reportId):
    signer = Signer()
    try:
        reportId_unsigned = signer.unsign(reportId)
        report = Report.objects.get(id=reportId_unsigned)
    except (BadSignature, Report.DoesNotExist):
        return render(request, "Users/restricted-access.html")
    form = GiveResponseForm(instance=report)
    if request.method == "POST":
        form = GiveResponseForm(request.POST ,instance=report)
        if form.is_valid():
            end_report = form.save(commit=False)
            end_report.responseDate = datetime.datetime.now()
            end_report.save()
            return redirect("Users:workers")
    context = {"form": form, "report": report}
    return render(request, "Tasks/send-response.html", context=context)

def report_flight_with_id(request, flightId):
    signer = Signer()
    flightId_unsigned = signer.unsign(flightId)
    request.session['flightId'] = flightId_unsigned
    return report_flight(request)  

def report_flight(request):
    flightId = request.session.get('flightId')
    flight = Flight.objects.get(id=flightId)
    form = ReportFlightForm()
    reports = FlightReport.objects.filter(flight=flight)
    request.session['ifReport'] = True
    if request.method == 'POST':
        form = ReportFlightForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.flight = flight
            report.pilot = flight.pilot
            report.date = datetime.datetime.now()
            report.save()
            return redirect("Users:flight-schedule-pilot")
    context = {"form": form, "flight": flight, "reports": reports}
    return render(request, "Tasks/report-flight.html", context=context)

def contact_pilot(request, flightId):
    request.session['ifReport'] = False
    signer = Signer()
    try:
        flightId_unsigned = signer.unsign(flightId)
        flight = Flight.objects.get(id=flightId_unsigned)
    except Flight.DoesNotExist:
        return render(request, "Users/restricted-access.html")
    conversation = PilotConversation.objects.filter(users=request.user).filter(users=flight.pilot).first()
    messages = PilotMessage.objects.none()
    if conversation:
        messages = conversation.messages.all().order_by('-date') 
    form = PilotWriteMessage()
    if request.method == "POST":
        form = PilotWriteMessage(request.POST)
        if form.is_valid():
            ifAnswer = form.cleaned_data['ifAnswer']
            message = form.save(commit=False)
            message.fromUser = request.user
            message.toUser = flight.pilot
            message.date = datetime.datetime.now()
            if ifAnswer:
                message.answerToFlight = flight
            conversation = PilotConversation.objects.filter(users=request.user).filter(users=flight.pilot).first()
            if not conversation:
                conversation = PilotConversation.objects.create()
                conversation.users.add(request.user, flight.pilot)
            message.save()
            conversation.messages.add(message)
            conversation.save()
            url = reverse('Tasks:contact-pilot', kwargs={'flightId': signer.sign(flight.id)})
            return redirect(url)
    context = {"form": form, "flight": flight, "messages": messages}
    return render(request, 'Tasks/message-pilot.html', context=context)

    
