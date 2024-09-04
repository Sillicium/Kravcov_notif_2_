import json

import requests

from reminder.header import headers
from reminder.models import ApiKey


def get_latest_api_key():
    latest_api_key = ApiKey.objects.order_by('-updated_at').first()
    return latest_api_key.key if latest_api_key else None


def create_python_script(file_name, data):
    with open(f'{file_name}.py', 'w') as script_file:
        script_file.write("# Auto-generated script\n\n")
        for key, value in data.items():
            if isinstance(value, str):
                script_file.write(f'{key} = "{value}"\n')
            else:
                script_file.write(f'{key} = {value}\n')


def create_response_json_file(file_name, filtered_response):
    with open(f'{file_name}.json', 'w') as json_file:
        json.dump([filtered_response], json_file, indent=4)


def send_post_request(url, data):
    return requests.post(url, headers=headers, data=data)


def send_get_request(url, data):
    return requests.get(url, headers=headers, params=data)


def response_result(response, file_name):
    if response.status_code in [200, 201]:
        try:
            response_json = response.json()
            print("Response JSON:")
            print(response_json)

            # create_python_script(file_name, response_json)
            with open(f'{file_name}.json', 'w') as json_file:
                json.dump([response_json], json_file, indent=4)

            # if isinstance(response_json, list):
            #     filtered_response = [item for item in response_json if item.get('removed') == 0]
            #     create_response_json_file('create_patient_list_response', filtered_response)
            # elif isinstance(response_json, dict):
            #
            #     create_response_json_file('create_patient_dict_response', [response_json])
            # else:
            #     print("Unexpected response format")

        except json.JSONDecodeError:
            print("Error decoding JSON response")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print(f"Error: Received status code {response.status_code}")
        print(response.text)
