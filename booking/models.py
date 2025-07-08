# booking/models.py

from django.db import models

class Shop(models.Model):
    name = models.CharField(max_length=100)
    # …any other fields like address, opening_hours…

    def __str__(self):
        return self.name

class Client(models.Model):
    name  = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} ({self.email})"

class Appointment(models.Model):
    client     = models.ForeignKey(Client, on_delete=models.CASCADE)
    shop       = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    status     = models.CharField(max_length=20, default="confirmed")

    def __str__(self):
        return f"{self.client.name} @ {self.start_time}"
