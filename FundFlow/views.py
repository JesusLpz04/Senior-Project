from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .forms import CreatePollForm, CreateTicketForm, SignUpForm
from .models import Poll, CreateTicket, UserProfile, CustomCategory, TicketManager
from django.contrib.auth import login #,authenticate, logout
from django.contrib.auth.models import Group, User

def fund_flow(request):
    return HttpResponse("Hello, this is your fundflow method!")

def home_logIn(request):
    return render(request, 'home.html', {})

@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST) # Reference the signupform form
        if form.is_valid():
            user = form.save() # Create user instance 

            # Create associated UserProfile for user.
            UserProfile.objects.create(
                user=user,
                user_type='member'#default to member upon creation, can upgrade later
            )
            
            # Always assign new users as members
            group = Group.objects.get_or_create(name='Members')
            user.groups.add(group)
            

            # Signup success message shown in Django admin.
            messages.success(request, 'Account created successfully!')
            login(request, user)
            
            return redirect('dashboard')
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'signUp.html', context)


#later, will require login
def register_org(request):
    dropdown_options = ["Org 1", "Org 2", "Org 3"]  #Hardcoded data for now 
    return render(request, "registerorg.html", {"options": dropdown_options})

def dashboard_view(request):
    template = loader.get_template('dashboard.html')
    return HttpResponse(template.render())

def expenses_view(request):
    tickets = CreateTicket.objects.all()  #grab updated tickets for log display
    balance = CreateTicket.objects.get_balance()     
    return render(request, 'expenses.html', {'tickets': tickets, 'balance':balance}) 

def createticket_view(request):
    if request.method == "POST":
        form = CreateTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            
            if ticket.expense_category == "other" and request.POST.get("new_custom_category"):
                custom_category_name = request.POST["new_custom_category"]
                custom_category = CustomCategory.objects.get_or_create(name=custom_category_name)
                ticket.custom_category = custom_category
            
            ticket.save()
            return redirect('expenses')
    else:
        form = CreateTicketForm()
    
    return render(request, "createTicket.html", {"form": form})

# Voting page views
def voting_view(request):
    polls = Poll.objects.all()
    context = {
        'polls' : polls
    }
    template = loader.get_template('voting/voting.html')
    return HttpResponse(template.render(context, request)) 

def createPoll_view(request):
    if request.method == 'POST':
        form = CreatePollForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('voting')
    else:
        form = CreatePollForm()
    context = {
        'form' : form
    }
    template = loader.get_template('voting/createPoll.html')
    return HttpResponse(template.render(context, request))

def voteForPoll_view(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    
    if request.method == 'POST':
        selected_option = request.POST['poll']
        if selected_option == 'option1':
            poll.option_one_count += 1
        elif selected_option == 'option2':
            poll.option_two_count += 1
        elif selected_option == 'option3':
            poll.option_three_count += 1
        else:
            return HttpResponse(400, 'Invalid Form')
    
        poll.save()

        return redirect('resultsPoll', poll.id)

    context = {
        'poll' : poll
    }
    template = loader.get_template('voting/voteForPoll.html')
    return HttpResponse(template.render(context, request))

def resultsPoll_view(request, poll_id):
    poll = Poll.objects.get(pk=poll_id)
    context = {
        'poll' : poll
    }
    template = loader.get_template('voting/resultsPoll.html')
    return HttpResponse(template.render(context, request)) 
# End of voting page views
def marketplace_view(request):
    template = loader.get_template('marketplace.html')
    return HttpResponse(template.render()) 

def manageOrg_view(request):
    template = loader.get_template('manageOrg.html')
    return HttpResponse(template.render())

def budgetRequests_view(request):
    template = loader.get_template('budgetRequests.html')
    return HttpResponse(template.render())

def budgetReview_view(request):
    template = loader.get_template('budgetReview.html')
    return HttpResponse(template.render())

def sellGoodies_view(request):
    template = loader.get_template('sellGoodies.html')
    return HttpResponse(template.render())