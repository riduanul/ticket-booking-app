from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Passenger(models.Model):
    user = models.OneToOneField(User, related_name='user_account', on_delete = models.CASCADE )
    nid = models.CharField(max_length=19, unique=True)
    balance = models.IntegerField(default=0, null=True)

    class Meta:
        verbose_name_plural = 'Passengers'
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'
    


class Transaction(models.Model):
    account = models.ForeignKey(Passenger,related_name='transactions', on_delete= models.CASCADE )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after_transaction = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add = True)
    
    class Meta:
        ordering = ['timestamp']
