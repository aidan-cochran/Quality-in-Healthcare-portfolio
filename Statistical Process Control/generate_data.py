import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_dates(start_date, end_date):
    """
    Generate a list of dates between start_date and end_date for each workday.
    
    Parameters:
        start_date (datetime): The starting date
        end_date (datetime): The ending date
        
    Returns:
        list: A list of datetime objects representing workdays
    """
    date_list = []
    current_date = start_date
    
    while current_date <= end_date:
        # Only include weekdays (Monday=0, Sunday=6)
        if current_date.weekday() < 5:  # Monday to Friday
            date_list.append(current_date)
        current_date += timedelta(days=1)
    
    return date_list

def generate_shifts(date_list):
    """
    Generate shift information for each date.
    
    Parameters:
        date_list (list): List of dates
        
    Returns:
        list: A list of tuples with (date, shift)
    """
    shifts = []
    for date in date_list:
        for shift in ['Morning', 'Afternoon', 'Night']:
            shifts.append((date, shift))
    
    return shifts

def generate_cycle_times(mean_cycle_time, std_dev, num_records, line_efficiency):
    """
    Generate cycle times for a production process with occasional spikes.
    
    Parameters:
        mean_cycle_time (float): The average cycle time in seconds
        std_dev (float): Standard deviation of cycle time
        num_records (int): Number of cycle time records to generate
        line_efficiency (float): Efficiency factor (0-1) affecting cycle time
        
    Returns:
        list: A list of cycle times
    """
    # Base cycle times from normal distribution
    cycle_times = np.random.normal(mean_cycle_time / line_efficiency, std_dev, num_records)
    
    # Add occasional spikes (representing issues in production)
    spike_indices = np.random.choice(range(num_records), size=int(num_records * 0.05), replace=False)
    for idx in spike_indices:
        cycle_times[idx] *= random.uniform(1.5, 3.0)
    
    return np.maximum(cycle_times, mean_cycle_time * 0.5)  # Ensure minimum cycle time

def generate_defects(production_volume, base_defect_rate, quality_factor):
    """
    Generate defect counts based on production volume and quality factor.
    
    Parameters:
        production_volume (int): Number of units produced
        base_defect_rate (float): Base rate of defects (0-1)
        quality_factor (float): Factor representing line quality (0-1)
        
    Returns:
        dict: Dictionary with defect counts by type
    """
    # Adjust defect rate based on quality factor (higher quality = lower defects)
    effective_defect_rate = base_defect_rate * (1 - quality_factor)
    
    # Calculate total defects
    total_defects = int(np.random.binomial(production_volume, effective_defect_rate))
    
    # Distribute defects across different types
    defect_types = {
        'Dimensional': 0,
        'Surface': 0,
        'Assembly': 0,
        'Material': 0,
        'Other': 0
    }
    
    # Distribute total defects across types
    defect_weights = [0.35, 0.25, 0.20, 0.15, 0.05]  # Probabilities for each defect type
    
    if total_defects > 0:
        defect_distribution = np.random.multinomial(total_defects, defect_weights)
        
        for i, defect_type in enumerate(defect_types.keys()):
            defect_types[defect_type] = defect_distribution[i]
    
    return defect_types, total_defects

def generate_downtime(mean_downtime_minutes, reliability_factor):
    """
    Generate machine downtime data.
    
    Parameters:
        mean_downtime_minutes (float): Average downtime in minutes per day
        reliability_factor (float): Factor representing machine reliability (0-1)
        
    Returns:
        dict: Dictionary with downtime minutes by cause
    """
    # Adjust downtime based on reliability (higher reliability = less downtime)
    effective_downtime = mean_downtime_minutes * (1 - reliability_factor)
    
    # Determine if downtime occurs (80% chance of some downtime each day per line)
    if random.random() < 0.8:
        # Generate total downtime with variation
        total_downtime = np.random.gamma(shape=2.0, scale=effective_downtime/2)
        
        # Ensure minimum and maximum reasonable values
        total_downtime = min(max(total_downtime, 0), mean_downtime_minutes * 5)
        
        # Distribute downtime across different causes
        downtime_causes = {
            'Maintenance': 0,
            'Setup/Changeover': 0,
            'Breakdown': 0,
            'Material Shortage': 0,
            'Operator Absence': 0
        }
        
        # Different probability distributions for downtime causes
        cause_weights = [0.3, 0.25, 0.2, 0.15, 0.1]  # Probabilities for each cause
        
        downtime_distribution = np.random.multinomial(100, cause_weights)
        
        for i, cause in enumerate(downtime_causes.keys()):
            downtime_causes[cause] = round(total_downtime * downtime_distribution[i] / 100, 1)
    else:
        # No downtime
        total_downtime = 0
        downtime_causes = {cause: 0 for cause in ['Maintenance', 'Setup/Changeover', 'Breakdown', 
                                                 'Material Shortage', 'Operator Absence']}
    
    return downtime_causes, total_downtime

def calculate_quality_metrics(defects_total, production_volume):
    """
    Calculate quality control metrics.
    
    Parameters:
        defects_total (int): Total number of defects
        production_volume (int): Number of units produced
        
    Returns:
        dict: Dictionary with quality metrics
    """
    defect_rate = defects_total / production_volume if production_volume > 0 else 0
    
    # First Pass Yield (FPY)
    fpy = 1 - defect_rate
    
    # Defects Per Million Opportunities (DPMO)
    dpmo = defect_rate * 1000000
    
    # Rolled Throughput Yield (RTY) - simplified calculation
    rty = (1 - defect_rate) ** 1.5  # Assuming 1.5 process steps on average
    
    # Process Sigma Level (simplified calculation)
    if defect_rate == 0:
        sigma_level = 6.0
    elif defect_rate >= 1:
        sigma_level = 0.0
    else:
        # Approximate sigma level based on defect rate
        sigma_level = max(0, min(6, 0.8406 - 3.42 * np.log10(defect_rate)))
    
    return {
        'FPY': round(fpy, 4),
        'DPMO': int(dpmo),
        'RTY': round(rty, 4),
        'Sigma_Level': round(sigma_level, 2)
    }

def generate_production_volume(base_capacity, efficiency_factor, downtime_total):
    """
    Generate production volume based on capacity, efficiency and downtime.
    
    Parameters:
        base_capacity (int): Base production capacity per shift
        efficiency_factor (float): Efficiency factor (0-1)
        downtime_total (float): Total downtime in minutes
        
    Returns:
        int: Production volume
    """
    # Calculate available production time (assuming 8-hour shift = 480 minutes)
    available_time = 480 - downtime_total
    
    # Calculate effective capacity based on available time and efficiency
    effective_capacity = base_capacity * (available_time / 480) * efficiency_factor
    
    # Add random variation
    actual_production = int(np.random.normal(effective_capacity, effective_capacity * 0.05))
    
    # Ensure production is non-negative and has reasonable ceiling
    return max(0, min(actual_production, int(base_capacity * 1.2)))

def generate_time_motion_metrics(cycle_time, efficiency_factor):
    """
    Generate time and motion study metrics.
    
    Parameters:
        cycle_time (float): Average cycle time
        efficiency_factor (float): Efficiency factor (0-1)
        
    Returns:
        dict: Dictionary with time and motion metrics
    """
    # Calculate setup time (minutes)
    setup_time = np.random.normal(15, 5) * (1 + (1 - efficiency_factor))
    
    # Calculate operator movement time (seconds per cycle)
    movement_time = np.random.normal(cycle_time * 0.2, cycle_time * 0.05)
    
    # Calculate machine time (seconds per cycle)
    machine_time = cycle_time - movement_time
    
    # Calculate operator utilization (%)
    utilization = np.random.normal(0.7, 0.1) * efficiency_factor
    utilization = max(0.3, min(0.95, utilization))  # Keep within reasonable bounds
    
    # Calculate work-in-process (WIP) average
    wip_avg = np.random.normal(15, 5) * (1 + (1 - efficiency_factor))
    
    return {
        'Setup_Time_Minutes': round(setup_time, 1),
        'Movement_Time_Seconds': round(movement_time, 1),
        'Machine_Time_Seconds': round(machine_time, 1),
        'Operator_Utilization': round(utilization, 2),
        'WIP_Average': round(wip_avg, 1)
    }

# def get_single_data_point():
#     """
#     Generate and return a single manufacturing data point.
    
#     Returns:
#         list: A list containing one data point (as a dictionary)
#     """
#     # Define a single date
#     single_date = datetime(2023, 1, 2)  # January 2, 2023 (a Monday)
    
#     # Define production line parameters for a single line
#     line_name = 'Line A'
#     line_params = {
#         'mean_cycle_time': 45.0,
#         'cycle_time_std_dev': 5.0,
#         'base_capacity': 500,
#         'base_defect_rate': 0.025,
#         'mean_downtime': 30.0,
#         'efficiency_trend': [0.75, 0.78, 0.82, 0.85, 0.88, 0.90],
#         'quality_trend': [0.80, 0.82, 0.85, 0.87, 0.89, 0.90],
#         'reliability_trend': [0.82, 0.84, 0.86, 0.87, 0.89, 0.90]
#     }
    
#     # Set shift to Morning
#     shift = 'Morning'
    
#     # Get month index
#     month_idx = single_date.month - 1
    
#     # Get efficiency, quality, and reliability factors
#     efficiency_factor = line_params['efficiency_trend'][month_idx]
#     quality_factor = line_params['quality_trend'][month_idx]
#     reliability_factor = line_params['reliability_trend'][month_idx]
    
#     # Add daily variation
#     daily_variation = 0.05
#     efficiency_factor *= random.uniform(1 - daily_variation, 1 + daily_variation)
#     quality_factor *= random.uniform(1 - daily_variation, 1 + daily_variation)
#     reliability_factor *= random.uniform(1 - daily_variation, 1 + daily_variation)
    
#     # Ensure factors stay in valid range
#     efficiency_factor = max(0.5, min(0.99, efficiency_factor))
#     quality_factor = max(0.5, min(0.99, quality_factor))
#     reliability_factor = max(0.5, min(0.99, reliability_factor))
    
#     # Generate downtime data
#     downtime_data, downtime_total = generate_downtime(
#         line_params['mean_downtime'], reliability_factor)
    
#     # Generate production volume
#     production_volume = generate_production_volume(
#         line_params['base_capacity'], efficiency_factor, downtime_total)
    
#     # Generate defect data
#     defect_data, defects_total = generate_defects(
#         production_volume, line_params['base_defect_rate'], quality_factor)
    
#     # Calculate quality metrics
#     quality_metrics = calculate_quality_metrics(defects_total, production_volume)
    
#     # Generate cycle times for a sample
#     sample_size = min(20, production_volume) if production_volume > 0 else 0
#     cycle_times = generate_cycle_times(
#         line_params['mean_cycle_time'],
#         line_params['cycle_time_std_dev'],
#         sample_size,
#         efficiency_factor
#     )
    
#     # Calculate average cycle time
#     avg_cycle_time = np.mean(cycle_times) if len(cycle_times) > 0 else 0
    
#     # Generate time and motion metrics
#     time_motion_metrics = generate_time_motion_metrics(avg_cycle_time, efficiency_factor)
    
#     # Create the single record
#     record = {
#         'Date': single_date.strftime('%Y-%m-%d'),
#         'Shift': shift,
#         'Line': line_name,
#         'Production_Volume': production_volume,
#         'Average_Cycle_Time': round(avg_cycle_time, 2),
#         'Defects_Total': defects_total,
#         'Defect_Rate': round(defects_total / production_volume if production_volume > 0 else 0, 4),
#         'Downtime_Total': downtime_total
#     }
    
#     # Add defect breakdown
#     for defect_type, count in defect_data.items():
#         record[f'Defects_{defect_type}'] = count
    
#     # Add downtime breakdown
#     for cause, minutes in downtime_data.items():
#         record[f'Downtime_{cause}'] = minutes
    
#     # Add quality metrics
#     for metric, value in quality_metrics.items():
#         record[f'Quality_{metric}'] = value
    
#     # Add time and motion metrics
#     for metric, value in time_motion_metrics.items():
#         record[f'TimeMotion_{metric}'] = value
    
#     # Add factors
#     record['Efficiency_Factor'] = round(efficiency_factor, 3)
#     record['Quality_Factor'] = round(quality_factor, 3)
#     record['Reliability_Factor'] = round(reliability_factor, 3)
    
#     # Return as a list with one data point
#     return [record]

# def generate_multiple_data_points(num_points=1, start_date=pd.date_time(), randomize_all=True):
#     """
#     Generate multiple manufacturing data points with random variations.
    
#     Parameters:
#         num_points (int): Number of data points to generate (default: 10)
#         start_date (datetime): Starting date for the data points (default: Jan 1, 2023)
#         randomize_all (bool): Whether to randomize all parameters (default: True)
        
#     Returns:
#         list: A list of dictionaries, each representing one data point
#     """

#     # start_date = datetime(2023, 1, 2)
    
#     # Define all production lines with their characteristics
#     production_lines = {
#         'Line A': {
#             'mean_cycle_time': 45.0,
#             'cycle_time_std_dev': 5.0,
#             'base_capacity': 500,
#             'base_defect_rate': 0.025,
#             'mean_downtime': 30.0,
#             'efficiency_trend': [0.75, 0.78, 0.82, 0.85, 0.88, 0.90],
#             'quality_trend': [0.80, 0.82, 0.85, 0.87, 0.89, 0.90],
#             'reliability_trend': [0.82, 0.84, 0.86, 0.87, 0.89, 0.90]
#         },
#         'Line B': {
#             'mean_cycle_time': 60.0,
#             'cycle_time_std_dev': 8.0,
#             'base_capacity': 400,
#             'base_defect_rate': 0.015,
#             'mean_downtime': 25.0,
#             'efficiency_trend': [0.88, 0.89, 0.90, 0.91, 0.92, 0.93],
#             'quality_trend': [0.90, 0.91, 0.92, 0.92, 0.93, 0.94],
#             'reliability_trend': [0.89, 0.90, 0.91, 0.92, 0.93, 0.94]
#         },
#         'Line C': {
#             'mean_cycle_time': 30.0,
#             'cycle_time_std_dev': 6.0,
#             'base_capacity': 650,
#             'base_defect_rate': 0.035,
#             'mean_downtime': 40.0,
#             'efficiency_trend': [0.65, 0.70, 0.75, 0.80, 0.83, 0.85],
#             'quality_trend': [0.70, 0.75, 0.80, 0.83, 0.85, 0.87],
#             'reliability_trend': [0.75, 0.78, 0.82, 0.85, 0.87, 0.88]
#         }
#     }
    
#     shifts = ['Morning', 'Afternoon', 'Night']
#     all_records = []
#     current_date = start_date
    
#     for i in range(num_points):
#         # Randomly select a line and shift
#         line_name = random.choice(list(production_lines.keys()))
#         shift = random.choice(shifts)
#         line_params = production_lines[line_name]
        
#         # Increment date for each record (only move to next workday occasionally)
#         if i > 0 and random.random() < 0.4:  # 40% chance to move to next day
#             current_date += timedelta(days=1)
#             # Skip weekends
#             while current_date.weekday() >= 5:
#                 current_date += timedelta(days=1)
        
#         # Get month index
#         month_idx = min(current_date.month - 1, 5)  # Cap at month 5 (June)
        
#         # Get efficiency, quality, and reliability factors from trends
#         efficiency_factor = line_params['efficiency_trend'][month_idx]
#         quality_factor = line_params['quality_trend'][month_idx]
#         reliability_factor = line_params['reliability_trend'][month_idx]
        
#         # Add random daily variation
#         if randomize_all:
#             daily_variation = 0.05
#             efficiency_factor *= random.uniform(1 - daily_variation, 1 + daily_variation)
#             quality_factor *= random.uniform(1 - daily_variation, 1 + daily_variation)
#             reliability_factor *= random.uniform(1 - daily_variation, 1 + daily_variation)
        
#         # Ensure factors stay in valid range
#         efficiency_factor = max(0.5, min(0.99, efficiency_factor))
#         quality_factor = max(0.5, min(0.99, quality_factor))
#         reliability_factor = max(0.5, min(0.99, reliability_factor))
        
#         # Generate downtime data
#         downtime_data, downtime_total = generate_downtime(
#             line_params['mean_downtime'], reliability_factor)
        
#         # Generate production volume
#         production_volume = generate_production_volume(
#             line_params['base_capacity'], efficiency_factor, downtime_total)
        
#         # Generate defect data
#         defect_data, defects_total = generate_defects(
#             production_volume, line_params['base_defect_rate'], quality_factor)
        
#         # Calculate quality metrics
#         quality_metrics = calculate_quality_metrics(defects_total, production_volume)
        
#         # Generate cycle times for a sample
#         sample_size = min(20, production_volume) if production_volume > 0 else 0
#         cycle_times = generate_cycle_times(
#             line_params['mean_cycle_time'],
#             line_params['cycle_time_std_dev'],
#             sample_size,
#             efficiency_factor
#         )
        
#         # Calculate average cycle time
#         avg_cycle_time = np.mean(cycle_times) if len(cycle_times) > 0 else 0
        
#         # Generate time and motion metrics
#         time_motion_metrics = generate_time_motion_metrics(avg_cycle_time, efficiency_factor)
        
#         # Create the record
#         record = {
#             'Date': current_date.strftime('%Y-%m-%d'),
#             'Shift': shift,
#             'Line': line_name,
#             'Production_Volume': production_volume,
#             'Average_Cycle_Time': round(avg_cycle_time, 2),
#             'Defects_Total': defects_total,
#             'Defect_Rate': round(defects_total / production_volume if production_volume > 0 else 0, 4),
#             'Downtime_Total': downtime_total
#         }
        
#         # Add defect breakdown
#         for defect_type, count in defect_data.items():
#             record[f'Defects_{defect_type}'] = count
        
#         # Add downtime breakdown
#         for cause, minutes in downtime_data.items():
#             record[f'Downtime_{cause}'] = minutes
        
#         # Add quality metrics
#         for metric, value in quality_metrics.items():
#             record[f'Quality_{metric}'] = value
        
#         # Add time and motion metrics
#         for metric, value in time_motion_metrics.items():
#             record[f'TimeMotion_{metric}'] = value
        
#         # Add factors
#         record['Efficiency_Factor'] = round(efficiency_factor, 3)
#         record['Quality_Factor'] = round(quality_factor, 3)
#         record['Reliability_Factor'] = round(reliability_factor, 3)
        
#         all_records.append(record)
    
#     return all_records

def generate_manufacturing_data(start_date=datetime(2023, 1, 1), end_date=datetime(2023, 6, 30)):
    """
    Main function to generate the complete manufacturing dataset.
    
    Returns:
        pandas.DataFrame: The complete manufacturing dataset
    """
    # Six months of data
    # Generate dates
    date_list = generate_dates(start_date, end_date)
    
    # Generate shifts
    shifts = generate_shifts(date_list)
    
    # Define production lines with their characteristics
    production_lines = {
        'Line A': {
            'mean_cycle_time': 45.0,  # seconds
            'cycle_time_std_dev': 5.0,
            'base_capacity': 500,  # units per shift
            'base_defect_rate': 0.025,
            'mean_downtime': 30.0,  # minutes
            'efficiency_trend': [0.75, 0.78, 0.82, 0.85, 0.88, 0.90],  # Monthly trend
            'quality_trend': [0.80, 0.82, 0.85, 0.87, 0.89, 0.90],     # Monthly trend
            'reliability_trend': [0.82, 0.84, 0.86, 0.87, 0.89, 0.90]  # Monthly trend
        },
        'Line B': {
            'mean_cycle_time': 60.0,
            'cycle_time_std_dev': 8.0,
            'base_capacity': 400,
            'base_defect_rate': 0.015,
            'mean_downtime': 25.0,
            'efficiency_trend': [0.88, 0.89, 0.90, 0.91, 0.92, 0.93],
            'quality_trend': [0.90, 0.91, 0.92, 0.92, 0.93, 0.94],
            'reliability_trend': [0.89, 0.90, 0.91, 0.92, 0.93, 0.94]
        },
        'Line C': {
            'mean_cycle_time': 30.0,
            'cycle_time_std_dev': 6.0,
            'base_capacity': 650,
            'base_defect_rate': 0.035,
            'mean_downtime': 40.0,
            'efficiency_trend': [0.65, 0.70, 0.75, 0.80, 0.83, 0.85],
            'quality_trend': [0.70, 0.75, 0.80, 0.83, 0.85, 0.87],
            'reliability_trend': [0.75, 0.78, 0.82, 0.85, 0.87, 0.88]
        }
    }
    
    # Initialize list to store all data records
    all_data = []
    
    # Generate data for each combination of line, date, and shift
    for line_name, line_params in production_lines.items():
        for date_idx, (date, shift) in enumerate(shifts):
            # Determine which month we're in (0-5 for Jan-Jun)
            month_idx = date.month - 1
            
            # Get current efficiency, quality, and reliability factors from trends
            efficiency_factor = line_params['efficiency_trend'][month_idx]
            quality_factor = line_params['quality_trend'][month_idx]
            reliability_factor = line_params['reliability_trend'][month_idx]
            
            # Add random daily variation to factors
            daily_variation = 0.05
            efficiency_factor *= random.uniform(1 - daily_variation, 1 + daily_variation)
            quality_factor *= random.uniform(1 - daily_variation, 1 + daily_variation)
            reliability_factor *= random.uniform(1 - daily_variation, 1 + daily_variation)
            
            # Ensure factors stay in valid range
            efficiency_factor = max(0.5, min(0.99, efficiency_factor))
            quality_factor = max(0.5, min(0.99, quality_factor))
            reliability_factor = max(0.5, min(0.99, reliability_factor))
            
            # Generate downtime data
            downtime_data, downtime_total = generate_downtime(
                line_params['mean_downtime'], reliability_factor)
            
            # Generate production volume
            production_volume = generate_production_volume(
                line_params['base_capacity'], efficiency_factor, downtime_total)
            
            # Generate defect data
            defect_data, defects_total = generate_defects(
                production_volume, line_params['base_defect_rate'], quality_factor)
            
            # Calculate quality metrics
            quality_metrics = calculate_quality_metrics(defects_total, production_volume)
            
            # Generate cycle times for a sample of units
            sample_size = min(20, production_volume) if production_volume > 0 else 0
            cycle_times = generate_cycle_times(
                line_params['mean_cycle_time'], 
                line_params['cycle_time_std_dev'],
                sample_size,
                efficiency_factor
            )
            
            # Calculate average cycle time
            avg_cycle_time = np.mean(cycle_times) if len(cycle_times) > 0 else 0
            
            # Generate time and motion metrics
            time_motion_metrics = generate_time_motion_metrics(avg_cycle_time, efficiency_factor)
            
            # Create record for this line, date, and shift 
            record = {
                'Date': date.strftime('%Y-%m-%d'),
                'Shift': shift,
                'Line': line_name,
                'Production_Volume': production_volume,
                'Average_Cycle_Time': round(avg_cycle_time, 2),
                'Defects_Total': defects_total,
                'Defect_Rate': round(defects_total / production_volume if production_volume > 0 else 0, 4),
                'Downtime_Total': downtime_total
            }
            
            # Add defect breakdown
            for defect_type, count in defect_data.items():
                record[f'Defects_{defect_type}'] = count
            
            # Add downtime breakdown
            for cause, minutes in downtime_data.items():
                record[f'Downtime_{cause}'] = minutes
            
            # Add quality metrics
            for metric, value in quality_metrics.items():
                record[f'Quality_{metric}'] = value
            
            # Add time and motion metrics 
            for metric, value in time_motion_metrics.items():
                record[f'TimeMotion_{metric}'] = value
            
            # Add factors (these would normally be hidden variables but useful for students)
            record['Efficiency_Factor'] = round(efficiency_factor, 3)
            record['Quality_Factor'] = round(quality_factor, 3)
            record['Reliability_Factor'] = round(reliability_factor, 3)
            
            # Add to the list of all records
            all_data.append(record)
    
    # Convert to DataFrame
    df = pd.DataFrame(all_data)
    
    # Add a unique ID column
    
    df['Record_ID'] = df.index + 1
    
    # Reorder columns to put ID first
    cols = df.columns.tolist()
    cols = ['Record_ID'] + [col for col in cols if col != 'Record_ID']
    df = df[cols]
    
    return df

if __name__ == "__main__":
    # Generate the data
    print("Generating manufacturing process data...")
    manufacturing_data = generate_manufacturing_data()
    
    # Save to CSV
    output_file = "manufacturiocess_data.csv"
    manufacturing_data.to_csv(output_file, index=False)
    
    # Print summary
    print(f"Data generation complete. {len(manufacturing_data)} records created.")
    print(f"Data saved to {output_file}")
    print("\nData summary:")
    print(f"- Time period: Jan 1, 2023 to Jun 30, 2023")
    print(f"- Production lines: {manufacturing_data['Line'].nunique()}")
    print(f"- Shifts: {manufacturing_data['Shift'].nunique()}")
    print(f"- Total production volume: {manufacturing_data['Production_Volume'].sum()}")
    print(f"- Average defect rate: {manufacturing_data['Defect_Rate'].mean():.4f}")
    print(f"- Average downtime: {manufacturing_data['Downtime_Total'].mean():.2f} minutes per shift")