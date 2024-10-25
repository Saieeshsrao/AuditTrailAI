import pandas as pd
import random
from datetime import datetime, timedelta

def create_correct_sequence():
    """Create a correct sequence for a coating batch process"""
    
    sequence = [
        # Standard batch sequence template
        {"Activity Description": "User logged into the system", "User": "operator1"},
        {"Activity Description": "Loaded recipe for batch #{batch_num}", "User": "operator1"},
        {"Activity Description": "Initiated pre-operation equipment check", "User": "operator1"},
        {"Activity Description": "Verified calibration of scales", "User": "operator1"},
        {"Activity Description": "Started coating process for batch #{batch_num}", "User": "operator1"},
        {"Activity Description": "Adjusted inlet air temperature from {temp1}°C to {temp2}°C", "User": "operator1"},
        {"Activity Description": "Adjusted spray rate from {spray1} mL/min to {spray2} mL/min", "User": "operator1"},
        {"Activity Description": "Performed intermediate quality check", "User": "operator1"},
        {"Activity Description": "Changed coating solution to type {solution}", "User": "operator1"},
        {"Activity Description": "Adjusted drum speed from {rpm1} RPM to {rpm2} RPM", "User": "operator1"},
        {"Activity Description": "Performed final quality check", "User": "operator1"},
        {"Activity Description": "Stopped coating process for batch #{batch_num}", "User": "operator1"},
        {"Activity Description": "Logged out of the system", "User": "operator1"}
    ]
    
    batches = []
    start_time = datetime(2024, 8, 27, 8, 0, 0)
    solutions = ['A', 'B', 'C']
    
    for batch_num in range(1, 7):
        batch_sequence = []
        current_time = start_time + timedelta(hours=2*(batch_num-1))
        
        for idx, step in enumerate(sequence):
            step_dict = step.copy()
            
            desc = step_dict["Activity Description"]
            desc = desc.replace("{batch_num}", str(batch_num).zfill(3))
            desc = desc.replace("{temp1}", str(145 + batch_num))
            desc = desc.replace("{temp2}", str(150 + batch_num))
            desc = desc.replace("{spray1}", str(8 + batch_num))
            desc = desc.replace("{spray2}", str(10 + batch_num))
            desc = desc.replace("{rpm1}", str(12 + batch_num))
            desc = desc.replace("{rpm2}", str(15 + batch_num))
            desc = desc.replace("{solution}", solutions[batch_num % 3])
            
            step_dict["Activity Description"] = desc
            step_dict["Date"] = current_time.strftime("%Y-%m-%d")
            step_dict["Time"] = current_time.strftime("%H:%M:%S")
            step_dict["Reason for change"] = "Not Available"
            step_dict["Anomaly"] = 0
            
            batch_sequence.append(step_dict)
            current_time += timedelta(minutes=5)
        
        batches.extend(batch_sequence)
    
    return pd.DataFrame(batches)

def create_anomalous_sequence(correct_df, num_anomalies=3):
    """Create an anomalous sequence by introducing various types of anomalies"""
    
    df = correct_df.copy()
    
    def swap_steps(df, idx1, idx2):
        """Swap two steps in the sequence"""
        df.iloc[idx1:idx2+1] = df.iloc[idx1:idx2+1][::-1].values
        df.iloc[idx1:idx2+1, df.columns.get_loc("Anomaly")] = 1
        return df
    
    def modify_parameter(df, idx):
        """Modify a parameter to an anomalous value"""
        desc = df.iloc[idx]["Activity Description"]
        if "temperature" in desc:
            new_value = random.randint(160, 180)
            desc = desc.split("to")[0] + f"to {new_value}°C"
        elif "RPM" in desc:
            new_value = random.randint(25, 30)
            desc = desc.split("to")[0] + f"to {new_value} RPM"
        elif "mL/min" in desc:
            new_value = random.randint(20, 25)
            desc = desc.split("to")[0] + f"to {new_value} mL/min"
        
        df.iloc[idx, df.columns.get_loc("Activity Description")] = desc
        df.iloc[idx, df.columns.get_loc("Anomaly")] = 1
        return df
    
    def insert_unexpected_action(df, idx):
        """Insert an unexpected action"""
        unexpected_actions = [
            "Attempted unauthorized recipe modification",
            "Bypassed safety interlock",
            "Changed batch parameters without approval",
            "Disabled temperature monitoring",
            "Overrode system warnings"
        ]
        
        new_row = df.iloc[idx].copy()
        new_row["Activity Description"] = random.choice(unexpected_actions)
        new_row["Anomaly"] = 1
        
        df = pd.concat([df.iloc[:idx], 
                       pd.DataFrame([new_row]), 
                       df.iloc[idx:]]).reset_index(drop=True)
        return df
    
    def skip_step(df, idx):
        """Skip a critical step"""
        df = df.drop(idx).reset_index(drop=True)
        if idx < len(df):
            df.iloc[idx, df.columns.get_loc("Anomaly")] = 1
        return df
    
    # List of possible anomaly functions
    anomaly_functions = [
        (swap_steps, 2),  # Function and number of indices needed
        (modify_parameter, 1),
        (insert_unexpected_action, 1),
        (skip_step, 1)
    ]
    
    # Apply random anomalies
    for _ in range(num_anomalies):
        func, num_indices = random.choice(anomaly_functions)
        
        if num_indices == 1:
            idx = random.randint(1, len(df)-2)
            df = func(df, idx)
        else:  # For swap_steps
            idx1 = random.randint(1, len(df)-3)
            df = func(df, idx1, idx1+1)
    
    # Fix timestamps
    start_time = datetime.strptime(df.iloc[0]["Date"] + " " + df.iloc[0]["Time"], 
                                 "%Y-%m-%d %H:%M:%S")
    for i in range(len(df)):
        current_time = start_time + timedelta(minutes=5*i)
        df.iloc[i, df.columns.get_loc("Date")] = current_time.strftime("%Y-%m-%d")
        df.iloc[i, df.columns.get_loc("Time")] = current_time.strftime("%H:%M:%S")
    
    return df

# Generate sequences
correct_df = create_correct_sequence()
anomalous_sequences = []

# Generate 5 different anomalous sequences
for i in range(5):
    anom_df = create_anomalous_sequence(correct_df, num_anomalies=3)
    anomalous_sequences.append(anom_df)

# Save sequences to CSV
correct_df.to_csv("correct_sequence.csv", index=False)
for i, anom_df in enumerate(anomalous_sequences, 1):
    anom_df.to_csv(f"anomalous_sequence_{i}.csv", index=False)

# Print sample of correct and anomalous sequences
print("\nSample of correct sequence:")
print(correct_df.head())
print("\nSample of anomalous sequence with anomalies marked:")
print(anomalous_sequences[0].head())