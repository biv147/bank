from django.urls import path

from . import views

#specify url mapping
urlpatterns = [
    path('', views.frontpage, name='frontpage'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('home', views.home, name='home'),
    path('logout', views.logout, name='logout'),
    path('table', views.table, name='table'),
    path('deposit', views.deposit, name='deposit'),
    path('withdraw', views.withdraw, name='withdraw'),
    path('contact', views.contact, name='contact'),
    path('transfer', views.transfer, name='transfer')
    # can have index.html in name as well if u want to link html page
]