from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.template import loader
import logging

from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from .forms import CreatePollForm, CreateTicketForm, SignUpForm, FundingRequestForm
from .models import Poll, CreateTicket, UserProfile, Membership, Organization, TicketManager, FundingRequest
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User

logger = logging.getLogger(__name__)

from decimal import Decimal


@login_required
def check_auth(request):
    print(f"Current user: {request.user}")
    print(f"Is authenticated: {request.user.is_authenticated}")
    return HttpResponse(f"You are logged in as {request.user.username}")


def home_logIn(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Changed from username to email
        password = request.POST.get('password')
        
        # Get the username associated with the email
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
            
            # Now authenticate with the username
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid password.')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
            
    return render(request, 'home.html', {})

def logout_view(request):
    logout(request)
    return redirect('home')


@csrf_protect
#separating global identity (User/UserProfile) from per-org relationships (Membership)
#does not create Membership upon sign up
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
                    user_type='guest' #default to guest upon creation, upgrades come with membership creation
                )

                # Add to group
                group, _ = Group.objects.get_or_create(name='Guests') # Always assign new users as guests 
                user.groups.add(group)

                messages.success(request, 'Account created successfully!') #on django admin
                login(request, user)
                return redirect('dashboard')
    else:
        form = SignUpForm()

    context = {'form': form}
    return render(request, 'signUp.html', context)

@login_required
def dashboard_view(request):
    
    #User INfo
    cur_user = request.user
    cur_prof = UserProfile.objects.get(user=cur_user)

    # Get memberships across various orgs for User
    user_memberships = Membership.objects.filter(user=cur_user)
    active_org_ids = user_memberships.filter(status='active').values_list('organization_id', flat=True)
    belongsOrgs = Organization.objects.filter(id__in=active_org_ids)
    pendsOrgs = Organization.objects.filter(
        id__in=user_memberships.filter(status='pending').values_list('organization_id', flat=True)
    )
    
    # Orgs user is NOT a part of
    orgs = Organization.objects.exclude(id__in=user_memberships.values_list('organization_id', flat=True))

    #Search for orgs
    if request.method == 'POST':
        form_type = request.POST.get('dashb')
        if form_type == 'search':
            inp = request.POST.get('seb')
            if inp:
                orgs = orgs.filter(name__icontains=inp)  # filter among orgs user isn't in
        elif form_type == 'viewJoin':
            org_id = request.POST.get('org_id')
            org = Organization.objects.get(pk=org_id)
            return redirect('joinOrg', org.id)
        elif form_type == 'explore':
            apt_id = request.POST.get('apt_id')
            orgd = Organization.objects.get(pk=apt_id)
            cur_prof.current_Org = orgd
            cur_prof.save()

            membership = Membership.objects.get(user=cur_user, organization=orgd)
            cur_prof.membership = membership
            cur_prof.membership.role = membership.role
            cur_prof.save()

            return redirect('dashboard')

    context = {
        'orgs': orgs,
        'belongsOrgs': belongsOrgs,
        'pendsOrgs': pendsOrgs,
        'user_type': cur_prof.user_type,
    }
    return render(request, 'dashboard.html', context)

#later, will require login
def register_org(request):
    dropdown_options = ["Org 1", "Org 2", "Org 3", "Org 4", "Org 5","testOrg2"]  #Hardcoded data for now 
    cur_user=request.user
    cur_prof= UserProfile.objects.get(user=cur_user)
    print(cur_prof)
    if request.method == 'POST':
        agree= request.POST.get('agree')
        makeOrg= request.POST.get('dropdown')
        desc=request.POST.get('desc')
        if agree == "on":
            exist=Organization.objects.filter(name=makeOrg)
            if exist.exists()==False:
                print("Making new org")
                new_org=Organization.objects.create(
                    name=makeOrg,
                    description=desc,
                )
                
                Membership.objects.create(
                    user=cur_user,
                    organization=new_org,
                    role='president',
                    status='active'
                )
                
                print(cur_prof.user_type)
                membership = Membership.objects.get(user=request.user, organization=org)
                print(membership.role)

            return redirect('dashboard')

    return render(request, "registerorg.html", {"options": dropdown_options})

def expenses_view(request):
    tickets = CreateTicket.objects.all().order_by('date', 'id')  
    balance = CreateTicket.objects.get_balance()
    running_balance = Decimal('0.00')
    ticket_data = []

    for ticket in tickets:
        operation_symbol = '+' if ticket.operation == 'add' else '-'  
        amount = ticket.amount if ticket.operation == 'add' else -ticket.amount
        running_balance += amount
        ticket_data.append({
            'ticket': ticket,
            'balance': running_balance,
            'operation_symbol': operation_symbol  
        })

    return render(request, 'expenses.html', {
    'tickets_with_balance': list(reversed(ticket_data)),  
    'balance': balance  
    })
    
@login_required
def createticket_view(request):
    if request.method == 'POST':
        form = CreateTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.save()
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
    curUser=request.user
    inOrg=Organization.objects.filter(president=curUser)
    curProf=UserProfile.objects.get(user=curUser)
    print(curProf.user_type=="member")
    print(curProf.current_Org.president)
    if curProf.user_type== "member" or curProf.current_Org.president != curUser :
        return render(request, 'noAccess.html')
        orgs = Organization.objects.filter(name='testOrg1')

    # for i in inOrg:
    #     print(i.president)
    #     if i.president == curUser :
    #         orgs= i
    #     else:
    #         orgs = Organization.objects.filter(name='testOrg1')
    orgs=curProf.current_Org
    display=""
    # for user in User:
    #     if user.username == "testdummy":
    #         pres = user
    # Organization.objects.create(
    #     name="testOrg2",
    #     description="This is a description of my new organization."
    # )
   # orgs = Organization.objects.filter(name='testOrg1')
    #users=User.objects.all()
    # for i in orgs:
    #     orgs=i
    #     print(i.name)
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
    user_type=curProf.user_type
    context = {
        'orgs' : orgs,
        'user_type' : user_type,
        'membersLst': membersLst,
        'display': display
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
@require_http_methods(["POST"])
def create_funding_request(request):
    # Explicit check for AJAX request
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({
            'error': 'Only AJAX requests are supported'
        }, status=400)
    
    form = FundingRequestForm(request.POST)
    
    try:
        if form.is_valid():
            funding_request = form.save(commit=False)
            funding_request.user = request.user
            funding_request.save()
            
            return JsonResponse({
                'id': funding_request.id,
                'subject': funding_request.subject,
                'status': funding_request.status,
                'created_at': funding_request.created_at.strftime('%Y-%m-%d %H:%M')
            })
        else:
            # Return form errors as JSON
            return JsonResponse({
                'errors': form.errors
            }, status=400)
    
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

@login_required
def budgetReview_view(request):
    ticks=CreateTicket.objects.all()
    print(ticks)
    labels = ', '.join(f'"{i.expense_category}"' for i in ticks)
    values = ', '.join(str(i.amount) for i in ticks)
    print(labels)
    # for i in ticks:
    #     print(i.confirmation.join(","))

    # expenses = {"dues": 1200, "Food": 500, "merch": 200, "utilities": 150}


    # labels = ', '.join(f'"{label}"' for label in expenses.keys()) 
    # values = ', '.join(str(value) for value in expenses.values())  
    # print(labels)
    # print(values)
    curUser=request.user
    curProf=UserProfile.objects.get(user=curUser)
    user_type=curProf.user_type
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
    return render(request, 'budgetReview.html', {"chart_script": script, "user_type": user_type})
    # template = loader.get_template('budgetReview.html')
    # return HttpResponse(template.render())

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
def manageMarketplace_view(request):
    curUser=request.user
    curProf=UserProfile.objects.get(user=curUser)
    user_type=curProf.user_type
    context={
        'user_type':user_type
    }
    return render(request, 'manageMarketplace.html',context)