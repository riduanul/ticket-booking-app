from django.db import models
from passengers.models import Passenger
# Create your models here.
class Train(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Schedule(models.Model):
    STATION_CHOICES = [
        ('Chittagong', 'Chittagong'),
        ('Dhaka', 'Dhaka'),
        ('Rajshahi', 'Rajshahi'),
        ('khulna', 'Khulna'),
        ('Coxbazar', 'Coxbazar'),
    ]
    
    TIME_CHOICES = [
        ('08:00 AM', '08:00 AM'),
        ('09:00 AM', '09:00 AM'),
        ('011:00 AM', '11:00 AM'),
        ('01:00 PM', '01:00 PM'),
        ('03:00 PM', '03:00 PM'),
        ('05:00 PM', '05:00 PM'),
        ('08:00 PM', '08:00 PM'),
        ('11:00 PM', '11:00 PM'),
    ]
      

    train = models.ForeignKey(Train, on_delete = models.CASCADE)
    departure_station = models.CharField(max_length=20, choices=STATION_CHOICES)
    arrival_station = models.CharField(max_length=20, choices=STATION_CHOICES)
    departure_time = models.CharField(max_length=20, choices=TIME_CHOICES)
    available_seats = models.IntegerField(default=30)
    date_of_journey = models.DateField()
    ticket_price  = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.train} - {self.departure_station} to {self.arrival_station} on {self.date_of_journey} at {self.departure_time}"
    

class Booking(models.Model):
    train = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    user = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    booked_seat = models.IntegerField()
    def __str__(self):
        return f'{self.user.user.first_name} {self.user.user.last_name} {self.train.train} on {self.train.date_of_journey} at {self.train.departure_time} seat no: {self.booked_seat} '


class Comment(models.Model):
    train = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name='comments', null=True)
    name = models.CharField(max_length=100)
    date = models.DateField(auto_now_add = True)
    comment = models.TextField()
    
    def __str__(self):
        return f'{self.name}'