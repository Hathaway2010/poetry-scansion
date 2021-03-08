from django.shortcuts import HttpResponseRedirect, render
from django.http import HttpResponse
from django.urls import reverse
# https://www.kite.com/python/docs/django.contrib.admindocs.views.staff_member_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt
from django.template.defaulttags import register
import random
import json

from .models import User, Pronunciation, Poem
from . import scan


# Create your views here.
def index(request):
    # when a user submits a scansion, score them or record the scansion
    if request.method == "PUT":
        data = json.loads(request.body)
        # if the user has proven themselves, write their scansion to the database
        if request.user.is_authenticated and request.user.promoted:
            # update poem's scansion in the poem table and mark it human-scanned
            p = Poem.objects.get(pk=data["id"])
            p.scansion = data["scansion"]
            p.human_scanned = True
            p.save()
            # use record function from scan.py to update popularities of word scansions
            # in Pronunciation instances
            scan.record(p.poem, p.scansion)
            return HttpResponse()

        # otherwise, score the user
        else:
            u = request.user
            u.points += data["score"]
            u.save()
            # promote the user if their score has reached 10 points
            if u.points >= 10:
                u.promoted = True
                u.save()
            return HttpResponse()
    else:
        # if user is logged in, respond to GET request with a random poem
        if request.user.is_authenticated:
            # https://books.agiliq.com/projects/django-orm-cookbook/en/latest/random.html
            if request.user.promoted:
                # if user is promoted, choose poem from all poems
                poem = Poem.objects.all().order_by("?").first()
            else:
                # otherwise, whether user logged in or not display poem
                # chosen from only human-scanned poems
                poem = Poem.objects.filter(human_scanned=True).order_by("?").first()

        else:
            poem = Poem.objects.filter(human_scanned=True).order_by("?").first()
        return render(request, "app/index.html", {"poem": poem})

def about(request):
    return render(request, "app/about.html")

# taken from distribution code for social network
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "app/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "app/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "app/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "app/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "app/register.html")

# allow admins to add new poems to database
@staff_member_required
def import_poem(request):
    if request.method == "POST":
        # get data input about poem
        title = request.POST["title"]
        poem = request.POST["poem"]
        poet = request.POST["poet"]
        human_scanned = False
        scansion = scan.house_robber_scan(poem)
        # if poem already in database, overwrite it
        p = Poem.objects.filter(poem=poem)
        if p.exists():
            for item in p:
                item.poem = poem
                item.poet = poet
                item.title = title
                item.scansion = scansion
                item.save()
        # otherwise, save new poem
        else:
            p = Poem(title=title, poem=poem, poet=poet, scansion=scansion, human_scanned=human_scanned)
            p.save()
        return HttpResponse(scansion)

    else:
        return render(request, "app/import_poem.html")

def choose_poem(request):
    # allow user to choose a poem to scan
    human_list = Poem.objects.filter(human_scanned=True).order_by("poet")
    computer_list = Poem.objects.filter(human_scanned=False).order_by("poet")
    return render(request, "app/choose_poem.html", {"human_list": human_list, "computer_list": computer_list})

def poem(request, id):
    # render the chosen poem instead of a random poem on index.html
    poem = Poem.objects.get(pk=id)
    return render(request, "app/index.html", {"poem": poem })
