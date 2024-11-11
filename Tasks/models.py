import datetime
from django.db import models
from Authentication.models import User
from Database.models import Airport, Flight

class RegularTasks(models.Model):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name

class Approval(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    departureApprove = models.BooleanField(default=False)   
    arrivalApprove = models.BooleanField(default=False)
    tasksToDoDeparture = models.ManyToManyField(RegularTasks, related_name="depTasks")
    tasksToDoArrival = models.ManyToManyField(RegularTasks, related_name="arrTasks")
    def __str__(self):
        arr = 'YES' if self.arrivalApprove else 'NO'
        dep = 'YES' if self.departureApprove else 'NO'    
        return self.flight.flightNumber + ' arr: ' + arr + ', dep: ' + dep

class Task(models.Model):
    STATUS_CHOICES = [("toDo", "To Do"), ("inProgress", "In Progress"), ("done", "Done")]
    name = models.ForeignKey(RegularTasks, on_delete=models.SET_NULL, null=True, blank=True)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    workers = models.ManyToManyField(User)
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="toDo")
    ifHidden = models.BooleanField(default=False)
    def __str__(self):
        worker_names = ", ".join([worker.username for worker in self.workers.all()])
        return f"{self.name} -> {worker_names}"
    
class Report(models.Model):
    ISSUES_CHOICES = [("Wrong working hours", "Wrong working hours"), ("Request coworkers change", "Request coworkers change"), ("Problem with the task", "Problem with the task"), ("Other", "Other")]
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    issue = models.CharField(max_length=30, choices=ISSUES_CHOICES, default="Other")
    message = models.CharField(max_length=250)
    worker = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)
    responseDate = models.DateTimeField(null=True, blank=True)
    response = models.CharField(max_length=300, null=True, blank=True)
    def __str__(self):
        return f"{self.worker} reports: {self.message}"

class FlightReport(models.Model):
    ISSUES_CHOICES = [("Wrong working hours", "Wrong working hours"), ("Not enough fuel", "Not enough fuel"), ("Problem with the task", "Problem with the task"), ("Aircraft failure", "Aircraft failure"), ("Other", "Other")]
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    issue = models.CharField(max_length=40, choices=ISSUES_CHOICES, default="Other")
    message = models.CharField(max_length=250)
    pilot = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(default=datetime.datetime.now)
    responseDate = models.DateTimeField(null=True, blank=True)
    response = models.CharField(max_length=300, null=True, blank=True)
    def __str__(self):
        return f"{self.pilot} reports: {self.message}"

class PilotMessage(models.Model):
    fromUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_from")
    toUser = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_to")
    message = models.TextField(max_length=255)
    date = models.DateTimeField(default=datetime.datetime.now)
    answerToFlight = models.ForeignKey(Flight, on_delete=models.SET_NULL, related_name="answer_to_flight", blank=True, null=True)

class PilotConversation(models.Model):
    users = models.ManyToManyField(User, related_name="conv_users")
    messages = models.ManyToManyField(PilotMessage, related_name="content")
