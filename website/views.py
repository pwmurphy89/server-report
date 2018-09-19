from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.template import RequestContext
from datetime import datetime, timedelta
from website.forms import UserForm, ProductForm
from django.contrib.auth.models import User
from website.models import Product, Table_Model, Shift_Model
from chartit import DataPool, Chart
import json

def index(request):
    date = datetime.now().strftime('%Y-%m-%d')
    template_name = 'index.html'
    return render(request, template_name, {'date':date})


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
        'user': user,
        'tables': tables.count(),
        'shifts':shifts.count(),
        'total_sales': total_sales,
        'food_sales': food_sales,
        'drink_sales': drink_sales,
        'hours': hours,
        'customers': customers,
        'average_tip_percentage': average_tip_percentage,
        'total_tips': total_tips,
        'average_tips_hourly': int(total_tips/ hours),
        'average_tips_shift': int(total_tips/ shifts.count()),
        'average_tips_table': int(total_tips/ tables.count()),
        'average_tips_customer': int(total_tips / customers),

        'average_sales_hourly': int(total_sales/ hours),
        'average_sales_shift': int(total_sales/ shifts.count()),
        'average_sales_table': int(total_sales/ tables.count()),
        'average_sales_customer': int(total_sales / customers),
        'tables_per_shift': int(tables_per_shift)
        })

def month_sales(request):
    template_name = 'reports/month.html'
    month = request.POST.get("month")
    user = User.objects.get(username=request.user)
    month_tables = Table_Model.objects.select_related('shift').filter(shift_id__server_id=user.id,shift_id__date__month=month)
    month_shifts = Shift_Model.objects.filter(server_id=user.id, date__month=month)
    print('type',type(month_shifts))
    if month_shifts.count() == 0:
        return render(request, template_name, {
            'message': 'no tables'
        })
    else:
        hours = int(month_shifts.count() * 5)
        tables_per_shift = int(month_tables.count()/month_shifts.count())
        month_sales = 0
        food_sales = 0
        drink_sales = 0
        customers = 0
        tip_percentage = 0
        total_tips = 0
        for table in month_tables:
            food_sales += table.food_sales
            drink_sales += table.drink_sales
            customers += table.guests_number
            total_tips += int((table.food_sales + table.drink_sales) * table.tip_percentage)
        month_sales = food_sales + drink_sales
        average_tip_percentage = int((total_tips/month_sales) * 100)

        return render(request, template_name, {
            'month': month,
            'tables': month_tables.count(),
            'shifts':month_shifts.count(),
            'month_sales': month_sales,
            'food_sales': food_sales,
            'drink_sales': drink_sales,
            'hours': hours,
            'customers': customers,
            'average_tip_percentage': average_tip_percentage,
            'total_tips': total_tips,
            'average_tips_hourly': int(total_tips/ hours),
            'average_tips_shift': int(total_tips/ month_shifts.count()),
            'average_tips_table': int(total_tips/ month_tables.count()),
            'average_tips_customer': int(total_tips / customers),

            'average_sales_hourly': int(month_sales/ hours),
            'average_sales_shift': int(month_sales/ month_shifts.count()),
            'average_sales_table': int(month_sales/ month_tables.count()),
            'average_sales_customer': int(month_sales / customers),
            'tables_per_shift': tables_per_shift
        })

def all_months(request):
    template_name = "reports/month_graph.html"
    all_months = {}
    months = [1,2,3,4,5,6,7,8,9,10,11,12]
    user = User.objects.get(username=request.user)
    for month in months:
        month_tables = Table_Model.objects.select_related('shift').filter(shift_id__server_id=user.id,shift_id__date__month=month)
        month_shifts = Shift_Model.objects.filter(server_id=user.id, date__month=month)
        total_sales = 0
        food_sales = 0
        drink_sales = 0
        total_tips = 0
        if month_shifts.count() == 0:
            all_months[month] = {"month": month, "total_sales": 0, "total_tips": 0}
            continue
        for table in month_tables:
            food_sales += table.food_sales
            drink_sales += table.drink_sales
            total_tips += int((table.food_sales + table.drink_sales) * table.tip_percentage)
        total_sales = food_sales + drink_sales
        all_months[month] = {"month": month, "total_sales": total_sales, "total_tips": total_tips}
    all_months_json = json.dumps(all_months)
    return render(request, template_name, { "all_months": all_months_json})


from chartit import DataPool, Chart

def month_chart_view(request, all_months):
    #Step 1: Create a DataPool with the data we want to retrieve.
    monthdata = \
        DataPool(
           series=
            [{'options': {
               'source': all_months},
              'terms': [
                'month',
                'total_sales',
                'total_tips']}
             ])

    #Step 2: Create the Chart object
    cht = Chart(
            datasource = monthdata,
            series_options =
              [{'options':{
                  'type': 'line',
                  'stacking': False},
                'terms':{
                  'month': [
                    'total_sales',
                    'total_tips']
                  }}],
            chart_options =
              {'title': {
                   'text': 'Weather Data of Boston and Houston'},
               'xAxis': {
                    'title': {
                       'text': 'Month number'}}})

    #Step 3: Send the chart object to the template.
    return render_to_response({'monthchart': cht})





def week_sales(request):
    user = User.objects.get(username=request.user)
    all_shifts = Shift_Model.objects.filter(server_id=user.id)
    template_name = 'reports/week.html'
    week = request.POST['week']
    sliced_week = int(week[6:])
    week_tables = []
    hours = 0
    week_shifts_count = 0
    week_tables_count = 0
    week_tips = 0
    week_sales = 0
    food_sales = 0
    drink_sales = 0
    customers = 0
    for shift in all_shifts:
        if shift.date.isocalendar()[1] == sliced_week:
            hours += 5
            week_shifts_count += 1
            tables_this_shift = Table_Model.objects.filter(shift_id=shift.id)
            for table in tables_this_shift:
                week_tables_count += 1
                week_tables.append(table)
    for table in week_tables:
        food_sales += table.food_sales
        drink_sales += table.drink_sales
        customers += table.guests_number
        week_tips += int((table.food_sales + table.drink_sales) * table.tip_percentage)
    week_sales = food_sales + drink_sales
    tables_per_shift = int(week_tables_count/ week_shifts_count)
    average_tip_percentage = int((week_tips/week_sales) * 100)
    return render(request, template_name, {
        'week':week,
        'tables': week_tables_count,
        'shifts':week_shifts_count,
        'week_sales': week_sales,
        'food_sales': food_sales,
        'drink_sales': drink_sales,
        'hours': hours,
        'customers': customers,
        'average_tip_percentage': average_tip_percentage,
        'week_tips': week_tips,
        'average_tips_hourly': int(week_tips/ hours),
        'average_tips_shift': int(week_tips/ week_shifts_count),
        'average_tips_table': int(week_tips/ week_tables_count),
        'average_tips_customer': int(week_tips / customers),
        'average_sales_hourly': int(week_sales/ hours),
        'average_sales_shift': int(week_sales/ week_shifts_count),
        'average_sales_table': int(week_sales/ week_tables_count),
        'average_sales_customer': int(week_sales / customers),
        'tables_per_shift': tables_per_shift
    })

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






