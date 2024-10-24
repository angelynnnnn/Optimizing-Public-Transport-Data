import pandas as pd
from sdv.constraints import create_custom_constraint_class

A1_bus = ['KR Bus Terminal', 'LT13', 'AS5', 'BIZ2', 'Opp TCOMS', 'PGP Terminal', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'YIH', 'CLB', 'KR Bus Terminal']
A2_bus = ['KR Bus Terminal', 'IT', 'Opp YIH', 'Museum', 'UHC', 'Opp University Hall', 'S17', 'Opp KR MRT', 'PGP Foyer', 'TCOMS', 'Opp HSSML', 'Opp NUSS', 'Ventus', 'KR Bus Terminal']
D1_bus = ['COM3', 'Opp HSSML', 'Opp NUSS', 'Ventus', 'IT', 'Opp YIH', 'Museum', 'UTown', 'YIH', 'CLB', 'LT13', 'AS5', 'BIZ2', 'COM3']
D2_bus = ['COM3', 'Opp TCOMS', 'PGP Terminal', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'Museum', 'UTown', 'UHC', 'Opp University Hall', 'S17', 'Opp KR MRT', 'PGP Foyer', 'TCOMS', 'COM3']
BTC_bus = ['Oei Tiong Ham Building (BTC)', 'Botanic Gardens MRT (BTC)', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'UTown', 'Raffles Hall', 'Kent Vale', 'Museum', 'YIH', 'CLB', 'LT13', 'AS5', 'BIZ2', 'PGP Terminal', 'College Green (BTC)', 'Oei Tiong Ham Building (BTC)']
E_bus = ['UTown', 'Raffles Hall', 'Kent Vale', 'EA', 'SDE3', 'IT', 'Opp YIH', 'UTown']
K_bus = ['PGP Terminal', 'KR MRT', 'LT27', 'University Hall', 'Opp UHC', 'YIH', 'CLB', 'Opp SDE3', 'The Japanese Primary School', 'Kent Vale', 'Museum', 'University Health Centre', 'Opp University Hall', 'S17', 'Opp KR MRT', 'PGP Foyer']
L_bus = ['Oei Tiong Ham Building (BTC)', 'Botanic Gardents MRT (BTC)', 'College Green (BTC)', 'Oei Tiong Ham Building (BTC)']

bus_routes = {'A1': A1_bus, 'A2':A2_bus, 'D1': D1_bus, 'D2': D2_bus, 'BTC (Bukit Timah Campus)': BTC_bus, 'E': E_bus, 'K': K_bus, 'L': L_bus}

# def valid_trip(row):
#     bus = row['ISB_Service']
#     start = row['bus_stop_board']
#     end = row['bus_stop_alight']

#     route = bus_routes.get(bus, [])

#     if start in route and end in route:
#         start_index = route.index(start)
#         end_index = route.index(end)
#         if end_index == 0: # buses that loop back to the start
#             end_index = len(route)
        
#         return start_index < end_index
    
#     else:
#         return False

# def is_valid(column_names, data):
#     data[column_names[0]] = data.apply(valid_trip, axis=1)
#     return data[column_names[0]]

def valid_route(column_names, data):
    def check_route(row):
        bus = row[column_names[0]]
        start = row[column_names[1]]
        end = row[column_names[2]]

        route = bus_routes[bus]

        if start in route and end in route:
            start_index = route.index(start)
            end_index = route.index(end)
            if end_index == 0: # for routes that loop back
                end_index = len(route)
            
            return start_index < end_index
        
        return False
    
    return data.apply(check_route, axis=1)

def valid_time(column_names, data):
    def check_time(row):
        time_str = row[column_names[0]]
        time = pd.to_datetime(time_str, format='%I:%M:%S %p').time()

        if (pd.to_datetime('07:00:00 AM', format='%I:%M:%S %p').time() <= time)  or (time <= pd.to_datetime('11:00:00 PM', format='%I:%M:%S %p').time()):
            return True
        else:
            return False

    return data.apply(check_time, axis=1)

def transform(column_names, data):
    return data

def reverse_transform(column_names, data):
    return data

BusStopsCheck = create_custom_constraint_class(
    is_valid_fn = valid_route,
    transform_fn = transform,
    reverse_transform_fn = reverse_transform
    )

TimeCheck = create_custom_constraint_class(
    is_valid_fn = valid_time,
    transform_fn = transform,
    reverse_transform_fn = reverse_transform
)