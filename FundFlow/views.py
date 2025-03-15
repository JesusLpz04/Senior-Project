from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

def fund_flow(request):
    return HttpResponse("Hello, this is your fundflow method!")

def home_logIn(request):
    return render(request, 'home.html', {})


def signup_view(request):
    template = loader.get_template('signUp.html')
    return HttpResponse(template.render())

#later, will require login
def landing_page(request):
    template = loader.get_template('landingPage.html')
    return HttpResponse(template.render())

def register_org(request):
    dropdown_options = ["Org 1", "Org 2", "Org 3"]  #Hardcoded data for now 
    return render(request, "registerorg.html", {"options": dropdown_options})

def dashboard_view(request):
    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render())

def expenses_view(request):
    template = loader.get_template('expenses.html')
    return HttpResponse(template.render())
     
def voting_view(request):
    template = loader.get_template('voting.html')
    return HttpResponse(template.render())  

def marketplace_view(request):
    template = loader.get_template('marketplace.html')
    return HttpResponse(template.render()) 

def manageOrg_view(request):
    template = loader.get_template('manageOrg.html')
    return HttpResponse(template.render())

def treasuryTickets_view(request):
    template = loader.get_template('treasuryTickets.html')
    return HttpResponse(template.render())

def budgetReview_view(request):
    template = loader.get_template('budgetReview.html')
    return HttpResponse(template.render())