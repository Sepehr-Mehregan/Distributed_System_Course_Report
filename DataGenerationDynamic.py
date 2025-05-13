# DataGenerationDynamic.py
import random
import pandas as pd

# Function to generate vehicle data with positions, battery, and speed
def generate_vehicle_data(num_vehicles):
    vehicles = []
    for i in range(num_vehicles):
        vehicle_id = f"V{i+1}"
        # Generate random (x,y) positions between 0 and 100
        position = (random.randint(0, 100), random.randint(0, 100))
        battery_level = random.randint(50, 100)  # Battery level between 50% and 100%
        speed = random.randint(3, 10)  # Speed in arbitrary units
        vehicles.append({
            'Vehicle ID': vehicle_id,
            'Vehicle Position (x, y)': position,
            'Battery Level (%)': battery_level,
            'Speed': speed
        })
    return pd.DataFrame(vehicles)

# Function to generate task data (initial set; additional tasks arrive dynamically)
def generate_task_data(num_tasks):
    tasks = []
    for i in range(num_tasks):
        task_id = f"T{i+1}"
        # Generate random (x,y) positions for the task
        position = (random.randint(0, 100), random.randint(0, 100))
        urgency = random.randint(0, 9)  # Initial urgency level (0=low, 9=high)
        duration = random.randint(10, 30)  # Duration in minutes
        tasks.append({
            'Task ID': task_id,
            'Task Position (x, y)': position,
            'Urgency': urgency,
            'Duration (min)': duration
        })
    return pd.DataFrame(tasks)

# Generate sample data
# vehicles_df = generate_vehicle_data(5)  # 5 vehicles
# tasks_df = generate_task_data(5)         # 5 tasks (for initial testing)

# Optionally, save to CSV files:
# vehicles_df.to_csv('vehicles_dataset.csv', index=False)
# tasks_df.to_csv('tasks_dataset.csv', index=False)

# print("Vehicles Data:")
# print(vehicles_df)
# print("\nInitial Tasks Data:")
# print(tasks_df)
