from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader

from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .forms import CreatePollForm, CreateTicketForm, SignUpForm
from .models import Poll, CreateTicket, UserProfile, Organization
from django.contrib.auth import login #,authenticate, logout
from django.contrib.auth.models import Group, User

def fund_flow(request):
    return HttpResponse("Hello, this is your fundflow method!")

def home_logIn(request):
    return render(request, 'home.html', {})


# def signup_view(request):
#     template = loader.get_template('signUp.html')
#     return HttpResponse(template.render())

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
    # Organization.objects.create(
    #     name="testOrg2",
    #     description="This is a description of my new organization 2."
    # )
    current_user = request.user

    print(current_user)
    orgs= Organization.objects.all()
    context = {
        'orgs':orgs
    }
    if request.method == 'POST':
        org_id = request.POST.get('org_id')
        org = Poll.objects.get(pk=org_id)
        return redirect('joinOrg', org.id)
    # template = loader.get_template('dashboard.html')
    # return HttpResponse(template.render(context))
    return render(request, 'dashboard.html', context)

def expenses_view(request):
    tickets = CreateTicket.objects.all()  #grab updated tickets for log display
    return render(request, 'expenses.html', {'tickets': tickets}) 

def createticket_view(request):
    if request.method == 'POST':
        form = CreateTicketForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('expenses')
    else:
        form = CreateTicketForm()

    return render(request, 'createTicket.html', {'form': form})

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
    display=""
    # for user in User:
    #     if user.username == "testdummy":
    #         pres = user
    # Organization.objects.create(
    #     name="testOrg1",
    #     description="This is a description of my new organization."
    # )
    orgs = Organization.objects.filter(name='testOrg2')
    #users=User.objects.all()
    for i in orgs:
        orgs=i
        print(i.name)
    membersLst=orgs.pending_members.all()
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        if form_type == 'members' :
            display = 'members'
            membersLst=orgs.members.all()

        if form_type == 'pending':
            display ='pending'
            membersLst=orgs.pending_members.all()

        if form_type == 'remove':
            display='members'
            user_id = request.POST.get('members_user_id')
            user = User.objects.get(pk=user_id)
            orgs.members.remove(user)

        if form_type == 'add':
            display='pending'
            user_id = request.POST.get('pending_user_id')
            user = User.objects.get(pk=user_id)
            print(user)
            orgs.approve_membership(user)

    # user = User.objects.filter(username='testdummy2')
    # for i in user:
    #     user = i

    # orgs.request_membership(user)
 
    context = {
        'orgs' : orgs,
        #'users' : users,
        'membersLst': membersLst,
        'display': display
    }
    template = loader.get_template('manageOrg.html')
    return HttpResponse(template.render(context,request))

def budgetRequests_view(request):
    template = loader.get_template('budgetRequests.html')
    return HttpResponse(template.render())

def budgetReview_view(request):

    expenses = {"dues": 1200, "Food": 500, "merch": 200, "utilities": 150}


    labels = ', '.join(f'"{label}"' for label in expenses.keys()) 
    values = ', '.join(str(value) for value in expenses.values())  

    script = f"""
    var ctx = document.getElementById('budgetChart').getContext('2d');
    new Chart(ctx, {{
        type: 'pie',
        data: {{
            labels: [{labels}],
            datasets: [{{
                data: [{values}],
                backgroundColor: ['#ff6384', '#36a2eb', '#ffcd56', '#4bc0c0', '#9966ff']
            }}]
        }}
    }});
    """

    return render(request, 'budgetReview.html', {"chart_script": script})
    # template = loader.get_template('budgetReview.html')
    # return HttpResponse(template.render())


def sellGoodies_view(request):
    template = loader.get_template('sellGoodies.html')
    return HttpResponse(template.render())

def joinOrg_view(request,org_id):
    org = Organization.objects.get(pk=org_id)

    context={
        'org':org
    }
    current_user= request.user
    if request.method == 'POST':
        org.request_membership(current_user)
        return redirect('dashboard')


    return render(request, 'joinOrg.html', context)