from django.contrib.auth.models import User
from django.db import models
from datetime import datetime, timedelta
import random

def default_start_time():
    now = datetime.now()
    start = now.replace(hour=17, minute=0, second=0, microsecond=0)
    return start
def default_end_time():
    now = datetime.now()
    end = now.replace(hour=22, minute=0, second=0, microsecond=0)
    return end

# Create your models here.
class Product(models.Model):
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    quantity = models.IntegerField()

class Shift_Model(models.Model):
    server = models.ForeignKey(User, on_delete=models.CASCADE, default='')
    date = models.DateField()
    time_in = models.TimeField(default=default_start_time)
    time_out = models.TimeField(default=default_end_time)

class Table_Model(models.Model):
    shift = models.ForeignKey(Shift_Model, on_delete=models.CASCADE, default='')
    food_sales = models.IntegerField()
    drink_sales = models.IntegerField()
    guests_number = models.IntegerField()
    tip_percentage = models.FloatField()
    @property
    def total(self):
        return sum(self.food_sales, self.drink_sales)




# class Departments_Model(models.Model):
#     """
#         This model holds the data for Bangazon Departments_Model.
#         fields:
#             name - string. name of the department. max length: 20.
#     """

#     name = models.CharField(max_length=20)

#     def __str__(self):
#         return self.name