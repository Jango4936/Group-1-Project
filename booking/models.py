from django.db import models

# Create your models here.

class Shop(models.Model):
    name = models.CharField(max_length=100)


class Client(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

class Appointment(models.Model):
    start_time = models.DateTimeField()
    status = models.CharField(max_length=20, default="confirmed")

class TodoItem(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)