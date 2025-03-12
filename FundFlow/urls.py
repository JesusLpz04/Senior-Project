from django.urls import path
from . import views

urlpatterns = [
    #tester
    path('fundflow/', views.fund_flow, name='FundFlow'),
    #path for home, which is the login page
    path('', views.home_logIn, name='home'),
    #path for signing up page
    path('signup/', views.signup_view, name='signUp'),
    #path('logout/', views.logout_view, name='logout'),
    path('landingpage/', views.landing_page, name='landingpage'),
    
]