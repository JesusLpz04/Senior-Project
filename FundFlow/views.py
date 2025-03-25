from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader

from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .forms import CreatePollForm, CreateTicketForm, SignUpForm, FundingRequestForm
from .models import Poll, CreateTicket, UserProfile, Organization, FundingRequest
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User

def fund_flow(request):
    return HttpResponse("Hello, this is your fundflow method!")

def home_logIn(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Since using email, check email and then make username
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            pass
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('dashboard')  # Redirect to dashboard after login
        else:
            messages.error(request, 'Invalid username or password.')
            
    return render(request, 'home.html', {})



def logout_view(request):
    logout(request)
    return redirect('home')

@csrf_protect
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST) # Reference the signupform form
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            # Generate username from email
            username = email.split('@')[0]
            
            if User.objects.filter(email=email).exists():
                messages.error(request, 'A user with this email already exists.')  
                return render(request, 'signUp.html', {'form': form})

            
            else:
                # Create user instance 
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )

                # Create UserProfile
                UserProfile.objects.create(
                    user=user,
                    user_type='member'#default to member upon creation, can upgrade later
                )

                # Add to group
                group, _ = Group.objects.get_or_create(name='Members') # Always assign new users as members
                user.groups.add(group)

                messages.success(request, 'Account created successfully!') #on django admin
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

@login_required
def dashboard_view(request):
    orgs= Organization.objects.all()
    context = {
        'orgs':orgs
    }
    return render(request, 'dashboard.html', context)

@login_required
def expenses_view(request):
    tickets = CreateTicket.objects.all()  #grab updated tickets for log display
    return render(request, 'expenses.html', {'tickets': tickets}) 

@login_required
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
@login_required
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

@login_required
def marketplace_view(request):
    return render(request, 'marketplace.html')

@login_required
def manageOrg_view(request):
    # for user in User:
    #     if user.username == "testdummy":
    #         pres = user
    # Organization.objects.create(
    #     name="testOrg1",
    #     description="This is a description of my new organization."
    # )
    orgs = Organization.objects.filter(name='testOrg1')
    #users=User.objects.all()
    for i in orgs:
        orgs=i
        print(i.name)
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.get(pk=user_id)
        print(user)
        orgs.approve_membership(user)

    # user = User.objects.filter(username='testdummy3')
    # for i in user:
    #     user = i
    # print(user)
    # print(orgs)
    # orgs.request_membership(user)
    members=orgs.pending_members.all()
    context = {
        'orgs' : orgs,
        #'users' : users,
        'members': members
    }
    template = loader.get_template('manageOrg.html')
    return HttpResponse(template.render(context,request))

@login_required
def fundingRequests_view(request):
    # Get all funding requests for display
    funding_requests = FundingRequest.objects.all().order_by('-created_at')
    
    context = {
        'funding_requests': funding_requests
    }
    template = loader.get_template('fundingRequests.html')
    return HttpResponse(template.render(context, request))

# This AJAX view is simplified but still available if you want to use it
@login_required
def create_funding_request(request):
    if request.method == 'POST':
        form = FundingRequestForm(request.POST)
        if form.is_valid():
            funding_request = form.save()
            
            # Return JSON response for AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'id': funding_request.id,
                    'subject': funding_request.subject,
                    'status': funding_request.status,
                    'created_at': funding_request.created_at.strftime('%Y-%m-%d %H:%M')
                })
            
            # Redirect for non-AJAX requests
            return redirect('fundingRequests')
        else:
            # Return form errors
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    
    # This view is mainly for AJAX, so return an error if accessed directly
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@login_required
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

@login_required
def manageMarketplace_view(request):
    return render(request, 'manageMarketplace.html')
    # template = loader.get_template('manageMarketplace.html')
    # return HttpResponse(template.render())