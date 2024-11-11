from google.oauth2 import service_account
import google.auth.transport.requests
import requests
import json



#testing page not needed but goood example of how to test methods by running just a page at a time  and debuging
# api_key = 
# Set up credentials with the correct scope
credentials = service_account.Credentials.from_service_account_file(
    "travel-planner-441113-ae2d0dd561d6.json",
    scopes=["https://www.googleapis.com/auth/maps-platform.places"]
)

# Generate an access token
auth_request = google.auth.transport.requests.Request()
credentials.refresh(auth_request)
access_token = credentials.token



# Step 1: Text-based search for activities
search_results = text_search_activities("honolulu snorkeling", api_key)
for result in search_results['results']:
    place_id = result['place_id']
    # Step 2: Get detailed activity information
    activity_details = get_activity_details(place_id, api_key)
    # Step 3: Display activity details with photo
    display_activity_info(activity_details['result'], api_key)