"""
Google Maps Helper - Stadium mapping utilities
Creates interactive stadium maps with gates, parking, transit
"""

class StadiumMapHelper:
    """Generate stadium maps using Google Maps Embed"""
    
    # Stadium center coordinates (Jawaharlal Nehru Stadium, Delhi as example)
    STADIUM_LAT = 28.5828
    STADIUM_LNG = 77.2344
    
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
    def get_embed_url(lat: float, lng: float, zoom: int = 15) -> str:
        """Generate Google Maps Embed URL (Free version)"""
        return f"https://maps.google.com/maps?q={lat},{lng}&z={zoom}&output=embed"
    
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
    def get_commute_estimates(from_location: str) -> dict:
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
