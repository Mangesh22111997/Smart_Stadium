"""
Google Maps Helper - Stadium mapping utilities
Creates interactive stadium maps with gates, parking, transit
"""

import folium
from folium import plugins
import streamlit as st
from typing import Dict, List, Tuple

class StadiumMapHelper:
    """Generate stadium maps using Folium"""
    
    # Stadium center coordinates (example)
    STADIUM_LAT = 28.5244
    STADIUM_LNG = 77.1855
    
    # Gate positions (relative to stadium center)
    GATES = {
        "Gate A": (28.5250, 77.1850),
        "Gate B": (28.5260, 77.1860),
        "Gate C": (28.5240, 77.1870),
        "Gate D": (28.5230, 77.1860),
        "Gate E": (28.5240, 77.1840),
    }
    
    # Parking areas
    PARKING = {
        "Parking North": (28.5270, 77.1855),
        "Parking South": (28.5220, 77.1855),
        "Parking East": (28.5245, 77.1890),
        "Parking West": (28.5245, 77.1820),
    }
    
    # Public transport nearby
    METRO_STATIONS = {
        "Metro Station A": (28.5300, 77.1900),
        "Metro Station B": (28.5180, 77.1800),
    }
    
    BUS_STOPS = {
        "Bus Stop 1": (28.5250, 77.1900),
        "Bus Stop 2": (28.5250, 77.1810),
        "Bus Stop 3": (28.5330, 77.1855),
    }
    
    @staticmethod
    def create_stadium_map(highlighted_gate: str = None) -> folium.Map:
        """Create main stadium map with all features"""
        
        # Base map centered on stadium
        m = folium.Map(
            location=[StadiumMapHelper.STADIUM_LAT, StadiumMapHelper.STADIUM_LNG],
            zoom_start=15,
            tiles="OpenStreetMap"
        )
        
        # Add stadium marker
        folium.Marker(
            location=[StadiumMapHelper.STADIUM_LAT, StadiumMapHelper.STADIUM_LNG],
            popup="<b>Smart Stadium</b><br>Main Event Venue",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
        
        # Add gate markers
        for gate_name, (lat, lng) in StadiumMapHelper.GATES.items():
            color = "red" if gate_name == highlighted_gate else "green"
            icon = "exclamation-sign" if gate_name == highlighted_gate else "info-sign"
            
            folium.Marker(
                location=[lat, lng],
                popup=f"<b>{gate_name}</b><br>Entry/Exit Point",
                icon=folium.Icon(color=color, icon=icon)
            ).add_to(m)
        
        # Add parking areas
        for parking_name, (lat, lng) in StadiumMapHelper.PARKING.items():
            folium.Marker(
                location=[lat, lng],
                popup=f"<b>{parking_name}</b>",
                icon=folium.Icon(color="orange", icon="car")
            ).add_to(m)
        
        # Add metro stations
        for metro_name, (lat, lng) in StadiumMapHelper.METRO_STATIONS.items():
            folium.Marker(
                location=[lat, lng],
                popup=f"<b>{metro_name}</b>",
                icon=folium.Icon(color="purple", icon="train")
            ).add_to(m)
        
        # Add bus stops
        for bus_name, (lat, lng) in StadiumMapHelper.BUS_STOPS.items():
            folium.Marker(
                location=[lat, lng],
                popup=f"<b>{bus_name}</b>",
                icon=folium.Icon(color="blue", icon="bus")
            ).add_to(m)
        
        # Add legend
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; right: 50px; width: 200px; height: 220px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
            <p style="margin: 0;"><b>Stadium Map Legend</b></p>
            <p style="margin: 5px 0;"><i class="fa fa-map-marker" style="color:blue"></i> Stadium</p>
            <p style="margin: 5px 0;"><i class="fa fa-map-marker" style="color:green"></i> Gate (Available)</p>
            <p style="margin: 5px 0;"><i class="fa fa-map-marker" style="color:red"></i> Gate (Highlighted)</p>
            <p style="margin: 5px 0;"><i class="fa fa-map-marker" style="color:orange"></i> Parking</p>
            <p style="margin: 5px 0;"><i class="fa fa-map-marker" style="color:purple"></i> Metro</p>
            <p style="margin: 5px 0;"><i class="fa fa-map-marker" style="color:blue"></i> Bus Stop</p>
        </div>
        '''
        m.get_root().html.add_child(folium.Element(legend_html))
        
        return m
    
    @staticmethod
    def create_gate_detail_map(gate_name: str, gate_lat: float, gate_lng: float) -> folium.Map:
        """Create detailed map for specific gate"""
        
        m = folium.Map(
            location=[gate_lat, gate_lng],
            zoom_start=16,
            tiles="OpenStreetMap"
        )
        
        # Gate location
        folium.Marker(
            location=[gate_lat, gate_lng],
            popup=f"<b>{gate_name}</b><br>Entry Point",
            icon=folium.Icon(color="red", icon="exclamation-sign"),
            prefix="fa"
        ).add_to(m)
        
        # Nearby parking
        folium.Circle(
            location=[gate_lat, gate_lng],
            radius=200,
            color="orange",
            fill=True,
            fillColor="orange",
            fillOpacity=0.2,
            popup="Nearby Parking"
        ).add_to(m)
        
        # Accessible routes
        folium.Circle(
            location=[gate_lat, gate_lng],
            radius=100,
            color="green",
            fill=True,
            fillColor="green",
            fillOpacity=0.1,
            popup="Accessible Area"
        ).add_to(m)
        
        return m
    
    @staticmethod
    def get_directions_text(from_location: str, to_location: str = "Stadium") -> str:
        """Generate text directions"""
        
        directions_map = {
            ("Metro Station A", "Stadium"): """
            📍 **Directions from Metro Station A to Stadium:**
            1. Exit Metro Station A
            2. Head South on Market Street for 200m
            3. Turn Right on Stadium Road
            4. Continue for 300m
            5. Arrive at **Gate B** entrance
            ⏱️ Time: ~10 minutes walk
            """,
            
            ("Bus Stop 1", "Stadium"): """
            📍 **Directions from Bus Stop 1 to Stadium:**
            1. Exit Bus Stop 1
            2. Head West on Main Avenue
            3. Turn Left on Stadium Lane
            4. Continue for 150m
            5. Arrive at **Gate A** entrance
            ⏱️ Time: ~5 minutes walk
            """,
            
            ("Parking North", "Stadium"): """
            📍 **Directions from Parking North to Stadium:**
            1. Exit Parking North
            2. Head South towards stadium
            3. Follow signs to nearest gate
            4. Proceed via **Gate A** or **Gate B**
            ⏱️ Time: ~15 minutes walk
            """,
        }
        
        key = (from_location, to_location)
        return directions_map.get(key, f"Navigate from {from_location} to {to_location}")
    
    @staticmethod
    def get_commute_estimates(from_location: str) -> Dict[str, str]:
        """Get travel time estimates"""
        
        estimates = {
            "Metro Station A": "12 minutes",
            "Metro Station B": "18 minutes",
            "Bus Stop 1": "7 minutes",
            "Bus Stop 2": "10 minutes",
            "Bus Stop 3": "14 minutes",
            "Parking North": "15 minutes",
            "Parking South": "12 minutes",
            "Parking East": "18 minutes",
            "Parking West": "17 minutes",
        }
        
        return {
            "travel_mode": "Walking",
            "estimated_time": estimates.get(from_location, "20 minutes"),
            "distance": "~1.2 km",
            "crowding": "Moderate"
        }
    
    @staticmethod
    def create_parking_utilization_map(utilization: Dict[str, float]) -> folium.Map:
        """Create map showing parking availability"""
        
        m = folium.Map(
            location=[StadiumMapHelper.STADIUM_LAT, StadiumMapHelper.STADIUM_LNG],
            zoom_start=14,
            tiles="OpenStreetMap"
        )
        
        # Add parking with color based on occupancy
        for parking_name, (lat, lng) in StadiumMapHelper.PARKING.items():
            occupancy = utilization.get(parking_name, 0)
            
            if occupancy > 80:
                color = "red"
                popup_text = "Almost Full"
            elif occupancy > 50:
                color = "orange"
                popup_text = "Moderately Full"
            else:
                color = "green"
                popup_text = "Many Spaces Available"
            
            folium.CircleMarker(
                location=[lat, lng],
                radius=15,
                popup=f"<b>{parking_name}</b><br>{popup_text}<br>Occupancy: {occupancy}%",
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.7
            ).add_to(m)
        
        return m
