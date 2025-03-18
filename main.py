import requests
import json
import re
import urllib3

# Disable InsecureRequestWarning
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Configuration
api_base_url = "https://key-rotation-ctem-inter-hip-tech-apigw.apps.ocp-dc8-03.ikeadt.com/keyRotate"
headers = {
    'Content-Type': 'application/json'
}

def generate_new_application(api_key, app_id):
    url = f"{api_base_url}/genApps"
    headers = {
        'Content-Type': 'application/json',
        'api-key': api_key,
        'app-id': app_id,
    }
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
    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
    
    if response.status_code == 200:
        print("New application generated successfully.")
        # print(response.json())
        try:
            response_text = response.text
            print(response_text)
            
            # Extract values using regular expressions
            old_app_id = re.search(r'Old AppId\s*:\s*(\d+)', response_text).group(1)
            new_app_id = re.search(r'New AppId\s*:\s*(\d+)', response_text).group(1)
            new_api_key = re.search(r'New ApiKey\s*:\s*([\w-]+)', response_text).group(1)
            
            print(f"Old AppId: {old_app_id}")
            print(f"New AppId: {new_app_id}")
            print(f"New ApiKey: {new_api_key}")
            
            return old_app_id, new_app_id, new_api_key
        except (json.JSONDecodeError, AttributeError) as e:
            print("Response is not in JSON format or parsing error occurred.")
            print(response.text)
    else:
        print("Failed to generate new application.")
        print(response.text)

def suspend_plans(api_key, app_id):
    url = f"{api_base_url}/singleApp"
    headers.update({'api-key': api_key, 'app-id': app_id})
    response = requests.post(url, headers=headers,verify=False)
    if response.status_code == 200:
        print("Plans suspended successfully.")
        print(response)
    else:
        print("Failed to suspend plans.")
        print(response.text)

def decommission_application(api_key, app_id):
    url = f"{api_base_url}/deleteApp"
    headers.update({'api-key': api_key, 'app-id': app_id})
    response = requests.post(url, headers=headers,verify=False)
    if response.status_code == 200:
        print("Application decommissioned successfully.")
    else:
        print("Failed to decommission application.")
        print(response.text)

def main():
    api_key = "a948bfae-00f2-47ae-9fb6-678269b58151"
    app_id = "2700"
    # Step 1: Get Data from the database
    print("Hello world")
    # Step 1: Generate new application
    generate_new_application(api_key, app_id)

    # Step 2: Suspend plans for the old application
    suspend_plans(api_key, app_id)

    # Step 3: Decommission the old application
    decommission_application(api_key, app_id)



if __name__ == "__main__":
    main()