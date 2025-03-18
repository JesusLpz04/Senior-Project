from django.urls import path
from . import views

urlpatterns = [
    #tester
    path('fundflow/', views.fund_flow, name='FundFlow'),
    #path for home, which is the login page
    path('', views.home_logIn, name='home'),
    path('signup/', views.signup_view, name='signUp'),
    #path('logout/', views.logout_view, name='logout'),
    path('registerorg/', views.register_org, name='registerorg'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('expenses/', views.expenses_view, name='expenses'),
    path('createticket/', views.createticket_view, name='createticket'),
    #voting will have 3 views in total: create, vote, result
    path('voting/', views.voting_view, name='voting'),
    path('createpoll/', views.createPoll_view, name='createPoll'),
    path('voteforpoll/<poll_id>', views.voteForPoll_view, name='voteForPoll'),
    path('resultspoll/<poll_id>', views.resultsPoll_view, name='resultsPoll'),
    #end of voting views
    path('marketplace/', views.marketplace_view, name='marketplace'),
    path('manageOrg/', views.manageOrg_view, name='manageOrg'),
    path('budgetRequests/', views.budgetRequests_view, name='budgetRequests'),
    path('budgetReview/', views.budgetReview_view, name='budgetReview'),
    path('sellGoodies/', views.sellGoodies_view, name='sellGoodies'),


    
]