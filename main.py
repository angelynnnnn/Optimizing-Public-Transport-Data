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
import polyline


# STREAMLIT APP

# To run this, run "streamlit run main.py" in terminal (ensure streamlit is installed locally)

@st.cache_data
def get_bus_stops():
    bus_stops = pd.read_csv('bus_stop_coords.csv', header=None)
    bus_stops.rename(columns={0:"Bus Stop", 1:"lat", 2:"lon"}, inplace=True)

    return bus_stops

bus_stops = get_bus_stops()
MAP_CENTER = [1.3083003040174188, 103.79569430095988]
KR_CENTER = [1.29782, 103.77711]

st.header("NUS Internal Shuttle Bus Service")
times = list(pd.date_range(start="07:00", end="23:00", freq="10min").time)
time_to_show = st.select_slider(label='Time', options=times)
bus_service = st.selectbox(label="Bus Service", options=['A1', 'A2', 'D1', 'D2', 'BTC', 'E', 'K'])

# Routes
A1_bus = ['KR Bus Terminal', 'LT13', 'AS5', 'BIZ2', 'Opp TCOMS', 'PGP Terminal', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'YIH', 'CLB', 'KR Bus Terminal']
A2_bus = ['KR Bus Terminal', 'IT', 'Opp YIH', 'Museum', 'UHC', 'Opp University Hall', 'S17', 'Opp KR MRT', 'PGP Foyer', 'TCOMS', 'Opp HSSML', 'Opp NUSS', 'Ventus', 'KR Bus Terminal']
D1_bus = ['COM3', 'Opp HSSML', 'Opp NUSS', 'Ventus', 'IT', 'Opp YIH', 'Museum', 'UTown', 'YIH', 'CLB', 'LT13', 'AS5', 'BIZ2', 'COM3']
D2_bus = ['COM3', 'Opp TCOMS', 'PGP Terminal', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'Museum', 'UTown', 'UHC', 'Opp University Hall', 'S17', 'Opp KR MRT', 'PGP Foyer', 'TCOMS', 'COM3']
BTC_bus = ['Oei Tiong Ham Building (BTC)', 'Botanic Gardens MRT (BTC)', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'UTown', 'Raffles Hall', 'Kent Vale', 'Museum', 'YIH', 'CLB', 'LT13', 'AS5', 'BIZ2', 'PGP Terminal', 'College Green (BTC)', 'Oei Tiong Ham Building (BTC)']
E_bus = ['UTown', 'Raffles Hall', 'Kent Vale', 'EA', 'SDE3', 'IT', 'Opp YIH', 'UTown']
K_bus = ['PGP Terminal', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'YIH', 'CLB', 'Opp SDE3', 'The Japanese Primary School', 'Kent Vale', 'Museum', 'UHC', 'Opp University Hall', 'S17', 'Opp KR MRT', 'PGP Foyer']
L_bus = ['Oei Tiong Ham Building (BTC)', 'Botanic Gardents MRT (BTC)', 'College Green (BTC)', 'Oei Tiong Ham Building (BTC)']

bus_routes = {'A1':A1_bus, 'A2':A2_bus, 'D1':D1_bus, 'D2':D2_bus, 'BTC':BTC_bus, 'E':E_bus, 'K':K_bus, 'L':L_bus}

MAPBOX_API = 'pk.eyJ1IjoiZ3VvaG9uZ3lpMTExIiwiYSI6ImNtMng0OHc4cTAwenMybG9iczg4cjBoNjcifQ.tc6o1kU_mTemKQhbVy5mNA'

@st.cache_data
def bus_service_data(bus):
    route = bus_routes[bus]

    stops = bus_stops[bus_stops['Bus Stop'].isin(route)]
    route_df = pd.DataFrame({'Bus Stop': route})
    route_df['route_index'] = route_df.index
    bus_df = route_df.merge(stops, on='Bus Stop', how='left')
    bus_df.loc[bus_df['route_index']==0, 'color'] = 'red'
    bus_df.loc[bus_df['route_index']!=0, 'color'] = 'blue'
    bus_df.loc[bus_df['route_index']==bus_df.shape[0]-1, 'color'] = 'red'
    bus_df.drop(columns='route_index', inplace=True)

    return bus_df

def route_map(bus):
    bus_df = bus_service_data(bus)

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

        route_coords = [list(reversed(coord)) for coord in direction['routes'][0]['geometry']['coordinates']]
        folium.PolyLine(locations=route_coords,
                color='blue',
                weight=3,
                smooth_factor=0.1).add_to(map)
        
    # Show demand for each bus stop
    global time_to_show

    
        
    return bus_df, map

st_folium(route_map(bus_service)[1], width=800)


# SIMULATION

st.subheader("Simulation")
col1, col2 = st.columns(2)

with col1:
    sim_bus_service = st.selectbox(label="Bus Service", options=['A1', 'A2', 'D1', 'D2', 'BTC', 'E', 'K'], key='sim')
with col2:
    num_buses = st.number_input('Number of buses', 1, 8)

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

# Sample bus schedule for each bus
bus_timings = {}
for bus in bus_freq.keys():
    bus_timings[bus] = []
    for t in range(len(bus_freq[bus])):
        times = pd.date_range(start=bus_freq[bus][t][0], end=bus_freq[bus][t][1], freq=bus_freq[bus][t][2]).time.tolist()
        if times[0] in bus_timings[bus]:
            times = times[1:]

        bus_timings[bus] += times

# Simulating bus schedule
BUS_CAPACITY = 88
queue_buses = [i+1 for i in range(num_buses)] # so that buses leave the terminal sequentially
sim_log = [] # store the strings of outputs

sim_bus_timings = pd.DataFrame(bus_timings[sim_bus_service], columns=['depart_time'])

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

def bus_route(env, bus_id, bus_df):
        
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

    env.process(bus_departure(env, sim_bus_timings))
    
    env.run(until=end_time)


if start_sim:
    main_sim()

unavailable_count = sum(1 for s in sim_log if 'available' in s)
total_trips = len(sim_bus_timings)

st.text_area("Simulation Log", "\n".join(sim_log), height=500)
st.write(f'Number of trips not done: {unavailable_count}')
st.write(f'Total number of trips: {total_trips}')


# SIMULATION OF CREATED ROUTES

bus_stops_names = bus_stops.loc[:, 'Bus Stop']

if 'available_options' not in st.session_state:
    st.session_state['available_options'] = bus_stops_names
if 'selected_options' not in st.session_state:
    st.session_state['selected_options'] = []

st.session_state['selected_options'] = st.multiselect(label='Create a route:', options=st.session_state['available_options'], default=st.session_state['selected_options'], 
                              placeholder='Choose bus stops')

@st.cache_data
def create_simulated_route(stops):
    chosen_stops_df = bus_stops[bus_stops['Bus Stop'].isin(stops)]
    chosen_stops_df['coordinates'] = chosen_stops_df['lon'].astype(str) + "," + chosen_stops_df['lat'].astype(str)
    all_coords = ';'.join(chosen_stops_df['coordinates'])

    sim_url = f"https://api.mapbox.com/optimized-trips/v1/mapbox/driving/{all_coords}?roundtrip=false&source=first&destination=last&access_token={MAPBOX_API}"
    response = requests.get(sim_url)
    directions = response.json()
    optimized_route = directions['trips'][0]['geometry']
    markers_in_order = pd.DataFrame({'coords': [list(reversed(wp['location'])) for wp in directions['waypoints']],
                        'order': [wp['waypoint_index'] for wp in directions['waypoints']]})

    # Plot optimized route onto map
    decoded_route = polyline.decode(optimized_route)
    # start = decoded_route[0]
    map = folium.Map(location=KR_CENTER, zoom_start=15)
    folium.PolyLine(decoded_route, weight=3).add_to(map)

    for i in range(len(markers_in_order)):
        folium.Marker(markers_in_order.loc[i, 'coords'], popup=f"Waypoint {i+1}").add_to(map)

    return map

st.write("Note: The first stop chosen will be the starting stop, and the last stop chosen will be the destination.")

chosen_stops = st.session_state['selected_options']

if len(chosen_stops) >= 2:
    st_folium(create_simulated_route(chosen_stops), width=800)
else:
    st.write('Please choose a minimum of 2 stops and maximum of 12 stops.')