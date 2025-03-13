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
    template = loader.get_template('landing_page.html')
    return HttpResponse(template.render())

def register_org(request):
    dropdown_options = ["Org 1", "Org 2", "Org 3"]  #Hardcoded data for now 
    return render(request, "registerorg.html", {"options": dropdown_options})
    