# booking/models.py
import datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models.functions import Lower
from django.utils.text import slugify

DAYS_OF_WEEK = [
    ('mon', 'Monday'),
    ('tue', 'Tuesday'),
    ('wed', 'Wednesday'),
    ('thu', 'Thursday'),
    ('fri', 'Friday'),
    ('sat', 'Saturday'),
    ('sun', 'Sunday'),
]

class Shop(models.Model):
    """
    \brief [This class starts the process of making the form that is needed to be filled out by business owners]
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, allow_unicode=True, blank=True)
    
    # keep shop name case insensitive
    class Meta:
        constraints = [
            models.UniqueConstraint(
                Lower("name"),
                name="uniq_shop_name_ci",
            )
        ]


    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name="shop")
    phone = models.CharField(max_length=20,default="NULL")
    opening_hours = models.TimeField(default=datetime.time(0, 0, 0))
    closing_hours = models.TimeField(default=datetime.time(0, 0, 0))
    address = models.CharField(max_length=500,default="NULL")
    description = models.CharField(max_length=1000,default="NULL")
    
    opening_day   = models.CharField(
                       max_length=3,
                       choices=DAYS_OF_WEEK,
                       default='mon',
                   )
    closing_day   = models.CharField(
                       max_length=3,
                       choices=DAYS_OF_WEEK,
                       default='fri',
                   )

    def __str__(self):
        return self.name
    
    def _unique_slug(self, base):
        base = slugify(base, allow_unicode=True)
        slug = base or "shop"
        i = 2
        Model = self.__class__
        while Model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base}-{i}"
            i += 1
        return slug

    def save(self, *args, **kwargs):
        # Only set/refresh slug if it's empty (keeps public links stable)
        if not self.slug:
            self.slug = self._unique_slug(self.name)
        super().save(*args, **kwargs)


class Client(models.Model):
    name  = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.name} ({self.email})"

class Appointment(models.Model):

    STATUS_CHOICES = [
        ("Pending",    "Pending"),
        ("Confirmed",  "Confirmed"),
        ("Cancelled",  "Cancelled"),
        ("Completed",  "Completed"),
    ]


    client     = models.ForeignKey(Client, on_delete=models.CASCADE)
    shop       = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField()
    status     = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="Confirmed",
    )
    duration   = models.DurationField(default=datetime.timedelta(minutes=30))
    note       = models.TextField(max_length=666, default="-")


    def __str__(self):
        return f"{self.client.name} @ {self.start_time}"
