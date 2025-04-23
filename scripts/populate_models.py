from django.contrib.auth.models import User
from FundFlow.models import UserProfile, Organization, Membership
import random

def run():
    sample_orgs = [
        {"name": "Robotics Club", "description": "Like Reel Steel, but with more firepower."},
        {"name": "Business Club", "description": "We play Monopoly on Fridays."},
        {"name": "Art Club", "description": "Every art but Corporate Memphis is welcome"},
        {"name": "Music Club", "description": "Ya like jazz?"},
        {"name": "Evil Aliens Club", "description": "Gleep Glorp!!!!!!!!!"},
        {"name": "Gamerz", "description": "I paused my game for this"},
        {"name": "Running Club", "description": "We chase each other."},
        {"name": "Debate Clurb", "description": "Yelling is allowed."},
    ]

    for org in sample_orgs:
        Organization.objects.get_or_create(name=org["name"], defaults={"description": org["description"]})

    orgs = list(Organization.objects.all())

    for i in range(30):
        username = f'user{i}'
        first_name = f'userF{i}'
        last_name = f'userL{i}'
        email = f'user{i}@utrgv.edu'
        password = 'testpassword123'

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
            }
        )
        if not created:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
        user.set_password(password)
        user.save()

        print(f'Created or updated {username}')

        UserProfile.objects.get_or_create(user=user, defaults={'user_type': 'student'})

        num_orgs = random.choice([1, 2])  # ensure they get at least 1 org
        assigned_orgs = random.sample(orgs, min(num_orgs, len(orgs)))

        for org in assigned_orgs:
            role = random.choices(['member', 'treasurer', 'president'], weights=[0.6, 0.2, 0.2])[0]
            membership, mem_created = Membership.objects.get_or_create(
                user=user,
                organization=org,
                defaults={'role': role, 'status': 'active'}
            )
            if mem_created:
                print(f'  - {username} added to {org.name} as {role}')
