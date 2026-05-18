from datetime import datetime
import random
import math

locations = {
    "Kukatpally": (17.4948, 78.3996),
    "Miyapur": (17.4933, 78.3915),
    "Ameerpet": (17.4375, 78.4483),
    "Begumpet": (17.4447, 78.4664),
    "Secunderabad": (17.4399, 78.4983),
    "Hitech City": (17.4435, 78.3772),
    "Gachibowli": (17.4401, 78.3489),
    "Madhapur": (17.4486, 78.3908),
    "Banjara Hills": (17.4156, 78.4347),
    "Dilsukhnagar": (17.3687, 78.5247)
}

ngos = [
    {"name": "Helping Hands NGO", "area": "Miyapur", "location": locations["Miyapur"]},
    {"name": "Food For All NGO", "area": "Ameerpet", "location": locations["Ameerpet"]},
    {"name": "Care Foundation", "area": "Secunderabad", "location": locations["Secunderabad"]},
    {"name": "Hope Shelter", "area": "Gachibowli", "location": locations["Gachibowli"]},
    {"name": "Meals Mission", "area": "Dilsukhnagar", "location": locations["Dilsukhnagar"]}
]

donations = []


def calculate_distance(loc1, loc2):
    return math.sqrt(
        (loc1[0] - loc2[0]) ** 2 +
        (loc1[1] - loc2[1]) ** 2
    )


def generate_otp():
    return random.randint(1000, 9999)


def find_nearest_ngo(restaurant_location):
    nearest_ngo = None
    min_distance = float("inf")

    for ngo in ngos:
        distance = calculate_distance(restaurant_location, ngo["location"])

        if distance < min_distance:
            min_distance = distance
            nearest_ngo = ngo

    return nearest_ngo, min_distance


def create_donation(restaurant_name, phone, food_name, quantity, area, expiry_time):
    if expiry_time <= datetime.now():
        return None, "Food is expired. Donation rejected."

    restaurant_location = locations[area]
    nearest_ngo, distance = find_nearest_ngo(restaurant_location)

    otp = generate_otp()

    donation = {
        "restaurant": restaurant_name,
        "phone": phone,
        "food": food_name,
        "quantity": quantity,
        "area": area,
        "location": restaurant_location,
        "expiry": expiry_time,
        "ngo": nearest_ngo["name"],
        "ngo_area": nearest_ngo["area"],
        "distance": round(distance * 100, 2),
        "otp": otp,
        "status": "Pending",
        "created_at": datetime.now()
    }

    donations.append(donation)
    return donation, "Donation request created successfully."


def get_donations():
    return donations


def verify_otp(index, entered_otp):
    if index < 0 or index >= len(donations):
        return False

    if entered_otp == donations[index]["otp"]:
        donations[index]["status"] = "Delivered"
        return True

    return False


def predict_surplus():
    if len(donations) == 0:
        return 0

    total_quantity = sum(donation["quantity"] for donation in donations)
    average = total_quantity / len(donations)

    return round(average)


def get_locations():
    return locations
