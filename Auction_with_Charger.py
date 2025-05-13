import pandas as pd
import numpy as np
import random
import matplotlib.pyplot as plt
import DataGenerationDynamic as dgd 

def calculate_distance(vehicle_pos, task_pos):
    return np.sqrt((vehicle_pos[0] - task_pos[0])**2 + (vehicle_pos[1] - task_pos[1])**2)

def parameter_calculator(vehicle,task,Charger_df):
    """
    Calculates the parameters needed for the auction algorithm from the vehicle and task data.
    Returns:
        vehicle_id: The ID of the vehicle
        task_id: The ID of the task
        engagment_time: The time the vehicle will be engaged in the task (Duration of the task + travel time)
        duration: The duration of the task
        travel_time: The time it will take for the vehicle to travel to the task
        urgency: The urgency of the task
        
    """
    distance = calculate_distance (vehicle["Vehicle Position (x, y)"] , task["Task Position (x, y)"] )
    # Calculate the time and energy it will take for the vehicle to travel to the task
    travel_time = distance / vehicle["Speed"]
    ch_v, ch_t = nearest_charger(vehicle, task["Task Position (x, y)"], Charger_df)
    # Check if the vehicle is busy
    ch_v_travel = ch_v[0] / vehicle["Speed"]
    ch_t_travel = ch_t[0] / vehicle["Speed"]
   
    if vehicle["Busy"]:
        # If the vehicle is busy, add the remaining duration to the engagement time
        engagment_time = travel_time + task["Duration (min)"] + vehicle["Remaining Duration"]+ ch_t_travel
    else:
        engagment_time = travel_time + task["Duration (min)"] + ch_t_travel
    
    # Check if the vehicle has enough battery for the engagement
    if vehicle["Battery Level (%)"] < engagment_time:
        return -1,-1,-1,-1,-1,-1

    return vehicle["Vehicle ID"],task["Task ID"],engagment_time,task["Duration (min)"] , travel_time , task["Urgency"]

def nearest_charger(vehicle_df,task_pos ,Charger_df):
    # TODO 
    """calculate the nearest charger to the vehicle and nearest charger from task in hand"""

    vehicle_pos = vehicle_df["Vehicle Position (x, y)"]

    nearest_to_vehicle = np.inf
    nearest_to_task = np.inf
    
    for _, charger in Charger_df.iterrows():
        distance_to_vehicle = calculate_distance(vehicle_pos , charger["Charger Position (x, y)"])
        dictance_to_task = calculate_distance(task_pos , charger["Charger Position (x, y)"])
        if charger["Busy"]:
            if charger["Available After"] < distance_to_vehicle/vehicle_df["Speed"]:
                nearest_to_vehicle = charger["Available After"]
            else:
                nearest_to_vehicle = -1
            if charger["Available After"] < dictance_to_task/vehicle_df["Speed"]:
                nearest_to_task = charger["Available After"]
            else:
                nearest_to_task = -1

        if distance_to_vehicle < nearest_to_vehicle:
            nearest_to_vehicle = distance_to_vehicle
        if dictance_to_task < nearest_to_task:
            nearest_to_task = dictance_to_task
    return((nearest_to_vehicle,Charger_df["Charger ID"]) , (nearest_to_task,Charger_df["Charger ID"]))

def auction_with_charger(vehicles_df, tasks_df,Charger_df):
    """
    Auction algorithm: For each vehicle, calculate the engagement time and urgency for each task.
    The vehicle will bid for the task with the lowest engagement time and highest urgency.
    The task will be assigned to the vehicle with the best bid.
    if the highest bid is for a busy vehicle, the task will not be assigned to any vehicle in current timestep.
    Returns:
        allocations: Dictionary mapping task IDs to vehicle IDs.
        engagement_details: List of per-task metrics dictionaries
    """
    allocations={}
    engagement_details=[]
    
    # Create a dataframe to store the bids
    bids= pd.DataFrame(columns=["Vehicle ID" , "Task ID" , "Engagement Time","Duration" , "Urgency" , "travel_time"])
    
    for _, vehicle in vehicles_df.iterrows():
        for _, task in tasks_df.iterrows():
            
            # get the parameters needed for the auction algorithm
            vehicle_id , task_id ,engagment_time ,duration, travel_time , urgency = parameter_calculator(vehicle,task,Charger_df)
            
            # if the vehicle does not have enough battery for the engagement, skip the task
            
            
            # Add the bid to the dataframe
            bids.loc[len(bids)] = [vehicle_id , task_id , engagment_time ,duration, urgency , travel_time]
        if bids.loc[bids["Vehicle ID"] == vehicle["Vehicle ID"]]["Engagement Time"].all()==-1:
            ch_v,_ = nearest_charger(vehicle, task["Task Position (x, y)"], Charger_df)
            ch_v_travel = ch_v[0] / vehicle["Speed"]
            if vehicle["Battery Level (%)"] > ch_v_travel:
                vehicle["Charging"] = True
                vehicle['Remaining Duration'] = ch_v_travel
                vehicle["Vehicle Position (x, y)"] = Charger_df.loc[Charger_df["Charger ID"] == ch_v[1], "Charger Position (x, y)"]
                Charger_df.loc[Charger_df["Charger ID"] == ch_v[1], "Busy"] = True
                Charger_df.loc[Charger_df["Charger ID"] == ch_v[1], "Available After"] = 100 - vehicle["Battery Level (%)"] - ch_v_travel

    # if there are no bids in current timestep, return empty allocations and engagement details             
    if bids.empty:
        return {}, []
    # loop for assigning the tasks to the vehicles with the highest bid
    # the loop will continue until all vehicles are busy or there are no bids left
    while not vehicles_df["Busy"].all() and not bids.empty:
        # Sort the bids by engagement time and urgency
        bids_per_task = bids.sort_values(by=["Engagement Time","Urgency"] , ascending=[True,False])
        
        # get the highest bid for the task
        best_bid=bids_per_task.iloc[0]
        
        # Drop the task and the vehicle that is selected for the best bid and update update the bid list without them
        bids.drop(bids[bids["Task ID"] == best_bid["Task ID"]].index , inplace = True)
        bids.drop(bids[bids["Vehicle ID"] == best_bid["Vehicle ID"]].index , inplace = True)
        
        # if the highest bid for a task is from a busy vehicle,
        # skip allocating the task in current timestep
        if vehicles_df[vehicles_df["Vehicle ID"] == best_bid["Vehicle ID"]]["Busy"].empty:
            continue
        if  vehicles_df[vehicles_df["Vehicle ID"] == best_bid["Vehicle ID"]]["Busy"].values[0]:
            continue
        
        # --- Allocating task and updating the vehicle data ---
        # NOTE : in this strategy the vehicle position from the first moment of assigning the task,
        # will be considered as the task position.
        # this is so the engagement time can be calculated correctly.

        engagement_time = float(best_bid["Engagement Time"])
        allocations[task["Task ID"]] = best_bid["Vehicle ID"]
        vehicle_idx = vehicles_df.index[vehicles_df['Vehicle ID'] == best_bid['Vehicle ID']].tolist()[0]
        vehicles_df.at[vehicle_idx, 'Battery Level (%)'] = float(vehicles_df.at[vehicle_idx, 'Battery Level (%)']) - engagement_time
        vehicles_df.at[vehicle_idx, 'Busy'] = True
        vehicles_df.at[vehicle_idx, 'Remaining Duration'] = float(engagement_time)
        vehicles_df.at[vehicle_idx, 'Vehicle Position (x, y)'] = task['Task Position (x, y)']

        # Append per-task engagement details
        engagement_details.append({
            "task_id": task['Task ID'],
            "task_duration": task['Duration (min)'],              # Intrinsic task duration
            "travel_time": best_bid["travel_time"],               # Time to travel to the task location
            "engagement_time": engagement_time,                   # Total time: task_duration + travel_time
            "normalized_engagement_time": engagement_time / task['Duration (min)'],  # Ratio (close to 1 means little travel overhead)
            "energy_consumed": engagement_time                    # In our model, energy consumption equals engagement time
        })    
    return allocations, engagement_details