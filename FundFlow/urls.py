from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.conf import settings



urlpatterns = [
    #tester
    path('fundflow/', views.fund_flow, name='FundFlow'),
    path('check-auth/', views.check_auth, name='check_auth'),
    #path for home, which is the login page
    path('', views.home_logIn, name='home'),
    path('signup/', views.signup_view, name='signUp'),
    path('logout/', views.logout_view, name='logout'),
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
    path('fundingRequests/', views.fundingRequests_view, name='fundingRequests'),
    path('fundingRequests/create/', views.create_funding_request, name='create_funding_request'),
    path('budgetReview/', views.budgetReview_view, name='budgetReview'),
    path('manageMarketplace/', views.manageMarketplace_view, name='manageMarketplace'),
    path('joinOrganization/<org_id>', views.joinOrg_view, name='joinOrg'),
    
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)