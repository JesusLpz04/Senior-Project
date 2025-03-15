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
    path('registerorg/', views.register_org, name='registerorg'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('expenses/', views.expenses_view, name='expenses'),
    path('voting/', views.voting_view, name='voting'),
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('manageOrg/', views.manageOrg_view, name='manageOrg'),
    path('treasuryTickets/', views.treasuryTickets_view, name='treasuryTickets'),
    path('budgetReview/', views.budgetReview_view, name='budgetReview'),

    
]