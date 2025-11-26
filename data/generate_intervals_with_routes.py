"""
Generate interval data with actual Mapbox route coordinates for travel segments
Uses Mapbox Directions API to get realistic paths
"""
import json
import random
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os

# Load locations
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'locations.json'), 'r', encoding='utf-8') as f:
    locations = json.load(f)

# Mapbox token
MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN', 'pk.eyJ1Ijoia3JsdW8iLCJhIjoiY21oaWwwdTNuMTR1aTJzb242ejQybm0zYiJ9.baefOu17StTORLdFeRHMEA')

def get_route(start_lat: float, start_lon: float, end_lat: float, end_lon: float, profile: str = 'walking') -> Optional[List[List[float]]]:
    """
    Get route between two points using Mapbox Directions API
    Returns list of [lon, lat] coordinates for the route
    """
    try:
        url = f"https://api.mapbox.com/directions/v5/mapbox/{profile}/{start_lon},{start_lat};{end_lon},{end_lat}"
        params = {
            'access_token': MAPBOX_TOKEN,
            'geometries': 'geojson',
            'steps': 'true'
        }
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('routes') and len(data['routes']) > 0:
                route_coords = data['routes'][0]['geometry']['coordinates']
                return route_coords
        else:
            print(f"API error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Error getting route: {e}")
    return None

def interpolate_route_points(route_coords: List[List[float]], num_points: int) -> List[Dict]:
    """
    Interpolate route coordinates to get evenly spaced points
    Returns list of {lat, lon} dicts
    """
    if not route_coords or len(route_coords) < 2:
        return []
    
    points = []
    total_distance = 0
    segment_distances = []
    
    # Calculate cumulative distances
    for i in range(len(route_coords) - 1):
        lon1, lat1 = route_coords[i]
        lon2, lat2 = route_coords[i + 1]
        # Simple distance calculation
        dist = ((lat2 - lat1)**2 + (lon2 - lon1)**2)**0.5
        total_distance += dist
        segment_distances.append(dist)
    
    if total_distance == 0:
        return [{'lat': route_coords[0][1], 'lon': route_coords[0][0]}]
    
    # Generate evenly spaced points
    for i in range(num_points):
        target_dist = (i / (num_points - 1)) * total_distance if num_points > 1 else 0
        cumulative = 0
        for j, seg_dist in enumerate(segment_distances):
            if cumulative + seg_dist >= target_dist:
                # Interpolate within this segment
                progress = (target_dist - cumulative) / seg_dist if seg_dist > 0 else 0
                lon1, lat1 = route_coords[j]
                lon2, lat2 = route_coords[j + 1]
                points.append({
                    'lat': lat1 + (lat2 - lat1) * progress,
                    'lon': lon1 + (lon2 - lon1) * progress
                })
                break
            cumulative += seg_dist
        else:
            # Use last point
            lon, lat = route_coords[-1]
            points.append({'lat': lat, 'lon': lon})
    
    return points

# Updated locations with correct Ralphs coordinates
location_map = {
    'home': next(loc for loc in locations if loc['type'] == 'home'),
    'gym': next(loc for loc in locations if loc['name'] == 'Lyon Center'),
    'cpa': next(loc for loc in locations if loc['name'] == 'Kaprielian Hall'),
    'ralphs': {'name': 'Ralphs', 'type': 'grocery', 'latitude': 34.0260, 'longitude': -118.2843, 'address': '2600 S. Vermont Ave., Los Angeles, CA 90007'},
    'doheny': next(loc for loc in locations if loc['name'] == 'Doheny Library')
}

# Update Ralphs in locations if it exists
for loc in locations:
    if loc['name'] == 'Ralphs':
        loc['latitude'] = 34.0260
        loc['longitude'] = -118.2843

def generate_intervals_with_routes():
    """
    Generate intervals based on user schedule with actual route coordinates
    """
    intervals = []
    start_date = datetime(2024, 11, 18, 0, 0)
    
    # Sentiment ranges
    sentiment_ranges = {
        'low': (0.2, 0.5),
        'low_medium': (0.1, 0.3),
        'medium': (-0.05, 0.15),
        'high': (-0.3, -0.1),
        'fluctuate_medium_high': None  # Will alternate
    }
    
    # Schedule with travel mode
    schedule = [
        {'start': (0, 0), 'end': (7, 30), 'location': 'home', 'stress': 'low'},
        {'start': (7, 30), 'end': (8, 30), 'location': 'home', 'stress': 'low_medium'},
        {'start': (8, 30), 'end': (8, 50), 'from': 'home', 'to': 'gym', 'stress': 'medium', 'mode': 'walking'},
        {'start': (8, 50), 'end': (9, 50), 'location': 'gym', 'stress': 'high'},
        {'start': (9, 50), 'end': (10, 0), 'location': 'gym', 'stress': 'low'},
        {'start': (10, 0), 'end': (10, 20), 'from': 'gym', 'to': 'home', 'stress': 'low', 'mode': 'walking'},
        {'start': (10, 20), 'end': (12, 0), 'location': 'home', 'stress': 'low'},
        {'start': (12, 0), 'end': (12, 20), 'from': 'home', 'to': 'cpa', 'stress': 'low', 'mode': 'walking'},
        {'start': (12, 20), 'end': (14, 0), 'location': 'cpa', 'stress': 'medium'},
        {'start': (14, 0), 'end': (14, 20), 'from': 'cpa', 'to': 'home', 'stress': 'medium', 'mode': 'walking'},
        {'start': (14, 20), 'end': (15, 0), 'location': 'home', 'stress': 'low'},
        {'start': (15, 0), 'end': (15, 5), 'from': 'home', 'to': 'ralphs', 'stress': 'low', 'mode': 'driving'},
        {'start': (15, 5), 'end': (15, 40), 'location': 'ralphs', 'stress': 'low'},
        {'start': (15, 40), 'end': (15, 45), 'from': 'ralphs', 'to': 'home', 'stress': 'low', 'mode': 'driving'},
        {'start': (15, 45), 'end': (19, 0), 'location': 'home', 'stress': 'medium'},
        {'start': (19, 0), 'end': (19, 20), 'from': 'home', 'to': 'doheny', 'stress': 'low', 'mode': 'walking'},
        {'start': (19, 20), 'end': (22, 0), 'location': 'doheny', 'stress': 'fluctuate_medium_high'},
        {'start': (22, 0), 'end': (22, 20), 'from': 'doheny', 'to': 'home', 'stress': 'high', 'mode': 'walking'},
        {'start': (22, 20), 'end': (24, 0), 'location': 'home', 'stress': 'high_to_low'},
    ]
    
    route_cache = {}
    
    for segment in schedule:
        start_hour, start_min = segment['start']
        end_hour, end_min = segment['end']
        
        segment_start = start_date.replace(hour=start_hour, minute=start_min)
        if end_hour == 24:
            segment_end = start_date.replace(hour=0, minute=end_min) + timedelta(days=1)
        else:
            segment_end = start_date.replace(hour=end_hour, minute=end_min)
        
        duration_minutes = (segment_end - segment_start).total_seconds() / 60
        
        if 'from' in segment and 'to' in segment:
            # Travel segment
            from_loc = location_map[segment['from']]
            to_loc = location_map[segment['to']]
            mode = segment.get('mode', 'walking')
            profile = 'driving' if mode == 'driving' else 'walking'
            
            # Get route
            cache_key = f"{from_loc['latitude']},{from_loc['longitude']}_{to_loc['latitude']},{to_loc['longitude']}_{profile}"
            if cache_key not in route_cache:
                print(f"Getting {profile} route from {from_loc['name']} to {to_loc['name']}...")
                route = get_route(
                    from_loc['latitude'], from_loc['longitude'],
                    to_loc['latitude'], to_loc['longitude'],
                    profile=profile
                )
                route_cache[cache_key] = route
            else:
                route = route_cache[cache_key]
            
            # Generate route points
            if route and len(route) > 2:
                # Use actual route coordinates
                route_points = interpolate_route_points(route, max(3, int(duration_minutes / 2)))  # Points every ~2 minutes
            else:
                # Fallback: linear interpolation
                print(f"  No route found, using linear interpolation")
                route_points = []
                num_points = max(3, int(duration_minutes / 2))
                for i in range(num_points):
                    progress = i / (num_points - 1) if num_points > 1 else 0
                    route_points.append({
                        'lat': from_loc['latitude'] + (to_loc['latitude'] - from_loc['latitude']) * progress,
                        'lon': from_loc['longitude'] + (to_loc['longitude'] - from_loc['longitude']) * progress
                    })
            
            # Create intervals for each route point
            time_per_point = duration_minutes / len(route_points) if route_points else duration_minutes
            stress_type = segment['stress']
            
            for i, point in enumerate(route_points):
                point_start = segment_start + timedelta(minutes=i * time_per_point)
                point_end = segment_start + timedelta(minutes=(i + 1) * time_per_point)
                if i == len(route_points) - 1:
                    point_end = segment_end
                
                if stress_type in sentiment_ranges and sentiment_ranges[stress_type]:
                    sentiment = random.uniform(*sentiment_ranges[stress_type])
                else:
                    sentiment = random.uniform(-0.05, 0.15)  # Default medium
                
                intervals.append({
                    'start_time': point_start.isoformat(),
                    'end_time': point_end.isoformat(),
                    'duration_minutes': (point_end - point_start).total_seconds() / 60,
                    'latitude': point['lat'],
                    'longitude': point['lon'],
                    'location_name': 'Traveling',
                    'location_type': 'traveling',
                    'sentiment_score': round(sentiment, 2),
                    'activity': 'traveling',
                    'travel_mode': mode
                })
        else:
            # Stay segment
            loc = location_map[segment['location']]
            stress_type = segment['stress']
            
            # For fluctuating stress, alternate
            if stress_type == 'fluctuate_medium_high':
                # Alternate every 20 minutes
                num_cycles = int(duration_minutes / 20)
                for cycle in range(num_cycles):
                    cycle_start = segment_start + timedelta(minutes=cycle * 20)
                    cycle_end = min(segment_start + timedelta(minutes=(cycle + 1) * 20), segment_end)
                    is_high = cycle % 2 == 1
                    sentiment_range = (-0.3, -0.1) if is_high else (-0.05, 0.15)
                    sentiment = random.uniform(*sentiment_range)
                    
                    intervals.append({
                        'start_time': cycle_start.isoformat(),
                        'end_time': cycle_end.isoformat(),
                        'duration_minutes': (cycle_end - cycle_start).total_seconds() / 60,
                        'latitude': loc['latitude'],
                        'longitude': loc['longitude'],
                        'location_name': loc['name'],
                        'location_type': loc['type'],
                        'sentiment_score': round(sentiment, 2),
                        'activity': 'studying' if loc['type'] == 'library' else 'other'
                    })
                
                # Handle remainder
                remainder_start = segment_start + timedelta(minutes=num_cycles * 20)
                if remainder_start < segment_end:
                    is_high = num_cycles % 2 == 1
                    sentiment_range = (-0.3, -0.1) if is_high else (-0.05, 0.15)
                    sentiment = random.uniform(*sentiment_range)
                    intervals.append({
                        'start_time': remainder_start.isoformat(),
                        'end_time': segment_end.isoformat(),
                        'duration_minutes': (segment_end - remainder_start).total_seconds() / 60,
                        'latitude': loc['latitude'],
                        'longitude': loc['longitude'],
                        'location_name': loc['name'],
                        'location_type': loc['type'],
                        'sentiment_score': round(sentiment, 2),
                        'activity': 'studying' if loc['type'] == 'library' else 'other'
                    })
            elif stress_type == 'high_to_low':
                # Transition from high to low
                num_segments = max(3, int(duration_minutes / 30))
                for i in range(num_segments):
                    seg_start = segment_start + timedelta(minutes=i * (duration_minutes / num_segments))
                    seg_end = segment_start + timedelta(minutes=(i + 1) * (duration_minutes / num_segments))
                    if i == num_segments - 1:
                        seg_end = segment_end
                    
                    progress = i / (num_segments - 1) if num_segments > 1 else 0
                    if progress < 0.3:
                        sentiment = random.uniform(-0.3, -0.1)
                    elif progress < 0.6:
                        sentiment = random.uniform(-0.1, 0.1)
                    else:
                        sentiment = random.uniform(0.2, 0.5)
                    
                    intervals.append({
                        'start_time': seg_start.isoformat(),
                        'end_time': seg_end.isoformat(),
                        'duration_minutes': (seg_end - seg_start).total_seconds() / 60,
                        'latitude': loc['latitude'],
                        'longitude': loc['longitude'],
                        'location_name': loc['name'],
                        'location_type': loc['type'],
                        'sentiment_score': round(sentiment, 2),
                        'activity': 'sleep' if loc['type'] == 'home' else 'other'
                    })
            else:
                # Simple stay
                if stress_type in sentiment_ranges and sentiment_ranges[stress_type]:
                    sentiment = random.uniform(*sentiment_ranges[stress_type])
                else:
                    sentiment = random.uniform(0.2, 0.5)  # Default low
                
                intervals.append({
                    'start_time': segment_start.isoformat(),
                    'end_time': segment_end.isoformat(),
                    'duration_minutes': duration_minutes,
                    'latitude': loc['latitude'],
                    'longitude': loc['longitude'],
                    'location_name': loc['name'],
                    'location_type': loc['type'],
                    'sentiment_score': round(sentiment, 2),
                    'activity': 'sleep' if loc['type'] == 'home' and segment_start.hour < 7 else 'other'
                })
    
    # Sort by start time
    intervals.sort(key=lambda x: x['start_time'])
    
    return intervals

if __name__ == '__main__':
    print("Generating intervals with actual Mapbox routes...")
    print("This may take a minute to fetch routes from Mapbox API...")
    
    intervals = generate_intervals_with_routes()
    
    output_file = os.path.join(script_dir, 'intervals.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(intervals, f, indent=2)
    
    print(f"\nGenerated {len(intervals)} intervals")
    print(f"Date range: {intervals[0]['start_time']} to {intervals[-1]['end_time']}")
    print(f"\nSaved to: {output_file}")
    print(f"\nNote: Copy to public/intervals.json for web app")

