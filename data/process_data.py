"""
Script to process OpenStreetMap building data and generate synthetic student activity data
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict

# Load locations
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(script_dir, 'locations.json'), 'r', encoding='utf-8') as f:
    locations = json.load(f)

# Convert OSM building data to GeoJSON format
def convert_osm_to_geojson(osm_file: str, output_file: str):
    """Convert OSM building data to GeoJSON format"""
    with open(osm_file, 'r', encoding='utf-8') as f:
        osm_data = json.load(f)
    
    features = []
    for element in osm_data.get('elements', []):
        if element.get('type') == 'way' and 'geometry' in element:
            # Extract coordinates
            coords = [[point['lon'], point['lat']] for point in element['geometry']]
            
            # Close the polygon if not already closed
            if coords[0] != coords[-1]:
                coords.append(coords[0])
            
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                },
                "properties": {
                    "id": element.get('id'),
                    "tags": element.get('tags', {})
                }
            }
            features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"Converted {len(features)} buildings to GeoJSON")

# Generate synthetic time interval data
def generate_synthetic_data(start_date: str, days: int = 14) -> List[Dict]:
    """
    Generate 2 weeks of synthetic student activity data
    
    Realistic patterns:
    - Sleep: 11pm-7am at home (calm, 0.3-0.7)
    - Morning routine: 7am-9am at home (neutral, 0.0-0.3)
    - Classes: 9am-12pm, 1pm-4pm (varies, -0.1 to 0.3)
    - Library study: afternoon/evening (stressed during finals, -0.2 to 0.4)
    - Gym: varies, 30-90 min sessions (stressed during -0.3, positive after 0.5-0.8)
    - Social: evening/weekends (positive, 0.4-0.9)
    - Eating: meal times (positive, 0.2-0.7)
    - Grocery: weekend (neutral, 0.0-0.2)
    """
    intervals = []
    start = datetime.fromisoformat(start_date)
    
    # Activity sentiment ranges
    sentiment_ranges = {
        'sleep': (0.3, 0.7),
        'morning_routine': (0.0, 0.3),
        'class': (-0.1, 0.3),
        'studying': (-0.2, 0.4),
        'gym': (-0.3, 0.8),  # Can be stressed during, positive after
        'social': (0.4, 0.9),
        'eating': (0.2, 0.7),
        'grocery': (0.0, 0.2),
        'traveling': (-0.1, 0.1)
    }
    
    for day in range(days):
        current_date = start + timedelta(days=day)
        is_weekend = current_date.weekday() >= 5
        
        # Sleep: 11pm previous day to 7am
        sleep_start = current_date.replace(hour=23, minute=0, second=0)
        if day > 0:
            sleep_start = (current_date - timedelta(days=1)).replace(hour=23, minute=0, second=0)
        sleep_end = current_date.replace(hour=7, minute=0, second=0)
        home_loc = next(loc for loc in locations if loc['type'] == 'home')
        intervals.append(create_interval(
            sleep_start, sleep_end, home_loc, 
            'sleep', sentiment_ranges['sleep']
        ))
        
        # Morning routine: 7am-8:30am at home
        morning_start = current_date.replace(hour=7, minute=0, second=0)
        morning_end = current_date.replace(hour=8, minute=30, second=0)
        intervals.append(create_interval(
            morning_start, morning_end, home_loc,
            'morning_routine', sentiment_ranges['morning_routine']
        ))
        
        # Breakfast: 8:30am-9am (at home or restaurant)
        breakfast_start = current_date.replace(hour=8, minute=30, second=0)
        breakfast_end = current_date.replace(hour=9, minute=0, second=0)
        if random.random() < 0.3:  # 30% chance eat out
            restaurant = random.choice([loc for loc in locations if loc['type'] == 'restaurant'])
            intervals.append(create_interval(
                breakfast_start, breakfast_end, restaurant,
                'eating', sentiment_ranges['eating']
            ))
        else:
            intervals.append(create_interval(
                breakfast_start, breakfast_end, home_loc,
                'eating', sentiment_ranges['eating']
            ))
        
        # Classes: 9am-12pm, 1pm-4pm (weekdays only)
        if not is_weekend:
            # Morning class
            class1_start = current_date.replace(hour=9, minute=0, second=0)
            class1_end = current_date.replace(hour=12, minute=0, second=0)
            classroom = random.choice([loc for loc in locations if loc['type'] == 'classroom'])
            intervals.append(create_interval(
                class1_start, class1_end, classroom,
                'class', sentiment_ranges['class']
            ))
            
            # Lunch: 12pm-1pm
            lunch_start = current_date.replace(hour=12, minute=0, second=0)
            lunch_end = current_date.replace(hour=13, minute=0, second=0)
            if random.random() < 0.4:  # 40% chance eat out
                restaurant = random.choice([loc for loc in locations if loc['type'] == 'restaurant'])
                intervals.append(create_interval(
                    lunch_start, lunch_end, restaurant,
                    'eating', sentiment_ranges['eating']
                ))
            else:
                intervals.append(create_interval(
                    lunch_start, lunch_end, home_loc,
                    'eating', sentiment_ranges['eating']
                ))
            
            # Afternoon class
            class2_start = current_date.replace(hour=13, minute=0, second=0)
            class2_end = current_date.replace(hour=16, minute=0, second=0)
            classroom = random.choice([loc for loc in locations if loc['type'] == 'classroom'])
            intervals.append(create_interval(
                class2_start, class2_end, classroom,
                'class', sentiment_ranges['class']
            ))
        
        # Study session: varies by day
        if random.random() < 0.7:  # 70% chance of studying
            study_start_hour = random.choice([16, 17, 18])
            study_duration = random.choice([90, 120, 150, 180])  # minutes
            study_start = current_date.replace(hour=study_start_hour, minute=0, second=0)
            study_end = study_start + timedelta(minutes=study_duration)
            library = next(loc for loc in locations if loc['type'] == 'library')
            intervals.append(create_interval(
                study_start, study_end, library,
                'studying', sentiment_ranges['studying']
            ))
        
        # Gym: 30-40% chance, usually afternoon/evening
        if random.random() < 0.35:
            gym_hour = random.choice([15, 16, 17, 18, 19])
            gym_duration = random.choice([45, 60, 75, 90])  # minutes
            gym_start = current_date.replace(hour=gym_hour, minute=0, second=0)
            gym_end = gym_start + timedelta(minutes=gym_duration)
            gym_loc = next(loc for loc in locations if loc['type'] == 'gym')
            intervals.append(create_interval(
                gym_start, gym_end, gym_loc,
                'gym', sentiment_ranges['gym']
            ))
        
        # Dinner: 6pm-8pm
        dinner_start = current_date.replace(hour=18, minute=0, second=0)
        dinner_end = current_date.replace(hour=20, minute=0, second=0)
        if random.random() < 0.3:  # 30% chance eat out
            restaurant = random.choice([loc for loc in locations if loc['type'] == 'restaurant'])
            intervals.append(create_interval(
                dinner_start, dinner_end, restaurant,
                'eating', sentiment_ranges['eating']
            ))
        else:
            intervals.append(create_interval(
                dinner_start, dinner_end, home_loc,
                'eating', sentiment_ranges['eating']
            ))
        
        # Social time: evening/weekends (20-30% chance)
        if random.random() < 0.25:
            social_hour = random.choice([19, 20, 21])
            social_duration = random.choice([60, 90, 120, 180])  # minutes
            social_start = current_date.replace(hour=social_hour, minute=0, second=0)
            social_end = social_start + timedelta(minutes=social_duration)
            friend_house = next(loc for loc in locations if loc['type'] == 'friend_house')
            intervals.append(create_interval(
                social_start, social_end, friend_house,
                'social', sentiment_ranges['social']
            ))
        
        # Grocery shopping: weekend or occasional weekday
        if (is_weekend and random.random() < 0.4) or (not is_weekend and random.random() < 0.1):
            grocery_hour = random.choice([10, 11, 14, 15])
            grocery_start = current_date.replace(hour=grocery_hour, minute=0, second=0)
            grocery_end = grocery_start + timedelta(minutes=random.choice([30, 45, 60]))
            grocery = next(loc for loc in locations if loc['type'] == 'grocery')
            intervals.append(create_interval(
                grocery_start, grocery_end, grocery,
                'grocery', sentiment_ranges['grocery']
            ))
    
    # Sort by start time
    intervals.sort(key=lambda x: x['start_time'])
    return intervals

def create_interval(start: datetime, end: datetime, location: Dict, 
                   activity: str, sentiment_range: tuple) -> Dict:
    """Create a single time interval entry"""
    duration_minutes = int((end - start).total_seconds() / 60)
    sentiment = round(random.uniform(*sentiment_range), 2)
    
    return {
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "location_name": location['name'],
        "location_type": location['type'],
        "latitude": location['latitude'],
        "longitude": location['longitude'],
        "sentiment_score": sentiment,
        "activity": activity,
        "duration_minutes": duration_minutes
    }

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Convert OSM to GeoJSON
    print("Converting OSM building data to GeoJSON...")
    osm_file = os.path.join(script_dir, 'buildings_usc.json')
    geojson_file = os.path.join(script_dir, 'buildings_usc.geojson')
    convert_osm_to_geojson(osm_file, geojson_file)
    
    # Generate synthetic data (2 weeks starting from a Monday)
    print("Generating synthetic student activity data...")
    # Start from a recent Monday
    start_date = "2024-11-18T00:00:00"  # Adjust as needed
    intervals = generate_synthetic_data(start_date, days=14)
    
    intervals_file = os.path.join(script_dir, 'intervals.json')
    with open(intervals_file, 'w', encoding='utf-8') as f:
        json.dump(intervals, f, indent=2)
    
    print(f"Generated {len(intervals)} time intervals")
    print(f"Date range: {intervals[0]['start_time']} to {intervals[-1]['end_time']}")
    print(f"\nNote: Copy processed files to public/ folder for web app:")
    print(f"  - intervals.json")
    print(f"  - locations.json")
    print(f"  - buildings_usc.geojson")

