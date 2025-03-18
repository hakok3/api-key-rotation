import threading
import requests
import json
import re
import urllib3

from DBConnect import deactivate_app_details, fetch_app_details, insert_app_details

# Disable InsecureRequestWarning to avoid warnings about unverified HTTPS requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
api_base_url = "https://key-rotation-ctem-inter-hip-tech-apigw.apps.ocp-dc8-03.ikeadt.com/keyRotate"
headers = {
    'Content-Type': 'application/json'
}

def generate_new_application(api_key, app_id):
    # Construct the URL for the API endpoint
    url = f"{api_base_url}/genApps"
    
    # Define the headers for the request
    headers = {
        'Content-Type': 'application/json',
        'api-key': api_key,
        'app-id': app_id,
    }
    
    # Define the data payload for the request
    data = {
        "applications": [
            {
                "appId": app_id,
                "apiKey": api_key
            }
        ]
    }
    
    # Print the URL, headers, and data for debugging purposes
    print("URL: " + url)
    print("HEADERS: " + str(headers))
    print("DATA: " + json.dumps(data, indent=4))
    
    # Send the POST request to the API endpoint
    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("New application generated successfully.")
        try:
            response_text = response.text
            print(response_text)
            
            # Extract values using regular expressions
            old_app_id = re.search(r'Old AppId\s*:\s*(\d+)', response_text).group(1)
            new_app_id = re.search(r'New AppId\s*:\s*(\d+)', response_text).group(1)
            new_api_key = re.search(r'New ApiKey\s*:\s*([\w-]+)', response_text).group(1)
            
            # Print the extracted values
            print(f"Old AppId: {old_app_id}")
            print(f"New AppId: {new_app_id}")
            print(f"New ApiKey: {new_api_key}")
            
            # Return the extracted values
            return old_app_id, new_app_id, new_api_key
        except (json.JSONDecodeError, AttributeError) as e:
            print("Response is not in JSON format or parsing error occurred.")
            print(response.text)
            return None
    else:
        print("Failed to generate new application.")
        print(response.text)
        return None

def suspend_plans(api_key, app_id):
    # Construct the URL for the API endpoint
    url = f"{api_base_url}/singleApp"
    
    # Update headers with API key and App ID
    headers.update({'api-key': api_key, 'app-id': app_id})
    
    # Send the POST request to the API endpoint
    response = requests.post(url, headers=headers, verify=False)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Plans suspended successfully.")
        return True
    else:
        print("Failed to suspend plans.")
        print(response.text)
        return False

def decommission_application(api_key, app_id):
    # Construct the URL for the API endpoint
    url = f"{api_base_url}/deleteApp"
    
    # Update headers with API key and App ID
    headers.update({'api-key': api_key, 'app-id': app_id})
    
    # Send the POST request to the API endpoint
    response = requests.post(url, headers=headers, verify=False)
    
    # Check if the request was successful
    if response.status_code == 200:
        print("Application decommissioned successfully.")
        return True
    else:
        print("Failed to decommission application.")
        print(response.text)
        return False

def process_record(application_name, app_key, app_id):
    print(f"App Key: {app_key}, App ID: {app_id}")
    api_key = app_key #"90a01e4f-c259-4c60-bda1-d08b132e784c"
    
    # Step 1: Generate new application
    result = generate_new_application(api_key, app_id)
    if result:
        old_app_id, new_app_id, new_api_key = result
        
        print(f"Old AppId: {old_app_id}")
        print(f"New AppId: {new_app_id}")
        print(f"New ApiKey: {new_api_key}")
        insert_app_details(application_name, new_api_key, new_app_id, "active")
        # Step 2: Suspend plans for the old application
        if suspend_plans(api_key, old_app_id):
            # Step 3: Decommission the old application
            if decommission_application(api_key, old_app_id):
                deactivate_app_details(api_key,old_app_id)
                print("All steps completed successfully.")
            else:
                print("Failed to decommission the old application.")
        else:
            print("Failed to suspend plans for the old application.")
    else:
        print("Failed to generate new application.")

def main():
    # Call the fetch_app_details function and store the returned data
    app_details = fetch_app_details()
   
    # Print the returned data
    if app_details:
        threads = []
        for row in app_details:
            application_name, app_key, app_id = row
            print(f"Application Name: {application_name}, App Key: {app_key}, App ID: {app_id}")
            # Create a new thread for each record
            # thread = threading.Thread(target=process_record, args=(application_name,app_key, app_id))
            # threads.append(thread)
            # thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
            
            
    else:
        print("No data found or an error occurred.")
        
    

if __name__ == "__main__":
    main()