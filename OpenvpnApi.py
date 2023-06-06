from flask import Flask, make_response, request, jsonify
import requests
from requests.auth import HTTPBasicAuth

app = Flask(__name__)



@app.route('/token', methods=['POST'])
def get_token():

    try:
        body = request.get_json()

        if not body:
            return jsonify({'error': 'Invalid request body'}), 400

        client_id = body.get('client_id')
        client_secret = body.get('client_secret')

        if not client_id or not client_secret:
            error_message = 'Missing client_id or client_secret'
            return jsonify({'error': error_message}), 400

        token_url = "https://api.openvpn.com/api/beta/oauth/token"

        default_grant_type = "client_credentials"

        params = {

            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': default_grant_type
        }
        
        response = requests.post(token_url, params=params)
        json_data = response.json()
        return jsonify(json_data), response.status_code

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        status_code = 500
        return jsonify({'error': error_message}), status_code


@app.route("/user", methods=["POST"])
def create_user():
    try:
        body = request.get_json()

        if not body:
            return jsonify({'error': 'Invalid request body'}), 400

        bearer_token = body.get('bearer_token')
        username = body.get('username')

        if not bearer_token:
            error_message = 'Missing bearer_token'
            return jsonify({'error': error_message}), 400

        url = "https://api.openvpn.com/api/beta/users"

        payload = {
            "devices": [
                {
                    "name": f"{username}_device"
                }
            ],
            "role": "MEMBER",
            "username": username
        }

        headers = {
            'Authorization': f'Bearer {bearer_token}'
        }

        vpn_response = requests.post(url, json=payload, headers=headers)

        if vpn_response.status_code == 201:

            response_data = {
                "userid": vpn_response.json().get("id"),
                "groupId": vpn_response.json().get("groupId"),
                "deviceId": vpn_response.json().get("devices")[0].get("id")
            }
            return jsonify(response_data), vpn_response.status_code
        else:
            return jsonify(vpn_response.json()), vpn_response.status_code

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        status_code = 500
        return jsonify({'error': error_message}), status_code

@app.route("/profile",methods=["POST"])
def get_profile():

    try :
        body = request.get_json()

        regionId = body.get('regionId')
        userId = body.get('userId')
        deviceId = body.get('deviceId')
        bearer_token = body.get('bearer_token')
        if not body or not regionId or not userId or not deviceId :
            error_message = 'invalid body request'
            return jsonify({'error': error_message}), 400


        url = f"https://harb.api.openvpn.com/api/beta/devices/{deviceId}/profile"


        params = {
            "regionId": regionId,
            "userId": userId
        }

        headers = {
            "accept": "text/plain",
            'Authorization': f'Bearer {bearer_token}'
        }


        response = requests.request("POST", url, params=params, headers=headers)
        profile_data = response.text
        return profile_data ,response.status_code

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        status_code = 500
        return jsonify({'error': error_message}), status_code


@app.route("/create_user_profile", methods=["POST"])
def create_user_and_get_profile():
    try:
        body = request.get_json()

        if not body:
            return jsonify({'error': 'Invalid request body'}), 400

        bearer_token = body.get('bearer_token')
        username = body.get('username')
        regionId = body.get('regionId')

        if not bearer_token:
            error_message = 'Missing bearer_token'
            return jsonify({'error': error_message}), 400

        # Create user
        user_url = "https://api.openvpn.com/api/beta/users"

        user_payload = {
            "devices": [
                {
                    "name": f"{username}_device"
                }
            ],
            "role": "MEMBER",
            "username": username
        }

        user_headers = {
            'Authorization': f'Bearer {bearer_token}'
        }

        user_response = requests.post(user_url, json=user_payload, headers=user_headers)

        if user_response.status_code != 201:
            return jsonify(user_response.json()), user_response.status_code

        user_data = user_response.json()
        user_id = user_data.get("id")
        device_id = user_data.get("devices")[0].get("id")
        print(user_data)

        # Get profile
        profile_url = f"https://api.openvpn.com/api/beta/devices/{device_id}/profile"


        profile_params = {
            "regionId": regionId,
            "userId": user_id
        }

        profile_headers = {
            'Authorization': f'Bearer {bearer_token}',
            "accept": "text/plain",
        }

        profile_response = requests.request("POST", profile_url, params=profile_params, headers=profile_headers)

        if profile_response.status_code != 200:
            return profile_response.text ,profile_response.status_code
        profile_data = profile_response.text

        return profile_data ,profile_response.status_code

    except requests.exceptions.RequestException as e:
        error_message = str(e)
        status_code = 500
        return jsonify({'error': error_message}), status_code

@app.route('/regions', methods=['POST'])
def get_regions():

    url = 'https://api.openvpn.com/api/beta/regions'

    body = request.get_json()

    if not body:
        return jsonify({'error': 'Invalid request body'}), 400

    bearer_token = body.get('bearer_token')

    if not bearer_token:
        error_message = 'Missing bearer_token'
        return jsonify({'error': error_message}), 400
    
    headers = {
        'accept': 'application/json',
         'Authorization': f'Bearer {bearer_token}'
    }
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        regions = response.json()
        return jsonify(regions)
    else:
        return jsonify({'error': 'Failed to fetch regions'}), response.status_code






if __name__ == '__main__':
    app.run(debug=True)