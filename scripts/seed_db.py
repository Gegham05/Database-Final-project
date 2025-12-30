import requests
import random
import string
from datetime import datetime, timedelta

# --- Configuration ---
BASE_URL = "http://127.0.0.1:8000"
NUM_CARS = 50
NUM_MECHANICS = 10
NUM_ORDERS = 200

# --- Simple Data Generators ---

def generate_vin():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=17))

def generate_name():
    first_names = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    return f"{random.choice(first_names)} {random.choice(last_names)}"

def generate_vehicle_make():
    return random.choice(["Toyota", "Ford", "Honda", "Chevrolet", "Nissan", "Jeep", "Hyundai", "Kia", "Subaru", "BMW"])

_used_employee_ids = set()
def generate_employee_id():
    while True:
        emp_id = f"EMP-{''.join(random.choices(string.digits, k=5))}"
        if emp_id not in _used_employee_ids:
            _used_employee_ids.add(emp_id)
            return emp_id

def generate_random_date(start_date, end_date):
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    return random_date

def generate_work_details(work_type):
    if work_type == "Oil Change":
        return {"description": "Standard oil and filter change.", "parts": ["Oil Filter", "Synthetic Oil 5L"]}
    elif work_type == "Brake Repair":
        return {"description": "Replaced front brake pads and rotors.", "parts": ["Front Brake Pads", "Front Rotors", "Brake Fluid"]}
    elif work_type == "Tire Rotation":
        return {"description": "Rotated tires and checked pressure.", "parts": []}
    else:
        return {"description": "Complex diagnostic and repair.", "parts": ["Sensor", "Wiring Harness", "Various clips"]}

# --- Seeding Functions ---

def create_cars():
    cars = []
    for _ in range(NUM_CARS):
        car_data = {
            "make": generate_vehicle_make(),
            "year": random.randint(2000, 2023),
            "vin": generate_vin(),
            "owner_name": generate_name()
        }
        try:
            response = requests.post(f"{BASE_URL}/cars/", json=car_data)
            response.raise_for_status()
            cars.append(response.json())
            print(f"Created car: {car_data['make']} {car_data['vin']}")
        except requests.exceptions.RequestException as e:
            print(f"Error creating car {car_data['vin']}: {e}")
            if response:
                print(f"Response content: {response.content}")
    return cars

def create_mechanics():
    mechanics = []
    for _ in range(NUM_MECHANICS):
        mechanic_data = {
            "full_name": generate_name(),
            "experience": random.randint(1, 30),
            "rank": random.choice(["Apprentice", "Technician", "Senior Technician", "Master Technician"]),
            "employee_id": generate_employee_id()
        }
        try:
            response = requests.post(f"{BASE_URL}/mechanics/", json=mechanic_data)
            response.raise_for_status()
            mechanics.append(response.json())
            print(f"Created mechanic: {mechanic_data['full_name']}")
        except requests.exceptions.RequestException as e:
            print(f"Error creating mechanic {mechanic_data['employee_id']}: {e}")
            if response:
                print(f"Response content: {response.content}")
    return mechanics

def create_orders(cars, mechanics):
    if not cars or not mechanics:
        print("No cars or mechanics to create orders for. Aborting.")
        return

    orders = []
    today = datetime.now()
    two_years_ago = today - timedelta(days=365 * 2)

    for _ in range(NUM_ORDERS):
        start_date = generate_random_date(two_years_ago, today)
        planned_end_date = start_date + timedelta(days=random.randint(1, 14))
        
        is_completed = random.random() < 0.8
        actual_end_date = planned_end_date + timedelta(days=random.randint(-2, 5)) if is_completed else None
        
        work_type = random.choice(["Oil Change", "Brake Repair", "Tire Rotation", "Engine Diagnostics", "Transmission Repair"])

        order_data = {
            "issue_date": start_date.isoformat().split('T')[0],
            "cost": str(round(random.uniform(50.0, 2000.0), 2)),
            "work_type": work_type,
            "planned_completion_date": planned_end_date.isoformat().split('T')[0],
            "actual_completion_date": actual_end_date.isoformat().split('T')[0] if actual_end_date else None,
            "car_id": random.choice(cars)['id'],
            "mechanic_id": random.choice(mechanics)['id'],
            "work_details": generate_work_details(work_type)
        }
        try:
            response = requests.post(f"{BASE_URL}/orders/", json=order_data)
            response.raise_for_status()
            orders.append(response.json())
            print(f"Created order {response.json()['id']} for car {order_data['car_id']}")
        except requests.exceptions.RequestException as e:
            print(f"Error creating order: {e}")
            if response:
                print(f"Response content: {response.content}")
            
    return orders

def main():
    print("--- Starting Database Seeding ---")
    
    try:
        requests.get(f"{BASE_URL}/docs")
    except requests.exceptions.ConnectionError:
        print(f"Error: API at {BASE_URL} is not reachable. Please start the FastAPI server first.")
        print("Run: uvicorn app.main:app --reload")
        return

    print(f"\nCreating {NUM_CARS} cars...")
    cars = create_cars()
    
    print(f"\nCreating {NUM_MECHANICS} mechanics...")
    mechanics = create_mechanics()
    
    print(f"\nCreating {NUM_ORDERS} orders...")
    create_orders(cars, mechanics)
    
    print("\n--- Database Seeding Complete ---")

if __name__ == "__main__":
    main()
