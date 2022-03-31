import requests
import json
# import related models here
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, ClassificationsOptions

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))

def get_request(url, api_key, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        if api_key:
            response = requests.get(url, params=kwargs, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:     
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data
# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, None)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer_doc in dealers:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object


            dealer_obj = CarDealer(address=dealer_doc["address"], city=dealer_doc["city"], full_name=dealer_doc["full_name"],
                                   id=dealer_doc["id"], lat=dealer_doc["lat"], long=dealer_doc["long"],
                                   short_name=dealer_doc["short_name"],
                                   st=dealer_doc["st"], state= dealer_doc["state"], zip=dealer_doc["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealerID , **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, None, dealerID=dealerID)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer_doc in dealers:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object

            if "car_make" not in dealer_doc:
                review_obj = None
            else:
                review_obj = DealerReview(car_make=dealer_doc["car_make"], car_model=dealer_doc["car_model"], car_year=dealer_doc["car_year"],
                                    dealership=dealer_doc["dealership"], id=dealer_doc["id"], name=dealer_doc["name"],
                                    purchase=dealer_doc["purchase"],
                                    purchase_date=dealer_doc["purchase_date"], review= dealer_doc["review"])
                
                review_obj.sentiment = analyze_review_sentiments(review_obj.review)
                results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative


    url = "https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/aeacd8b7-370f-4bc3-9e23-31f89444bc6b/v1/analyze"
    api_key = "9PSFdAwVgYinpWHcfk-Nkg9K5nZfBAYq8LES13vGPsju"
    params = dict()
    params["text"] = text
    params["language"]= "en"
    params["version"] = '2021-08-01'
    params["features"] = {  'sentiment': {}}
    params["return_analyzed_text"] = "true"
    json_result = get_request(url=url, api_key=api_key, **params)

    if json_result:
        if json_result["sentiment"]:
            return json_result["sentiment"]["document"]["label"]
        
    return ' '




