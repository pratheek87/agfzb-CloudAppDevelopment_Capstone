from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
from dateutil import parser

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context = {}
    return render(request, 'djangoapp/about.html', context)

# Create a `contact` view to return a static contact page
def contact(request):
    context = {}
    return render(request, 'djangoapp/contact.html', context)
# Create a `login_request` view to handle sign in request
def login_request(request):   
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp/index.html', context)
    else:
        return render(request, 'djangoapp/index.html', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    if request.method == "GET":
        url = "https://cce9429f.eu-gb.apigw.appdomain.cloud/api/dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        context = {}
        context["dealers"] = dealerships
        # Return a list of dealer short name
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
def get_dealer_details(request, dealerID):
    if request.method == "GET":
        url = "https://cce9429f.eu-gb.apigw.appdomain.cloud/review/review"
        # Get dealers from the URL
        reviews = get_dealer_reviews_from_cf(url, dealerID)
        # Concat all dealer's short name
        #print(reviews)
        review_string =  ' '.join([review.review + "sentiment :" + review.sentiment for review in reviews])
        context = {}

        for review in reviews:
            review.purchase_date_year = parser.parse(reviews[0].purchase_date).date().year

        context["reviews"] = reviews
        context["dealerID"] = dealerID
    return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealerID):

    context = {}
    if request.method == 'GET':
        context["cars"] = CarModel.objects.all()
        context['dealerID'] = dealerID
        return render(request, 'djangoapp/add_review.html', context)
    if request.method == "POST":
        
        url = "https://cce9429f.eu-gb.apigw.appdomain.cloud/postreview/postreview"

        car = CarModel.objects.all()[int(request.POST["car"])-1]

        purchase = False
        if "purchase" in request.POST:
            purchase = True

        review = {
        "id": dealerID,
        "name": str(request.user),
        "dealership": car.dealerID,
        "review": request.POST["review"],
        "purchase": purchase,
        "purchase_date":request.POST["purchase_date"],
        "car_make": car.name,
        "car_model": car.carmodels.name,
        "car_year": car.year.strftime("%m/%d/%Y")
        }

        json_payload = {}
        json_payload["review"] = review
        print(review)
        response = post_request(url, json_payload)
        return  redirect("djangoapp:dealer_details", dealerID)