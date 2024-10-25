import pandas as pd
from datetime import datetime, timedelta
import random

class AuditLogGenerator:
    def __init__(self):
        self.users = ['user123', 'user456', 'user789']
        self.base_sequence = [
            'User logged into the system',
            'Loaded recipe for batch #{}',
            'Initiated pre-operation equipment check',
            'Verified calibration of scales',
            'Started coating process for batch #{}'
        ]
        
        self.normal_adjustments = [
            ('inlet air temperature', 145, 155),
            ('spray rate', 8, 15),
            ('drum speed', 12, 19),
            ('exhaust air temperature', 42, 47),
            ('atomization air pressure', 1.8, 2.2)
        ]
        
        self.alarms = [
            'Low spray pressure',
            'High exhaust temperature',
            'Low atomization pressure',
            'High drum speed',
            'Low exhaust temperature',
            'High spray rate'
        ]
        
        self.coating_solutions = ['A', 'B', 'C']

    def generate_time_string(self, time_obj):
        """Generate time string in standard format"""
        return time_obj.strftime('%H:%M:%S')

    def generate_normal_sequence(self, date, start_time, user, batch_num):
        current_time = start_time
        sequence = []
        
        # Add base sequence
        for activity in self.base_sequence:
            if '{}' in activity:
                activity = activity.format(f"{batch_num:03d}")
            sequence.append([
                date.strftime('%Y-%m-%d'),
                self.generate_time_string(current_time),
                user,
                activity,
                'Not Available',
                '0'
            ])
            current_time += timedelta(minutes=random.randint(5, 10))
            
        # Add normal adjustments
        for _ in range(random.randint(3, 6)):
            param, min_val, max_val = random.choice(self.normal_adjustments)
            val1 = round(random.uniform(min_val, max_val), 1)
            val2 = round(val1 + random.uniform(-2, 2), 1)
            activity = f"Adjusted {param} from {val1} to {val2}"
            
            sequence.append([
                date.strftime('%Y-%m-%d'),
                self.generate_time_string(current_time),
                user,
                activity,
                'Not Available',
                '0'
            ])
            current_time += timedelta(minutes=random.randint(5, 10))
            
        # Add batch end
        sequence.append([
            date.strftime('%Y-%m-%d'),
            self.generate_time_string(current_time),
            user,
            f'Stopped coating process for batch #{batch_num:03d}',
            'Not Available',
            '0'
        ])
        current_time += timedelta(minutes=5)
        
        # Add logout
        sequence.append([
            date.strftime('%Y-%m-%d'),
            self.generate_time_string(current_time),
            user,
            'Logged out of the system',
            'Not Available',
            '0'
        ])
        
        return sequence

    def generate_anomalous_sequence(self, date, start_time, user, batch_num):
        sequence = []
        current_time = start_time
        
        # Choose anomaly type (removed time_format from options)
        anomaly_type = random.choice([
            'alarm_sequence',
            'batch_deletion',
            'solution_change',
            'logout_sequence'
        ])
        
        if anomaly_type == 'alarm_sequence':
            # Generate sequence with alarm events
            sequence.extend(self.generate_normal_sequence(date, start_time, user, batch_num)[:4])
            
            # Insert alarm sequence
            alarm = random.choice(self.alarms)
            sequence.append([
                date.strftime('%Y-%m-%d'),
                self.generate_time_string(current_time),
                user,
                f'Resolved alarm: {alarm}',
                'Not Available',
                '1'
            ])
            current_time += timedelta(minutes=1)
            
            sequence.append([
                date.strftime('%Y-%m-%d'),
                self.generate_time_string(current_time),
                user,
                f'Acknowledged alarm: {alarm}',
                'Not Available',
                '1'
            ])
            
            # Continue with normal sequence
            sequence.extend(self.generate_normal_sequence(date, current_time + timedelta(minutes=5), user, batch_num)[4:])
            
        elif anomaly_type == 'batch_deletion':
            # Generate partial sequence then delete batch
            sequence.extend(self.generate_normal_sequence(date, start_time, user, batch_num)[:6])
            
            sequence.append([
                date.strftime('%Y-%m-%d'),
                self.generate_time_string(current_time),
                random.choice(self.users),  # Maybe different user
                f'Deleted batch#{batch_num:03d}',
                'Not Available',
                '1'
            ])
            
        elif anomaly_type == 'solution_change':
            # Generate sequence with unusual solution changes
            sequence.extend(self.generate_normal_sequence(date, start_time, user, batch_num)[:5])
            
            # Add multiple solution changes
            for _ in range(2):
                sequence.append([
                    date.strftime('%Y-%m-%d'),
                    self.generate_time_string(current_time),
                    user,
                    f'Changed coating solution to type {random.choice(self.coating_solutions)}',
                    'Not Available',
                    '1'
                ])
                current_time += timedelta(minutes=5)
                
            sequence.extend(self.generate_normal_sequence(date, current_time, user, batch_num)[5:])
            
        elif anomaly_type == 'logout_sequence':
            # Generate sequence with logout before process end
            sequence.extend(self.generate_normal_sequence(date, start_time, user, batch_num)[:-2])
            
            # Add logout before process end
            sequence.append([
                date.strftime('%Y-%m-%d'),
                self.generate_time_string(current_time),
                user,
                'Logged out of the system',
                'Not Available',
                '1'
            ])
            current_time += timedelta(minutes=5)
            
            sequence.append([
                date.strftime('%Y-%m-%d'),
                self.generate_time_string(current_time),
                user,
                f'Stopped coating process for batch #{batch_num:03d}',
                'Not Available',
                '1'
            ])
            
        return sequence

def generate_dataset(num_sequences=50, anomaly_probability=0.3):  # Changed default to 0.3
    generator = AuditLogGenerator()
    all_sequences = []
    current_date = datetime.strptime('2024-08-27', '%Y-%m-%d')
    
    for seq in range(num_sequences):
        start_time = datetime.strptime('08:00:00', '%H:%M:%S')
        user = random.choice(generator.users)
        
        if random.random() < anomaly_probability:
            sequence = generator.generate_anomalous_sequence(current_date, start_time, user, seq+1)
        else:
            sequence = generator.generate_normal_sequence(current_date, start_time, user, seq+1)
            
        all_sequences.extend(sequence)
        current_date += timedelta(days=1)
    
    return pd.DataFrame(all_sequences, columns=['Date', 'Time', 'User', 
                                              'Activity Description', 'Reason for change', 'Anomaly'])

if __name__ == "__main__":
    # Generate dataset with 30% anomalous sequences
    df = generate_dataset(num_sequences=50, anomaly_probability=0.3)
    df.to_csv('audit_logs_with_anomalies.csv', index=False)
    print(f"Generated {len(df)} records with anomalies")