from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.template import loader
import logging
from collections import defaultdict

from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from .forms import CreatePollForm, CreateTicketForm, SignUpForm, FundingRequestForm, CreateItemForm
from .models import Poll, CreateTicket, UserProfile, Organization, Item, FundingRequest, Tag, TicketManager #, CartItem
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from paypal.standard.forms import PayPalPaymentsForm
from django.conf import settings 
import uuid
from django.urls import reverse
from django.utils import timezone
from .decorators import unauthorized_user, allowed_users
from collections import defaultdict
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

from decimal import Decimal

@login_required
def check_auth(request):
    print(f"Current user: {request.user}")
    print(f"Is authenticated: {request.user.is_authenticated}")
    return HttpResponse(f"You are logged in as {request.user.username}")

def fund_flow(request):
    return HttpResponse("Hello, this is your fundflow method!")

@unauthorized_user
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

@unauthorized_user
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
            if not email.endswith('@utrgv.edu'):
                messages.error(request,"Only @utrgv.edu email addresses are allowed.")
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
                print("a")
                new_org=Organization.objects.create(
                    name=makeOrg,
                    description=desc,
                    president= cur_user
                )
                new_org.members.add(cur_user)
                cur_prof.user_type = 'president'
                cur_prof.save()
                cur_prof.current_Org=new_org
                cur_prof.save()
                print(cur_prof.user_type)

            return redirect('dashboard')

    return render(request, "registerorg.html", {"options": dropdown_options})

@login_required
def dashboard_view(request):
# Organization.objects.create(
    #     name="testOrg2",
    #     description="This is a description of my new organization 2."
    # )
    current_user = request.user
    curProf=UserProfile.objects.get(user=current_user)

    # print(current_user)
    orgs= Organization.objects.all()
    belongsOrgs= Organization.objects.filter(members=current_user)
    pendsOrgs= Organization.objects.filter(pending_members=current_user)
    # for i in belongsOrgs:
    #     print(i.name)
    # print(belongsOrgs)
    user_type= curProf.user_type
    print(user_type)
    # context = {
    #     'orgs':orgs,
    #     'belongsOrgs':belongsOrgs,
    #     'user_type':user_type
    # }
    if request.method == 'POST':
        form_type = request.POST.get('dashb')
        if form_type == 'search':
            inp=request.POST.get('seb')
            if inp:
                orgs = Organization.objects.filter(name__icontains=inp)
                print(orgs)
            else:
                orgs = Organization.objects.all() 
        if form_type == 'viewJoin' :
            org_id = request.POST.get('org_id')
            org = Organization.objects.get(pk=org_id)
            return redirect('joinOrg', org.id)
        if form_type == 'explore':
            apt_id = request.POST.get('apt_id')
            orgd = Organization.objects.get(pk=apt_id)
            curProf.current_Org= orgd
            curProf.save()
            print(curProf.current_Org)
            if current_user == curProf.current_Org.president:
                curProf.user_type= 'president'
                curProf.save()
            elif current_user == curProf.current_Org.treasurer:
                curProf.user_type= 'treasurer'
                curProf.save()
            else:
                curProf.user_type='member'
                curProf.save()
            print(curProf.user_type)
            return redirect('dashboard')
            #curProf.save()
    # template = loader.get_template('dashboard.html')
    # return HttpResponse(template.render(context))
    context = {
        'orgs':orgs,
        'belongsOrgs':belongsOrgs,
        'user_type':user_type,
        'pendsOrgs':pendsOrgs,
        'curProf':curProf
    }
    return render(request, 'dashboard.html', context)


def expenses_view(request):
    tickets = CreateTicket.objects.all().order_by('date', 'id')  
    balance = CreateTicket.objects.get_balance()
    running_balance = Decimal('0.00')
    ticket_data = []
    curUser = request.user
    curProf = UserProfile.objects.get(user=curUser)
    user_type = curProf.user_type
    curOrg= curProf.current_Org
    if curOrg == None:
         return render(request, 'noAccess.html')
    tic=curOrg.tickets.all()
    print(tic)
    for ticket in tic:
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
    'balance': running_balance, 'user_type':user_type, "curProf":curProf  
    })
    
@login_required
def createticket_view(request):
    curUser = request.user
    curProf = UserProfile.objects.get(user=curUser)
    curOrg= curProf.current_Org
    if request.method == 'POST':
        form = CreateTicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.save()
            curOrg.tickets.add(ticket)
            curOrg.save()
            return redirect('expenses')
    else:
        form = CreateTicketForm()

    return render(request, 'createTicket.html', {'form': form})

# Voting page views

@login_required
def voting_view(request):
    
    current_time = timezone.now()
    current_user = request.user
    
    try:
        curProf = UserProfile.objects.get(user=current_user)
        user_type = curProf.user_type
        
        # Get organizations the user is a member of
        user_orgs = Organization.objects.filter(members=current_user)
        
        # Get polls for those organizations that are still active
        polls_by_org = defaultdict(list)
        
        for org in user_orgs:
            org_polls = Poll.objects.filter(
                organization=org,
                expiration_date__gt=current_time
            )
            
            if org_polls.exists():
                polls_by_org[org] = org_polls
        
    except Exception as e:
        print(f"Error: {str(e)}")
        user_type = None
        polls_by_org = {}
        
    print("Polls by org:", polls_by_org)
    
    context = {
        'polls_by_org': dict(polls_by_org),
        'user_type': user_type,
        'user_orgs': user_orgs
    }

    template = loader.get_template('voting/voting.html')
    return HttpResponse(template.render(context, request))

@allowed_users(allowed_roles=['president', 'treasurer'])
def createPoll_view(request):
    if request.method == 'POST':
        form = CreatePollForm(request.POST, user=request.user)
        if form.is_valid():
            poll = form.save(commit=False)
            poll.created_by = request.user  # Track who created the poll
            poll.save()
            return redirect('voting')
    else:
        form = CreatePollForm(user=request.user)
    
    context = {
        'form': form
    }
    return render(request, 'voting/createPoll.html', context)

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
@allowed_users(allowed_roles=['president', 'treasurer'])
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
    current_user = request.user

    try:
        # Get the user type of the logged in user
        curProf = UserProfile.objects.get(user=current_user)
        user_type = curProf.user_type

        # Get organizations the user is a member of
        user_orgs = Organization.objects.filter(members=current_user)

        # Get all funding requests for display
        funding_requests_by_org = defaultdict(list)

        for org in user_orgs:
            org_requests = FundingRequest.objects.filter(
                organization=org
            ).order_by('created_at')

            if org_requests.exists():
                funding_requests_by_org[org] = org_requests

        # Process status update if form was submitted
        if request.method == 'POST' and (user_type == 'president' or user_type == 'treasurer'):
            request_id = request.POST.get('request_id')
            new_status = request.POST.get('status')
            
            if request_id and new_status:
                funding_request = FundingRequest.objects.get(pk=request_id)
                # Check if user has permission to update this request (belongs to their organization)
                if funding_request.organization in user_orgs:
                    funding_request.status = new_status
                    funding_request.save()
                    
                    
                    # Redirect to prevent form resubmission
                    return redirect('fundingRequests')
        
    except Exception as e:
        print(f"Error: {str(e)}")
        user_type = None
        funding_requests_by_org = {}
        user_orgs = []

    context = {
        'funding_requests_by_org': dict(funding_requests_by_org),
        'user_type': user_type,
        'user_orgs': user_orgs,
    }

    template = loader.get_template('fundingRequests.html')
    return HttpResponse(template.render(context, request))

@login_required
@require_http_methods(["POST"])
def create_funding_request(request):
    # Check for AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if not is_ajax:
        return JsonResponse({
            'error': 'Only AJAX requests are supported'
        }, status=400)
    
    form = FundingRequestForm(request.POST, user=request.user)
    
    try:
        if form.is_valid():
            funding_request = form.save(commit=False)
            funding_request.created_by = request.user
            funding_request.save()
            
            # Return complete data including status display name
            return JsonResponse({
                'id': funding_request.id,
                'subject': funding_request.subject,
                'organization': funding_request.organization.name,
                'status': funding_request.status,
                'status_display': funding_request.get_status_display(),
                'created_at': funding_request.created_at.strftime('%Y-%m-%d %H:%M'),
                'amount': str(funding_request.amount),
                'description': funding_request.description,
                'link': funding_request.link or ''
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
@allowed_users(allowed_roles=['president', 'treasurer'])
def budgetReview_view(request):
    curUser=request.user
    curProf=UserProfile.objects.get(user=curUser)
    user_type=curProf.user_type
    curOrg=curProf.current_Org
    ticks=curOrg.tickets.all()
    category_totals = {}
    for ticket in ticks:
        if ticket.expense_category in category_totals:
            category_totals[ticket.expense_category] += ticket.amount
        else:
            category_totals[ticket.expense_category] = ticket.amount

    labels = ', '.join(f'"{label}"' for label in category_totals.keys())
    values = ', '.join(str(value) for value in category_totals.values())
    # for i in ticks:
    #     print(i.confirmation.join(","))

    # expenses = {"dues": 1200, "Food": 500, "merch": 200, "utilities": 150}


    # labels = ', '.join(f'"{label}"' for label in expenses.keys()) 
    # values = ', '.join(str(value) for value in expenses.values())  
    # print(labels)
    # print(values)

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


@login_required
def marketplace_view(request):
    selected_tag_ids = request.GET.getlist('tags')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    curUser = request.user
    curProf = UserProfile.objects.get(user=curUser)
    user_type = curProf.user_type
    thisOrg = curProf.current_Org
    
    items = Item.objects.all()

    #for search through items
    search_query = request.GET.get('search')
    if search_query:
        items = items.filter(item_name__icontains=search_query)  # adjust "name" to your item model's search-relevant field

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        print(item_id)
        item=Item.objects.get(pk=item_id)
        return redirect('checkout', item.id)

    #for filter
    if selected_tag_ids:
        items = items.filter(tags__id__in=selected_tag_ids).distinct()
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)
        
    #for sort by
    sort_option = request.GET.get('sort')
    if sort_option == 'price_asc':
        items = items.order_by('price')
    elif sort_option == 'price_desc':
        items = items.order_by('-price')


    alltags = Tag.objects.all()
    
    temp_grouped = defaultdict(list)
    for item in items:
        temp_grouped[item.organization.name].append(item)

    grouped_items = dict(temp_grouped)


    
    context = {
        'thisOrg': thisOrg,
        'user_type': user_type,
        'items': items,
        'grouped_items': grouped_items,
        'alltags': alltags,
        'selected_tag_ids': list(map(int, selected_tag_ids)),  
        'selected_tags_raw': selected_tag_ids,
        'min_price': min_price,
        'max_price': max_price, 
        'search_query': search_query, 
        'sort_option': sort_option
    }
    return render(request, 'marketplace.html', context)

def checkout_view(request,item_id):
    itm = Item.objects.get(pk=item_id)

    host = request.get_host()

    org=itm.organization

    orgEmail=org.bank_email
    print(orgEmail)
    paypal_checkout ={
        'business': orgEmail,
        'amount':itm.price,
        'item_name': itm.item_name,
        'invoice': uuid.uuid4(),
        'currency_code': 'USD',
        'notify_url': f"http://{host}{reverse('paypal-ipn')}",
        'return_url': f"http://{host}{reverse('buyConfirm', kwargs ={'item_id':itm.id})}",
        'cancel_url': f"http://{host}{reverse('buyDenied', kwargs ={'item_id':itm.id})}"
    }

    paypal_payment= PayPalPaymentsForm(initial = paypal_checkout)

    context={
        'itm':itm,
        'paypal':paypal_payment
    }
    return render(request, 'checkout.html', context)

def PaymentSuccessful(request,item_id):
    item = Item.objects.get(pk=item_id)

    subject = f"Purchase Confirmation: {item.item_name}"
    message = (
        f"Hello {request.user.first_name},\n\n"
        f"Thank you for purchasing '{item.item_name}'.\n"
        f"Price: ${item.price:.2f}\n"
        f"We hope you enjoy your item!\n\n"
        f"- The Marketplace Team"
    )
    recipient = request.user.email

    # Send the email
    send_mail(subject, message, "utrgvmarketplace@gmail.com", [recipient], fail_silently=False)

    curUser = request.user
    curProf = UserProfile.objects.get(user=curUser)
    user_type = curProf.user_type
    thisOrg = item.organization

    new_ticket=CreateTicket.objects.create(
    amount=item.price,
    date= timezone.now(),
    operation="add",
    expense_category="other",
    description=f"{item.item_name} was sold"
    
    )
    thisOrg.tickets.add(new_ticket)
    item.quantity -= 1
    item.save()

    return render(request, 'buyConfirm.html', {'item': item, 'user_type':user_type})

def Paymentfailed(request,item_id):
    item = Item.objects.get(pk=item_id)
    curUser = request.user
    curProf = UserProfile.objects.get(user=curUser)
    user_type = curProf.user_type
    return render(request, 'buyDenied.html', {'item': item, 'user_type':user_type})

@login_required
@allowed_users(allowed_roles=['president', 'treasurer'])
def manageMarketplace_view(request):
    selected_tag_ids = request.GET.getlist('tags')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    curUser = request.user
    curProf = UserProfile.objects.get(user=curUser)
    user_type = curProf.user_type
    thisOrg = curProf.current_Org

    #for item cards
    items = Item.objects.filter(organization=thisOrg)
    
    #for search through items
    search_query = request.GET.get('search')
    if search_query:
        items = items.filter(item_name__icontains=search_query)  # adjust "name" to your item model's search-relevant field


    #for filter
    if selected_tag_ids:
        items = items.filter(tags__id__in=selected_tag_ids).distinct()
    if min_price:
        items = items.filter(price__gte=min_price)
    if max_price:
        items = items.filter(price__lte=max_price)
        
    #for sort by
    sort_option = request.GET.get('sort')
    if sort_option == 'price_asc':
        items = items.order_by('price')
    elif sort_option == 'price_desc':
        items = items.order_by('-price')


    alltags = Tag.objects.all()
    
    if request.method == 'POST':
        newEmail=request.POST.get('addE')
        if newEmail != "":
        # orgs = Organization.objects.filter(name__icontains=inp)
            thisOrg.bank_email=newEmail
            thisOrg.save()

    context = {
        'thisOrg': thisOrg,
        'user_type': user_type,
        'items': items,
        'alltags': alltags,
        'selected_tag_ids': list(map(int, selected_tag_ids)),  
        'selected_tags_raw': selected_tag_ids,
        'min_price': min_price,
        'max_price': max_price, 
        'search_query': search_query, 
        'sort_option': sort_option
    }

    return render(request, 'manageMarketplace.html', context)





@login_required
def createitem_view(request):
    curUser = request.user
    curProf = UserProfile.objects.get(user=curUser)
    user_type = curProf.user_type
    thisOrg = curProf.current_Org

    if request.method == 'POST':
        form = CreateItemForm(request.POST, request.FILES)
        if form.is_valid():
            new_item = form.save(commit=False)
            new_item.organization = thisOrg  # adding item to current org
            new_item.save()
            form.save_m2m()  
            return redirect('manageMarketplace')
    else:
        form = CreateItemForm()

    items = Item.objects.filter(organization=thisOrg)

    context = {
        'user_type': user_type,
        'form': form,
        'items': items,
    }

    return render(request, 'createitem.html', context)


@login_required
def delete_item_view(request, item_id):
    curUser = request.user
    curProf = UserProfile.objects.get(user=curUser)
    thisOrg = curProf.current_Org

    item = get_object_or_404(Item, id=item_id, organization=thisOrg)

    if request.method == 'POST':
        item.delete()
        return redirect('manageMarketplace')
    
    return render(request, 'confirm_delete.html', {'item': item})


