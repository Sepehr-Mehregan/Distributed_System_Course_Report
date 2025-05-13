import numpy as np
import pandas as pd
import random
from matplotlib import pyplot as plt


def calculate_distance(vehicle_pos, task_pos):
    return np.sqrt((vehicle_pos[0] - task_pos[0])**2 + (vehicle_pos[1] - task_pos[1])**2)

def parameter_calculator(vehicle,task):
    """
    Calculates the parameters needed for the auction algorithm from the vehicle and task data.
    Returns:
        vehicle_id: The ID of the vehicle
        task_id: The ID of the task
        engagment_time: The time the vehicle will be engaged in the task (Duration of the task + travel time)
        travel_time: The time it will take for the vehicle to travel to the task
        urgency: The urgency of the task
    """
    distance = calculate_distance (vehicle["Vehicle Position (x, y)"] , task["Task Position (x, y)"] )
    # Calculate the time and energy it will take for the vehicle to travel to the task
    travel_time = distance / vehicle["Speed"]

    # Check if the vehicle is busy
    if vehicle["Busy"]:
        # If the vehicle is busy, add the remaining duration to the engagement time
        return -1,-1,-1,-1,-1,-1
        # engagment_time = travel_time + task["Duration (min)"] + vehicle["Remaining Duration"]
    else:
        engagment_time = travel_time + task["Duration (min)"]
    
    # Check if the vehicle has enough battery for the engagement
    if vehicle["Battery Level (%)"] < engagment_time:
        return -1,-1,-1,-1,-1,-1

    return vehicle["Vehicle ID"],task["Task ID"],engagment_time , travel_time , task["Urgency"],vehicle["Battery Level (%)"]

def create_qvalues(vehicles_df,tasks_df,actions):
    """Create a DataFrame to store the Q-values for each state-action pair.
    rows: MultiIndex with vehicle IDs, task IDs, and actions
    columns: Q-Value
    returns: DataFrame with Q-values initialized to zero
    """
    # Create a MultiIndex from the Cartesian product of the vehicle IDs, task IDs, and actions
    index = pd.MultiIndex.from_product([vehicles_df["Vehicle ID"], tasks_df["Task ID"], actions], names=["Vehicle ID", "Task ID", "Action"])

    # Initialize the Q-table with zeros values
    q_values_df = pd.DataFrame(0.0, index=index, columns=["Q-Value"])
    # sort the dataframe by the index for decreasing the time complexity
    q_values_df.sort_index(inplace=True)
    return q_values_df

def get_env(vehicles_df,tasks_df):
    """
    Create a DataFrame to store the environment state for each vehicle-task pair.
    columns: Vehicle ID, Task ID, Engagement Time, Urgency, Travel Time
    """
    env = pd.DataFrame(columns=["Vehicle ID" , "Task ID" , "Engagement Time" , "Urgency" , "travel_time","Battery"])

    for v_id, vehicle in vehicles_df.iterrows():
        
        # in thest implementation we are not considering the case of the vehicle being busy,
        # as it will increase the complexity of the states from only one timestep into  mutli-timesteps
        if vehicle["Busy"]:
            continue
        
        for t_id, task in tasks_df.iterrows():

            vehicle_id , task_id ,engagment_time , travel_time , urgency,battery = parameter_calculator(vehicle,task)

            # if the vehicle does not have enough battery for the engagement, skip the task as it is not a valid state
            if engagment_time == -1:
                continue
            
            env.loc[len(env)] = [vehicle_id , task_id, engagment_time , urgency , travel_time,battery]
    # if there are no valid states in the current timestep, return None
    if env.empty:
        return None
    
    return env

def get_reward(vehicle_ID,task_ID,act,env):
    """
    Get the reward for the vehicle-task pair
    """
    battery = env[(env["Vehicle ID"] == vehicle_ID) & (env["Task ID"] == task_ID)]["Battery"].values[0]
    engagment_time = env[(env["Vehicle ID"] == vehicle_ID) & (env["Task ID"] == task_ID)]["Engagement Time"].values[0]
    
    # act == 0 --> Bid
    # act == 1 --> No Bid
    if battery>engagment_time and act == 0:
        # reward for bidding
        return 1 
    elif battery>engagment_time and act == 1:
        # reward for not bidding
        return -1 
    elif battery<engagment_time and act == 0:
        # penalty for bidding because the vehicle does not have enough battery
        return -10 
    else:
        # no reward for not bidding 
        return 0 

def get_action(env,q_values,epsilon):
    """
    Get the action for the vehicle in the current timestep
    The action consists of two part
    1- selecting the vehicle-task pair
    2- selecting the Bid for the selected vehicle-task pair

    returns:
        vehicle_ID: The ID of the vehicle
        task_ID: The ID of the task
        bid_flag: 0 for bid , 1 for no_bid
    """
    # --- select the vehicle-task pair ---
    if random.uniform(0,1) < epsilon:
        pair = env.sort_values(by=["Engagement Time" , "Urgency"] , ascending=[True, False]).iloc[0]
    else:
        pair =env.sample(frac=1).iloc[0]

    vehicle_ID = pair["Vehicle ID"]
    task_ID = pair["Task ID"]
    
    # --- select the bid for the selected vehicle-task pair ---
    if random.uniform(0,1) < epsilon:
        bid_flag= np.argmax(q_values.loc[(vehicle_ID, task_ID)])
    else:
        bid_flag= random.choice([0,1])

    return vehicle_ID,task_ID,bid_flag

def env_update(env,vehicle_ID,task_ID):
    """
    Update the environment after a task is assigned to a vehicle
    by removing the vehicle-task pair from the environment
    """
    env = env[(env["Vehicle ID"] != vehicle_ID) & (env["Task ID"] != task_ID)]
    return env

def QL_without_charger(vehicles,tasks,episodes=100):
    """
    Q-Learning algorithm: For each vehicle, calculate the engagement time and urgency for each task.
    The vehicle will bid for the task with the highest Q-value.
    The task will be assigned to the vehicle with the best bid.
    Returns:
        allocations: Dictionary mapping task IDs to vehicle IDs.
        engagement_details: List of per-task metrics dictionaries
    """
    epsilon = 0.3         # the percentage of time when we should take the best action (instead of a random action)
    discount_factor = 0.95 # discount factor for future rewards
    learning_rate = 0.05   # the rate at which the AI agent should learn
    allocations={}
    engagement_details=[]
    
    # --- Initialize the Q-values, environment  ---
    vehicles_df = vehicles.copy()
    tasks_df = tasks.copy()

    env = get_env(vehicles_df,tasks_df)
    
    # action consists of  vehicle-task pair and the bid (vehicle_ID,task_ID,bid)
    actions= ['bid', 'no_bid']
    
    q_values = create_qvalues(vehicles_df,tasks_df,actions)
    # rewards=env_reward(vehicles_df,tasks_df,actions)

    if env is None:
        return allocations, engagement_details
    
    # --- Q-Learning loop ---
    for episode in range(episodes):
        # reset the environment for each episode
        env = get_env(vehicles_df,tasks_df)

        # if there are no valid states in the current timestep, skip the episode
        if env is None:
            return allocations, engagement_details

        # action 
        vehicle_ID,task_ID,act = get_action(env,q_values,0) 

        # loop until the environment is empty
        # env is empty when all the vehicle-task pairs are assigned
        while not env.empty :
            
            # store the previous vehicle-task pair and the bid             
            old_vehicle_ID,old_task_ID,oldact = vehicle_ID,task_ID,act
            # action
            vehicle_ID,task_ID,act = get_action(env,q_values,epsilon)
            # reward
            reward = get_reward(vehicle_ID,task_ID,act,env)
            # get the old Q-value
            old_q_value = q_values.loc[(old_vehicle_ID, old_task_ID, actions[oldact])]
            # update current Q-value 
            temporal_difference = reward + discount_factor * np.max(q_values.loc[(vehicle_ID, task_ID)]) - old_q_value
            new_q_value = old_q_value + (learning_rate * temporal_difference)
            q_values.loc[(old_vehicle_ID, old_task_ID, actions[oldact])] = new_q_value
            # update environment
            env=env_update(env,old_vehicle_ID,old_task_ID)
    
    # get the environment after the Q-learning loop
    # to allocate tasks to the vehicles based on the Q-values
    env = get_env(vehicles_df,tasks_df)
    # copy the Q-values to a new dataframe to keep the original Q-values
    qval= q_values.copy()
    for t_id, task in tasks_df.iterrows():
        
        # get the bids for the task
        bids_per_task = qval.loc[(slice(None), task["Task ID"],"bid")].sort_values(by="Q-Value", ascending=False)
        
        # if all bids are zero, skip the allocation of the task
        if bids_per_task["Q-Value"].max() == 0:
            continue
        # if there are no bids for the task, skip the allocation of the
        # task in the current timestep
        if bids_per_task.empty:
                continue
         
        # get the engagement time and travel time for the task
        engagement_time=env[(env["Vehicle ID"] == bids_per_task.index[0]) & (env["Task ID"] == task["Task ID"])]["Engagement Time"].values[0]
        travel_time=env[(env["Vehicle ID"] == bids_per_task.index[0]) & (env["Task ID"] == task["Task ID"])]["travel_time"].values[0]
        
        # --- Allocate the task to the vehicle with the best bid ---
        vehicle_idx = vehicles.index[vehicles['Vehicle ID'] == bids_per_task.index[0]].tolist()[0]
        
        if vehicles.at[vehicle_idx, 'Battery Level (%)'] < engagement_time:
            continue
        if vehicles.at[vehicle_idx, 'Busy']: 
            continue
        vehicles.at[vehicle_idx, 'Battery Level (%)'] = float(vehicles.at[vehicle_idx, 'Battery Level (%)']) - engagement_time
        vehicles.at[vehicle_idx, 'Busy'] = True
        vehicles.at[vehicle_idx, 'Remaining Duration'] = float(engagement_time)
        vehicles.at[vehicle_idx, 'Vehicle Position (x, y)'] = task['Task Position (x, y)']
        
        # update the Q-values and the environment after the allocation and remove the vehicle-task pair from the environment
        qval.drop(qval.iloc[qval.index.get_level_values('Vehicle ID') == bids_per_task.index[0][0]].index , inplace = True )
        qval.drop(qval.iloc[qval.index.get_level_values('Task ID') == task["Task ID"]].index , inplace = True )
        
        allocations[task["Task ID"]] = bids_per_task.index[0]
        engagement_details.append({
            "task_id": task['Task ID'],
            "task_duration": task['Duration (min)'],              # Intrinsic task duration
            "travel_time": travel_time,                        # Time to travel to the task location
            "engagement_time": engagement_time,                   # Total time: task_duration + travel_time
            "normalized_engagement_time": engagement_time / task['Duration (min)'],  # Ratio (close to 1 means little travel overhead)
            "energy_consumed": engagement_time                    # In our model, energy consumption equals engagement time
        })   
    return allocations, engagement_details
