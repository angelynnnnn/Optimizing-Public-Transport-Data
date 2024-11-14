import numpy as np
import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import math
from datetime import datetime, time, timedelta
import simpy
import random

MAPBOX_API = 'pk.eyJ1IjoiZ3VvaG9uZ3lpMTExIiwiYSI6ImNtMng0OHc4cTAwenMybG9iczg4cjBoNjcifQ.tc6o1kU_mTemKQhbVy5mNA'

@st.cache_data
def get_bus_stops():
    bus_stops = pd.read_csv('bus_stop_coords.csv', header=None)
    bus_stops.rename(columns={0:"Bus Stop", 1:"lat", 2:"lon"}, inplace=True)

    return bus_stops

bus_stops = get_bus_stops()
MAP_CENTER = [1.3083003040174188, 103.79569430095988]
KR_CENTER = [1.29782, 103.77711]

st.header("NUS Internal Shuttle Bus Service")

# INPUT DATA HERE
data = pd.read_csv('synthetic_data.csv')
monday_data = data[data['day_of_the_week'] == 'Monday'] # For simulation purposes, we will use data where the trips are done on Mondays

monday_data['time_start'] = pd.to_datetime(monday_data['time_start'], format='%H:%M:%S')

# Now apply rounding to the nearest 10 minutes
monday_data['time_start'] = monday_data['time_start'].dt.round('10min')
monday_data['time_start'] = monday_data['time_start'].dt.time

monday_data = monday_data.drop(columns=['role', 'frequency_of_travel','primary_purpose', 'travel_days', 'travel_hours', 'not_able_to_get_on', 'additional_features_frequency', 'additional_features_seats',
                          'additional_features_cleanliness', 'additional_features_comfortable', 'additional_features_route_coverage', 'additional_features_updates',
                          'issues_with_quality_of_info', 'special_events', 'seasonal_changes'])


# Routes
A1_bus = ['KR Bus Terminal', 'LT13', 'AS5', 'BIZ2', 'Opp TCOMS', 'PGP Terminal', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'YIH', 'CLB', 'KR Bus Terminal']
A2_bus = ['KR Bus Terminal', 'IT', 'Opp YIH', 'Museum', 'UHC', 'Opp University Hall', 'S17', 'Opp KR MRT', 'PGP Foyer', 'TCOMS', 'Opp HSSML', 'Opp NUSS', 'Ventus', 'KR Bus Terminal']
D1_bus = ['COM3', 'Opp HSSML', 'Opp NUSS', 'Ventus', 'IT', 'Opp YIH', 'Museum', 'UTown', 'YIH', 'CLB', 'LT13', 'AS5', 'BIZ2', 'COM3']
D2_bus = ['COM3', 'Opp TCOMS', 'PGP Terminal', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'Museum', 'UTown', 'UHC', 'Opp University Hall', 'S17', 'Opp KR MRT', 'PGP Foyer', 'TCOMS', 'COM3']
BTC_bus = ['Oei Tiong Ham Building (BTC)', 'Botanic Gardens MRT (BTC)', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'UTown', 'Raffles Hall', 'Kent Vale', 'Museum', 'YIH', 'CLB', 'LT13', 'AS5', 'BIZ2', 'PGP Terminal', 'College Green (BTC)', 'Oei Tiong Ham Building (BTC)']
E_bus = ['UTown', 'Raffles Hall', 'Kent Vale', 'EA', 'SDE3', 'IT', 'Opp YIH', 'UTown']
K_bus = ['PGP Terminal', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'YIH', 'CLB', 'Opp SDE3', 'The Japanese Primary School', 'Kent Vale', 'Museum', 'UHC', 'Opp University Hall', 'S17', 'Opp KR MRT', 'PGP Foyer']
L_bus = ['Oei Tiong Ham Building (BTC)', 'Botanic Gardents MRT (BTC)', 'College Green (BTC)', 'Oei Tiong Ham Building (BTC)']

bus_routes = {'A1':A1_bus, 'A2':A2_bus, 'D1':D1_bus, 'D2':D2_bus, 'BTC':BTC_bus, 'E':E_bus, 'K':K_bus}

@st.cache_data
def bus_service_data(route_lst):

    stops = bus_stops[bus_stops['Bus Stop'].isin(route_lst)]
    route_df = pd.DataFrame({'Bus Stop': route_lst})
    route_df['route_index'] = route_df.index
    bus_df = route_df.merge(stops, on='Bus Stop', how='left')
    bus_df.loc[bus_df['route_index']==0, 'color'] = 'red'
    bus_df.loc[bus_df['route_index']!=0, 'color'] = 'blue'
    bus_df.loc[bus_df['route_index']==bus_df.shape[0]-1, 'color'] = 'red'
    bus_df.drop(columns='route_index', inplace=True)

    return bus_df

def get_route_timing(route, bus_stops_df):
    route_df = pd.DataFrame({'Bus Stop': route})
    route_df = route_df.merge(bus_stops_df, on='Bus Stop', how='left')
    dir_coord = [(route_df['lon'].iloc[i], route_df['lat'].iloc[i]) for i in range(len(route_df))]
    coords = ';'.join([f"{lon},{lat}" for lon, lat in dir_coord])
    mapbox_url = f'https://api.mapbox.com/directions/v5/mapbox/driving/{coords}?alternatives=false&geometries=geojson&language=en&overview=full&steps=true&access_token={MAPBOX_API}'
    response = requests.get(mapbox_url)
    route_data = response.json()

    if 'routes' in route_data and len(route_data['routes']) > 0:
        segment_durations = []
        for leg in route_data['routes'][0]['legs']:
            segment_durations.append(leg['duration'])
        total_duration_seconds = sum(segment_durations)
        total_duration_minutes = total_duration_seconds / 60
        return total_duration_minutes
    else:
        return None

route_times = {
    'A1': get_route_timing(A1_bus, bus_stops),
    'A2': get_route_timing(A1_bus, bus_stops), 
    'BTC': get_route_timing(BTC_bus, bus_stops),
    'D1': get_route_timing(D1_bus, bus_stops),
    'D2': get_route_timing(D2_bus, bus_stops),
    'E': get_route_timing(E_bus, bus_stops),
    'K': get_route_timing(K_bus, bus_stops),
}

@st.cache_data
def route_map(bus):
    bus_df = bus_service_data(bus_routes[bus])

    # Place markers on map
    if bus == 'BTC':
        map = folium.Map(location=MAP_CENTER, zoom_start=14)
    else: 
        map = folium.Map(location=KR_CENTER, zoom_start=16)
    for i in range(len(bus_df)):
        folium.Marker(location=[bus_df.iloc[i,1], bus_df.iloc[i,2]], icon=folium.Icon(color=bus_df.iloc[i,3]), popup=bus_df.iloc[i,0]).add_to(map)

    # Draw out routes for each bus service
    for i in range(len(bus_df)-1):
        lat_source, lon_source = bus_df.iloc[i, 1], bus_df.iloc[i, 2]
        lat_dest, lon_dest = bus_df.iloc[i+1, 1], bus_df.iloc[i+1, 2]
        url = f'https://api.mapbox.com/directions/v5/mapbox/driving/{lon_source},{lat_source};{lon_dest},{lat_dest}?alternatives=false&geometries=geojson&language=en&overview=full&steps=true&access_token={MAPBOX_API}'
        response = requests.get(url)
        direction = response.json()
        bus_df.loc[i, 'duration_to_next'] = math.ceil(direction['routes'][0]['duration']/60) + 1
        bus_df['minutes_from_start'] = bus_df['duration_to_next'].cumsum()
        bus_df['minutes_from_start'] = bus_df['minutes_from_start'].shift(1, fill_value=0) # calculate the minutes from the terminal

        route_coords = [list(reversed(coord)) for coord in direction['routes'][0]['geometry']['coordinates']]
        folium.PolyLine(locations=route_coords,
                color='blue',
                weight=3,
                smooth_factor=0.1).add_to(map)   

    # Show demand for each bus stop
    global time_to_show

    selected_time_data = monday_data[(monday_data['time_start'] == time_to_show) & (monday_data['ISB_Service'] == bus)]
    values_to_plot = selected_time_data['bus_stop_board'].value_counts()
    merged = pd.merge(values_to_plot, bus_stops, left_on='bus_stop_board', right_on='Bus Stop')

    for _, row in merged.iterrows():
        folium.Circle(
            location=[row['lat'], row['lon']],
            radius=row['count']*4,
            color=None,
            fill=True,
            fill_color='purple',
            fill_opacity=0.5,
        ).add_to(map)
        
    return bus_df, map, merged

# ====================================================================

# SIMULATION
# This simulation allows us to determine the minimum number of buses for each bus service required, so that every trip in the schedule will be fulfilled.

st.subheader("Simulation")
col1, col2 = st.columns(2)

with col1:
    sim_bus_service = st.selectbox(label="Bus Service", options=['A1', 'A2', 'D1', 'D2', 'BTC', 'E', 'K'], key='sim')
with col2:
    num_buses = st.number_input('Number of buses', 1, 10)

start_sim = st.button('Simulate')

# Bus frequencies, taken from NUS UCI website 
# (https://uci.nus.edu.sg/oca/mobilityservices/getting-around-nus/)


bus_freq = {
    'A1': {0: ['07:15', '08:00', '9min'],
           1: ['08:00', '10:00', '5min'],
           2: ['10:00', '11:00', '11min'],
           3: ['11:00', '14:00', '6min'],
           4: ['14:00', '17:15', '9min'],
           5: ['17:15', '19:30', '6min'],
           6: ['19:30', '23:00', '15min']},
    'A2': {
        0: ['07:15', '10:00', '7min'],
        1: ['10:00', '11:15', '10min'],
        2: ['11:15', '14:00', '7min'],
        3: ['14:00', '17:00', '8min'],
        4: ['17:00', '19:30', '7min'],
        5: ['19:30', '21:30', '12min'],
        6: ['21:30', '23:00', '15min']
    },
    'D1': {
        0: ['07:15', '08:00', '11min'],
        1: ['08:00', '19:30', '7min'],
        2: ['19:30', '21:30', '12min'],
        3: ['21:30', '23:00', '15min']
    },
    'D2': {
        0: ['07:15', '10:00', '6min'],
        1: ['10:00', '11:15', '10min'],
        2: ['11:15', '14:00', '6min'],
        3: ['14:00', '17:15', '8min'],
        4: ['17:15', '19:30', '6min'],
        5: ['19:30', '21:30', '11min'],
        6: ['21:30', '23:00', '15min']
    },
    'BTC': {
        0: ['07:30', '10:00', '30min'],
        1: ['10:00', '11:10', '35min'],
        2: ['11:10', '14:10', '30min'],
        3: ['14:10', '17:10', '45min'],
        4: ['17:10', '19:40', '30min'],
        5: ['19:40', '21:10', '45min'],
        6: ['21:10', '21:40', '30min']
    },
    'E': {
        0: ['08:00', '16:00', '15min'],
    },
    'K': {
        0: ['07:00', '23:00', '15min']
    }
}

def create_schedule(freq_dict, bus): # freq_dict is a dictionary with bus service as key and a dict of [start time, end time, freq] as values
    bus_timings = {}
    frequencies = freq_dict[bus]
    bus_timings[bus] = []
    for t in range(len(frequencies)):
        times = pd.date_range(start=frequencies[t][0], end=frequencies[t][1], freq=frequencies[t][2]).time.tolist()
        if times[0] in bus_timings[bus]: # dont add timings that are already in list
            times = times[1:]

        bus_timings[bus] += times

    return bus_timings # returns a dictionary with bus as key and a list of departure times (datetime object) as values
    

# Simulating bus schedule
BUS_CAPACITY = 88
queue_buses = [i+1 for i in range(num_buses)] # so that buses leave the terminal sequentially
sim_log = [] # store the strings of outputs
passengers_served = 0

sim_bus_timings = pd.DataFrame(create_schedule(bus_freq, sim_bus_service)[sim_bus_service], columns=['depart_time'])

day_start = sim_bus_timings.loc[0, 'depart_time']
day_end = time(23, 59)
day_starttime = datetime.combine(datetime.today(), day_start)
day_endtime = datetime.combine(datetime.today(), day_end)

end_time = (day_endtime - day_starttime).total_seconds() / 60  # Calculate the number of minutes from the first bus to 2359hrs

# Calculate number of minutes from the first bus
def time_from_start(time):
    global day_start
    time_start = datetime.combine(datetime.today(), day_start)
    time_curr = datetime.combine(datetime.today(), time)

    duration = (time_curr - time_start).total_seconds() / 60

    return duration

def sim_time_to_actual(minutes):
    global day_starttime
    new_time = (day_starttime + timedelta(minutes=minutes)).strftime('%H:%M')

    return new_time

sim_bus_timings['minutes_from_start'] = sim_bus_timings['depart_time'].apply(time_from_start) # creates a column that gives the minutes from the first bus
bus_data = route_map(sim_bus_service)[0] # contains route data with travel times to next stop

def bus_route(env, bus_id, bus_df): # bus_df is a df of route data with travel times
    global passengers_served
    stop_index = 0
    onboard = 0
    while stop_index < len(bus_df):

        stop = bus_df.iloc[stop_index]
        stop_name = stop['Bus Stop']
        travel_time = stop['duration_to_next']
        if stop_index != 0:
            # print(f"Bus {bus_id} reaches {stop_name} at {env.now}")
            log_msg = f"Bus {bus_id} reaches {stop_name} at {sim_time_to_actual(env.now)}"
            sim_log.append(log_msg)

        # Alight passengers
        if stop_index != len(bus_df) - 1:
            num_alighting = random.randint(0, onboard)
            onboard -= num_alighting
        else: # let all passengers alight
            num_alighting = onboard
            onboard = 0

        log_msg = f"Bus {bus_id} at {stop_name}: {num_alighting} alight, {onboard} onboard"
        sim_log.append(log_msg)

        # Board passengers
        if stop_index != len(bus_df) - 1:
            queue = random.randint(0, 50) # replace with demand data
            num_boarding = min(queue, BUS_CAPACITY - onboard)
            queue -= num_boarding
            onboard += num_boarding
            passengers_served += num_boarding
        else: # do not let passengers board
            num_boarding = 0

        log_msg = f"Bus {bus_id} at {stop_name}: {num_boarding} board, {onboard} onboard"
        sim_log.append(log_msg)

        if pd.notna(travel_time):
            yield env.timeout(travel_time)

        stop_index += 1

    return_to_terminal = 0
    yield env.timeout(return_to_terminal)
    log_msg = f"Bus {bus_id} returns to the terminal at {sim_time_to_actual(env.now)}"
    sim_log.append(log_msg)
    queue_buses.append(bus_id)

def bus_departure(env, bus_schedule):
    previous_time = 0
    for _, row in bus_schedule.iterrows():
        dept_time = row['minutes_from_start']
        wait_time = dept_time - previous_time
        yield env.timeout(wait_time)
        previous_time = dept_time

        if queue_buses: # empty buses are available for a trip
            bus_id = queue_buses.pop(0)
            log_msg = f"Bus {bus_id} departs at {sim_time_to_actual(env.now)}"
            sim_log.append(log_msg)

            env.process(bus_route(env, bus_id, bus_data))

        else:
            log_msg = f"No bus available for scheduled departure at {sim_time_to_actual(env.now)}"
            sim_log.append(log_msg)


def main_sim():
    env = simpy.Environment()

    env.process(bus_departure(env, sim_bus_timings)) # sim_bus_timings is a DF of the schedule created from create_schedules, with a column that has the minutes from start
    
    env.run(until=end_time)

if start_sim:
    main_sim()

unavailable_count = sum(1 for s in sim_log if 'available' in s)
total_trips = len(sim_bus_timings)

st.text_area("Simulation Log", "\n".join(sim_log), height=350)
st.write(f'Number of trips not done: {unavailable_count}')
st.write(f'Total number of trips: {total_trips}')

st.text('')
st.text('')
st.text('')

# INPUT PREDICTED DEMAND DATA HERE
predicted_demand = pd.read_csv("future_predicted_data.csv")
predicted_demand['predicted_count'] = predicted_demand['predicted_count'].apply(math.ceil)
predicted_demand['ISB_Service'] = predicted_demand['ISB_Service'].replace('BTC (Bukit Timah Campus)', 'BTC')
predicted_demand['time_start'] = pd.to_datetime(predicted_demand['time_start']).dt.time

st.subheader('Optimal Route and Bus Allocation')
day_to_sim = st.selectbox('Day of Week', ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'])

start_time = st.time_input('Start Time', value=None, key='start')
end_time = st.time_input('End Time', value=None, key='end')
optimize = st.button('Optimize')

# Create a list of timings that will reach a bus stop
def stop_schedule(bus_schedule, minutes): # minutes is the time required to reach the bus stop from the terminal
    if minutes == 0:
        return bus_schedule
    
    schedule = []
    for t in bus_schedule:
        new_t = datetime.combine(datetime.today(), t) + timedelta(minutes=minutes)
        schedule.append(new_t.time())

    return schedule

# algorithm for route optimization is the calculation of satisfaction score

def buses_at_bus_stops():
    bus_stops_dict = {stops: [] for stops in bus_stops['Bus Stop']}
    for stops in bus_stops_dict.keys():
        for bus, route_list in bus_routes.items():
            if stops in route_list and bus not in bus_stops_dict[stops]:
                bus_stops_dict[stops].append(bus)

    return bus_stops_dict

def generate_schedule(bus_stop, bus):
    bus_df = route_map(bus)[0]
    minutes = bus_df.loc[bus_df['Bus Stop'] == bus_stop, 'minutes_from_start'].values[0]

    return stop_schedule(create_schedule(bus_freq, bus)[bus], minutes)

def get_next_bus_time(curr_time, bus_stop, bus):
    schedule = generate_schedule(bus_stop, bus)
    next_times = [bus_time for bus_time in schedule if bus_time >= curr_time]
    return min(next_times) if next_times else None

def time_diff(time1, time2):
    dt_time1 = datetime.combine(datetime.today(), time1)
    dt_time2 = datetime.combine(datetime.today(), time2)

    return (dt_time2 - dt_time1).total_seconds() / 60

demand_by_day = predicted_demand[predicted_demand['day_of_the_week'] == day_to_sim]
bus_dict = buses_at_bus_stops()

def get_density_scores(bus_stop):
    buses = bus_dict[bus_stop]
    time_range = pd.date_range(start=datetime.combine(datetime.today(), start_time), end=datetime.combine(datetime.today(), end_time), freq='T').time
    density_df = pd.DataFrame(0, index=time_range, columns=buses)
    for bus in buses:
        for t in density_df.index:
            t_data = demand_by_day[(demand_by_day['time_start'] == t) & (demand_by_day['ISB_Service'] == bus)]
            density_df.at[t, bus] += t_data.loc[t_data['bus_stop_board'] == bus_stop, 'predicted_count'].values[0]
        
    for bus in buses:
        schedule = generate_schedule(bus_stop, bus)
        cum_sum = 0
        for t in density_df.index:
            cum_sum += density_df.loc[t, bus]
            if t in schedule:
                cum_sum = 0
            density_df.at[t, bus] = cum_sum

    density_df = density_df.drop(columns=[col for col in ['K', 'E', 'BTC'] if col in density_df.columns], errors='ignore')

    density_df['Total'] = density_df.sum(axis=1)

    def assign_scores(total):
        if 0 <= total <= 20:
            return total * 1
        elif 21 <= total <= 40:
            return total * 2
        elif 41 <= total <= 60:
            return total * 3
        elif 61 <= total <= 80:
            return total * 4
        elif 81 <= total <= 100:
            return total * 5
        else:
            return total * 6

    density_df['Score'] = density_df['Total'].apply(assign_scores)
            
    return density_df


def get_satisfaction_scores(day):
    # Create dictionary to store number of people waiting and the scores
    waittime_dict = {
        stop_name: {bus: 0 for bus in bus_routes.keys()} for stop_name in bus_stops['Bus Stop'] # metric score
    }
    demand_by_day = predicted_demand[predicted_demand['day_of_the_week'] == day]
    demand_by_day_time = demand_by_day[demand_by_day['time_start'].between(start_time, end_time)]
    bus_stops_buses = buses_at_bus_stops()

    def get_entries(stop, bus):
        entries = demand_by_day_time[(demand_by_day_time['ISB_Service']==bus) & (demand_by_day_time['bus_stop_board']==stop)].copy()
        entries['next_bus'] = entries.apply(lambda r: get_next_bus_time(r['time_start'], r['bus_stop_board'], r['ISB_Service']), axis=1)
        entries['minutes_to_next_bus'] = entries.apply(lambda r: time_diff(r['time_start'], r['next_bus']), axis=1)

        return entries

    for stop in bus_stops_buses.keys():
        for bus in bus_stops_buses[stop]:
            entries = get_entries(stop, bus)

            total_waiting_time = (entries['predicted_count'] * entries['minutes_to_next_bus']).sum()
            waittime_dict[stop][bus] = total_waiting_time

    return waittime_dict

def get_priority_score(score_dict):
    priority_dict = {}
    for stop in score_dict.keys():
        priority_dict[stop] = score_dict[stop]['A1'] + score_dict[stop]['A2'] + score_dict[stop]['D1'] + score_dict[stop]['D2']
        density_scores = get_density_scores(stop)
        priority_dict[stop] += density_scores['Score'].sum()

    priority_dict = dict(sorted(priority_dict.items(), key=lambda item: item[1], reverse=True))

    return priority_dict

def generate_time_intervals(start_time_str, end_time_str):
    start_time = datetime.combine(datetime.today(), start_time_str)
    end_time = datetime.combine(datetime.today(), end_time_str)

    # Generate the list of 15-minute intervals
    time_intervals = []
    current_time = start_time

    while current_time < end_time:
        time_intervals.append((current_time.hour, current_time.minute))
        current_time += timedelta(minutes=15)

    return time_intervals

def get_demand(data):
    demand_by_interval = data.groupby(['ISB_Service', 'day_of_the_week', 'hour', 'minute'])['predicted_count'].sum().reset_index(name='predicted_count')
    return demand_by_interval


## Function to calculate optimal bus allocation
def optimize_buses_needed(data, route_times, bus_capacity):
    max_demand_per_route = data.groupby(['ISB_Service', 'hour', 'minute'])['predicted_count'].max().reset_index(name='max_demand')

    def calculate_buses_needed(row):
        route_id = row['ISB_Service']
        peak_demand = row['max_demand']
        turnaround_time = route_times.get(route_id)
        if turnaround_time is None or turnaround_time == 0:
            return np.nan
        trips_per_interval = (15 / turnaround_time)
        buses_needed = np.ceil(np.ceil(peak_demand / bus_capacity) / trips_per_interval)
        return buses_needed

    max_demand_per_route['buses_needed'] = max_demand_per_route.apply(calculate_buses_needed, axis=1)
    buses_per_interval = max_demand_per_route.groupby(['hour', 'minute'])['buses_needed'].sum().reset_index(name='min_buses_needed')
    buses_needed_per_route = max_demand_per_route.groupby(['ISB_Service'])['buses_needed'].max().reset_index()

    return buses_per_interval, buses_needed_per_route

def consider_express(data, express, day, time, initial_ratio=0.2, increment=0.1):
    EX_time = get_route_timing(express, bus_stops)
    route_times['EX'] = EX_time
    temp = data[data['day_of_the_week'] == day].copy()

    # Get the optimal ratio of demand that would utilise the express bus
    ratio = initial_ratio
    optimal_buses_needed = None
    optimal_ratio = None
    min_total_buses = float('inf')
    
    while ratio <= 1.0:
        adjusted_data = temp.copy()
        for hour, minute in time:
            for stop in express:
                stop_demand = temp[(temp['hour'] == hour) & (temp['minute'] == minute) & (temp['bus_stop_board'] == stop)]['predicted_count'].sum()
                express_demand = ratio * stop_demand
                adjusted_data.loc[(adjusted_data['hour'] == hour) & (adjusted_data['minute'] == minute) & (adjusted_data['bus_stop_board'] == stop), 'predicted_count'] *= (1 - ratio)

                new_row = pd.DataFrame({
                    'ISB_Service': ['EX'],  # Assuming EX is the ID of the express bus
                    'bus_stop_board': [stop],
                    'day_of_the_week': [day],
                    'hour': [hour],
                    'minute': [minute],
                    'predicted_count': [express_demand]
                })
                adjusted_data = pd.concat([adjusted_data, new_row], ignore_index=True)
        
        _, buses_needed_per_route = optimize_buses_needed(adjusted_data, route_times, BUS_CAPACITY)
        total_buses = buses_needed_per_route['buses_needed'].sum()
        
        # Update the optimal ratio and bus count if this ratio reduces total buses
        if total_buses < min_total_buses:
            min_total_buses = total_buses
            optimal_ratio = ratio
            optimal_buses_needed = buses_needed_per_route
        ratio += increment
    return optimal_buses_needed, optimal_ratio, total_buses

if optimize:
    scores = get_priority_score(get_satisfaction_scores(day_to_sim))
    top_5 = sorted(scores, key=scores.get, reverse=True)[:5]
    st.write(f'The 5 bus stops in the express bus route are: {", ".join(top_5)}')
    optimal_buses_needed, optimal_ratio, total_buses = consider_express(predicted_demand, top_5, day_to_sim, generate_time_intervals(start_time, end_time))

    st.write(f'Optimal bus allocation:')
    st.write(optimal_buses_needed)
    st.write(f'Total number of buses needed: {total_buses}')

