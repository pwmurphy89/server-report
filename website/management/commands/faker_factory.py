from django.core.management.base import BaseCommand
from django_seed import Seed
seeder = Seed.seeder()
import random
import decimal
from datetime import datetime
from django.contrib.auth.models import User
from website.models import Shift_Model, Table_Model
from django.contrib.auth.hashers import make_password

def random_date():
    year = 2018
    month = random.randint(1, 9)
    day = random.randint(1, 28)
    date = datetime(year, month, day)
    return date
def food():
    return random.randint(10, 200)
def drink():
    return random.randint(10, 125)
def guests():
    return random.randint(1, 10)
def tip():
    return float(random.randint(12, 25)/100)

class Command(BaseCommand):
    """Allows command line integration for faker_factory.py"""

    def handle(self, *args, **options):
        """uses faker to generate fake data.  First arg = model, second arg = number of entries to create"""

        # the number argument is the total num of rows you want created

        seeder.add_entity(User, 5, {
            'password': lambda x: make_password("password")
        })
        seeder.add_entity(Shift_Model, 200, {
            'date': lambda x: random_date()
        })
        seeder.add_entity(Table_Model, 500, {
            'food_sales': lambda x: food(),
            'drink_sales': lambda x: drink(),
            'guests_number': lambda x: guests(),
            'tip_percentage': lambda x: tip()
        })


        inserted_pks = seeder.execute()