import requests

def get_height_from_flask_app(lat, lon):
    url = "http://127.0.0.1:5000/get_height"

    try:
        # Make a POST request to get the height
        response = requests.post(url, data={'lat': lat, 'lon': lon})

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                height = float(data['height'])
                # print(f"Height at latitude {lat}, longitude {lon}: {height}")
            else:
                print(f"Error: {data['error']}")
                height = 0
        else:
            print(f"Failed to make the request. Status code: {response.status_code}")
        return height
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return 0