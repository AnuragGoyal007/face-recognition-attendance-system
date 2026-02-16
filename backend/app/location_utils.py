import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance in KM using Haversine formula
    """

    R = 6371  # Earth radius in KM

    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(d_lon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def is_within_radius(student_lat, student_lon, class_lat, class_lon, allowed_km=0.1):

    distance = calculate_distance(
        student_lat,
        student_lon,
        class_lat,
        class_lon
    )

    return distance <= allowed_km