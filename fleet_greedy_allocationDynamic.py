# fleet_greedy_allocationDynamic.py
import numpy as np

def calculate_distance(vehicle_pos, task_pos):
    return np.sqrt((vehicle_pos[0] - task_pos[0])**2 + (vehicle_pos[1] - task_pos[1])**2)

def greedy_basic(vehicles_df, tasks_df):
    """
    Greedy allocation: For each task (sorted by urgency descending), choose the closest free vehicle 
    that has sufficient battery to cover the full engagement (task duration + travel time).
    
    Returns:
      allocations: Dictionary mapping task IDs to vehicle IDs.
      engagement_details: List of per-task metrics dictionaries.
    """
    allocations = {}
    engagement_details = []   # List to store per-task metrics

    # Sort tasks by urgency (High -> Low)
    tasks_df = tasks_df.sort_values('Urgency', ascending=False)

    for _, task in tasks_df.iterrows():
        best_vehicle = None
        best_distance = float('inf')
        best_travel_time = None  # Will store the travel time for the chosen vehicle

        # Evaluate each vehicle for the current task
        for idx, vehicle in vehicles_df.iterrows():
            if vehicle['Busy']:
                continue  # Skip vehicles that are currently busy

            distance = calculate_distance(vehicle['Vehicle Position (x, y)'], task['Task Position (x, y)'])
            travel_time = distance / vehicle['Speed']
            engagement_time = task['Duration (min)'] + travel_time

            # Check if the vehicle has enough battery for the engagement and is closer than previous candidates
            if vehicle['Battery Level (%)'] >= engagement_time and distance < best_distance:
                best_vehicle = vehicle
                best_distance = distance
                best_travel_time = travel_time

        # If a suitable vehicle was found, assign the task and record metrics.
        if best_vehicle is not None and best_travel_time is not None:
            engagement_time = task['Duration (min)'] + best_travel_time

            # Record the allocation
            allocations[task['Task ID']] = best_vehicle['Vehicle ID']
            vehicle_idx = vehicles_df.index[vehicles_df['Vehicle ID'] == best_vehicle['Vehicle ID']][0]

            # Deduct battery (energy consumption is modeled as engagement time)
            vehicles_df.at[vehicle_idx, 'Battery Level (%)'] = float(vehicles_df.at[vehicle_idx, 'Battery Level (%)']) - engagement_time
            ###################################################################################################################
            # vehicles_df.at[vehicle_idx, 'Vehicle Position (x, y)'] = task['Task Position (x, y)']#############################
            ###################################################################################################################
            # Mark vehicle as busy and set its remaining duration to the engagement time
            vehicles_df.at[vehicle_idx, 'Busy'] = True
            vehicles_df.at[vehicle_idx, 'Remaining Duration'] = float(engagement_time)

            # Append per-task engagement details
            engagement_details.append({
                "task_id": task['Task ID'],
                "task_duration": task['Duration (min)'],              # Intrinsic task duration
                "travel_time": best_travel_time,                        # Time to travel to the task location
                "engagement_time": engagement_time,                   # Total time: task_duration + travel_time
                "normalized_engagement_time": engagement_time / task['Duration (min)'],  # Ratio (close to 1 means little travel overhead)
                "energy_consumed": engagement_time                    # In our model, energy consumption equals engagement time
            })

    return allocations, engagement_details


def greedy_positionupdate(vehicles_df, tasks_df):
    """
    Greedy allocation: For each task (sorted by urgency descending), choose the closest free vehicle 
    that has sufficient battery to cover the full engagement (task duration + travel time).
    
    Returns:
      allocations: Dictionary mapping task IDs to vehicle IDs.
      engagement_details: List of per-task metrics dictionaries.
    """
    allocations = {}
    engagement_details = []   # List to store per-task metrics

    # Sort tasks by urgency (High -> Low)
    tasks_df = tasks_df.sort_values('Urgency', ascending=False)

    for _, task in tasks_df.iterrows():
        best_vehicle = None
        best_distance = float('inf')
        best_travel_time = None  # Will store the travel time for the chosen vehicle

        # Evaluate each vehicle for the current task
        for idx, vehicle in vehicles_df.iterrows():
            if vehicle['Busy']:
                continue  # Skip vehicles that are currently busy

            distance = calculate_distance(vehicle['Vehicle Position (x, y)'], task['Task Position (x, y)'])
            travel_time = distance / vehicle['Speed']
            engagement_time = task['Duration (min)'] + travel_time

            # Check if the vehicle has enough battery for the engagement and is closer than previous candidates
            if vehicle['Battery Level (%)'] >= engagement_time and distance < best_distance:
                best_vehicle = vehicle
                best_distance = distance
                best_travel_time = travel_time

        # If a suitable vehicle was found, assign the task and record metrics.
        if best_vehicle is not None and best_travel_time is not None:
            engagement_time = task['Duration (min)'] + best_travel_time

            # Record the allocation
            allocations[task['Task ID']] = best_vehicle['Vehicle ID']
            vehicle_idx = vehicles_df.index[vehicles_df['Vehicle ID'] == best_vehicle['Vehicle ID']][0]

            # Deduct battery (energy consumption is modeled as engagement time)
            vehicles_df.at[vehicle_idx, 'Battery Level (%)'] = float(vehicles_df.at[vehicle_idx, 'Battery Level (%)']) - engagement_time
            ###################################################################################################################
            vehicles_df.at[vehicle_idx, 'Vehicle Position (x, y)'] = task['Task Position (x, y)']#############################
            ###################################################################################################################
            # Mark vehicle as busy and set its remaining duration to the engagement time
            vehicles_df.at[vehicle_idx, 'Busy'] = True
            vehicles_df.at[vehicle_idx, 'Remaining Duration'] = float(engagement_time)

            # Append per-task engagement details
            engagement_details.append({
                "task_id": task['Task ID'],
                "task_duration": task['Duration (min)'],              # Intrinsic task duration
                "travel_time": best_travel_time,                        # Time to travel to the task location
                "engagement_time": engagement_time,                   # Total time: task_duration + travel_time
                "normalized_engagement_time": engagement_time / task['Duration (min)'],  # Ratio (close to 1 means little travel overhead)
                "energy_consumed": engagement_time                    # In our model, energy consumption equals engagement time
            })

    return allocations, engagement_details
