from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.template import RequestContext
from datetime import datetime
from website.forms import UserForm, ProductForm
from django.contrib.auth.models import User
from website.models import Product, Table_Model, Shift_Model

def index(request):
    template_name = 'index.html'
    return render(request, template_name, {})


# Create your views here.
def register(request):
    '''Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    '''

    # A boolean value for telling the template whether the registration was successful.
    # Set to False initially. Code changes value to True when registration succeeds.
    registered = False

    # Create a new user by invoking the `create_user` helper method
    # on Django's built-in User model
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            # Save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            # Once hashed, we can update the user object.
            user.set_password(user.password)
            user.save()

            # Update our variable to tell the template registration was successful.
            registered = True

        return login_user(request)

    elif request.method == 'GET':
        user_form = UserForm()
        template_name = 'register.html'
        return render(request, template_name, {'user_form': user_form})


def login_user(request):
    '''Handles the creation of a new user for authentication

    Method arguments:
      request -- The full HTTP request object
    '''

    # Obtain the context for the user's request.
    context = RequestContext(request)

    # If the request is a HTTP POST, try to pull out the relevant information.
    if request.method == 'POST':

        # Use the built-in authenticate method to verify
        username=request.POST['username']
        password=request.POST['password']
        authenticated_user = authenticate(username=username, password=password)

        # If authentication was successful, log the user in
        if authenticated_user is not None:
            login(request=request, user=authenticated_user)
            return HttpResponseRedirect('/')

        else:
            # Bad login details were provided. So we can't log the user in.
            print("Invalid login details: {}, {}".format(username, password))
            return HttpResponse("Invalid login details supplied.")


    return render(request, 'login.html', {}, context)

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required

def total_sales(request):
    user = User.objects.get(username=request.user)
    shifts = Shift_Model.objects.filter(server_id=user.id)
    hours = shifts.count() * 5
    tables = Table_Model.objects.select_related('shift').filter(shift_id__server_id=user.id)
    tables_per_shift = tables.count()/shifts.count()
    template_name = 'reports/total.html'
    total_sales = 0
    food_sales = 0
    drink_sales = 0
    customers = 0
    tip_percentage = 0
    total_tips = 0
    for table in tables:
        food_sales += table.food_sales
        drink_sales += table.drink_sales
        customers += table.guests_number
        total_tips += int((table.food_sales + table.drink_sales) * table.tip_percentage)
    total_sales = food_sales + drink_sales
    average_tip_percentage = int((total_tips/total_sales) * 100)

    return render(request, template_name, {
        'tables': tables.count(),
        'shifts':shifts.count(),
        'total_sales': total_sales,
        'food_sales': food_sales,
        'drink_sales': drink_sales,
        'hours': hours,
        'customers': customers,
        'average_tip_percentage': average_tip_percentage,
        'total_tips': total_tips,
        'average_tips_hourly': total_tips/ hours,
        'average_tips_shift': total_tips/ shifts.count(),
        'average_tips_table': total_tips/ tables.count(),
        'average_tips_customer': int(total_tips / customers),

        'average_sales_hourly': total_sales/ hours,
        'average_sales_shift': total_sales/ shifts.count(),
        'average_sales_table': total_sales/ tables.count(),
        'average_sales_customer': int(total_sales / customers),
        'tables_per_shift': int(tables_per_shift)
        })

def month(request):
    month = request.POST.get("month")
    user = User.objects.get(username=request.user)
        # tables = Table_Model.objects.select_related('shift').filter(shift_id__server_id=user.id)

    month_tables = Table_Model.objects.select_related('shift').filter(shift_id__server_id=user.id,shift_id__date__month=month)
    month_shifts = Shift_Model.objects.filter(server_id=user.id, date__month=month)
    for shift in month_shifts:
        print("hello",shift.date)
    for table in month_tables:
        print("months", table.food_sales)
#     shifts = Shift_Model.objects.filter(server_id=user.id)
#     hours = shifts.count() * 5
#     tables = Table_Model.objects.select_related('shift').filter(shift_id__server_id=user.id, date__month = "09")
#     tables_per_shift = tables.count()/shifts.count()
    template_name = 'reports/month.html'
#     total_sales = 0
#     food_sales = 0
#     drink_sales = 0
#     customers = 0
#     tip_percentage = 0
#     total_tips = 0
#     for table in tables:
#         food_sales += table.food_sales
#         drink_sales += table.drink_sales
#         customers += table.guests_number
#         total_tips += int((table.food_sales + table.drink_sales) * table.tip_percentage)
#     total_sales = food_sales + drink_sales
#     average_tip_percentage = int((total_tips/total_sales) * 100)

    return render(request, template_name, {})
#         'tables': tables.count(),
#         'shifts':shifts.count(),
#         'total_sales': total_sales,
#         'food_sales': food_sales,
#         'drink_sales': drink_sales,
#         'hours': hours,
#         'customers': customers,
#         'average_tip_percentage': average_tip_percentage,
#         'total_tips': total_tips,
#         'average_tips_hourly': total_tips/ hours,
#         'average_tips_shift': total_tips/ shifts.count(),
#         'average_tips_table': total_tips/ tables.count(),
#         'average_tips_customer': int(total_tips / customers),

#         'average_sales_hourly': total_sales/ hours,
#         'average_sales_shift': total_sales/ shifts.count(),
#         'average_sales_table': total_sales/ tables.count(),
#         'average_sales_customer': int(total_sales / customers),
#         'tables_per_shift': int(tables_per_shift)
#         })







def user_logout(request):
    # Since we know the user is logged in, we can now just log them out.
    logout(request)

    # Take the user back to the homepage. Is there a way to not hard code
    # in the URL in redirects?????
    return HttpResponseRedirect('/')


def sell_product(request):
    if request.method == 'GET':
        product_form = ProductForm()
        template_name = 'product/create.html'
        return render(request, template_name, {'product_form': product_form})

    elif request.method == 'POST':
        form_data = request.POST

        p = Product(
            seller = request.user,
            title = form_data['title'],
            description = form_data['description'],
            price = form_data['price'],
            quantity = form_data['quantity'],
        )
        p.save()
        template_name = 'product/success.html'
        return render(request, template_name, {})

def list_products(request):
    all_products = Product.objects.all()
    template_name = 'product/list.html'
    return render(request, template_name, {'products': all_products})






