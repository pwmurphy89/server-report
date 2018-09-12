from django.conf.urls import url
from . import views

app_name = "website"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_user, name='login'),
    url(r'^logout$', views.user_logout, name='logout'),
    url(r'^register$', views.register, name='register'),
    url(r'^sell$', views.sell_product, name='sell'),
    url(r'^products$', views.list_products, name='list_products'),
    url(r'^total$', views.total_sales, name='total_sales'),
    url(r'^month$', views.month_sales, name='month'),
    url(r'^week$', views.week_sales, name='week'),
    # url(r'^shift$', views.shift, name='shift'),
]