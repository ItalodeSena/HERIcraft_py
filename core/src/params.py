from geopy.distance import geodesic

def calculate_bounding_box(midpoint, length_km, width_km):
    # Convert length and width from kilometers to degrees
    length_deg = geodesic(kilometers=length_km).meters / 111000
    width_deg = geodesic(kilometers=width_km).meters / 111000

    # Extract latitude and longitude from the midpoint
    mid_latitude, mid_longitude = midpoint

    # Calculate the bounding box coordinates
    min_latitude = mid_latitude - (width_deg / 2)
    max_latitude = mid_latitude + (width_deg / 2)
    min_longitude = mid_longitude - (length_deg / 2)
    max_longitude = mid_longitude + (length_deg / 2)

    # convert values to 4 decimal places
    min_latitude = round(min_latitude, 5)
    max_latitude = round(max_latitude, 5)
    min_longitude = round(min_longitude, 5)
    max_longitude = round(max_longitude, 5)


    return min_latitude, min_longitude, max_latitude, max_longitude

# Example usage
# midpoint = (54.1145, -9.1510)
# length = 10  # in kilometers
# width = 10   # in kilometers

# bbox = calculate_bounding_box(midpoint, length, width)
# print("Bounding Box Coordinates:", bbox)
