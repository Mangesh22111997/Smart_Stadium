"""
Seed test events into Firebase Realtime Database
"""

from app.config.firebase_config import get_db_connection
import datetime

def seed_test_events():
    """Create sample events in Firebase"""
    
    db = get_db_connection()
    
    events = [
        {
            "event_name": "Rock Concert 2026",
            "event_date": "2026-05-15",
            "start_time": "18:00",
            "end_time": "23:00",
            "venue_type": "Concert",
            "description": "Experience the best rock bands performing live at Smart Stadium. A night full of energy and excitement!",
            "seating_capacity": 5000,
            "available_seats": 3500,
            "price_per_ticket": 500,
            "number_of_gates": 5,
            "parking_available": True,
            "food_available": True,
            "wifi_available": True,
            "status": "active",
            "created_at": datetime.datetime.now().isoformat()
        },
        {
            "event_name": "Cricket World Cup Qualifier",
            "event_date": "2026-06-01",
            "start_time": "14:00",
            "end_time": "20:00",
            "venue_type": "Sports",
            "description": "Witness high-octane cricket action as teams battle for supremacy. Don't miss this thrilling match!",
            "seating_capacity": 10000,
            "available_seats": 4200,
            "price_per_ticket": 1000,
            "number_of_gates": 8,
            "parking_available": True,
            "food_available": True,
            "wifi_available": True,
            "status": "active",
            "created_at": datetime.datetime.now().isoformat()
        },
        {
            "event_name": "Comedy Night Live",
            "event_date": "2026-05-25",
            "start_time": "19:00",
            "end_time": "21:30",
            "venue_type": "Concert",
            "description": "Laugh till your belly hurts with the funniest comedians in town. An evening of pure entertainment!",
            "seating_capacity": 3000,
            "available_seats": 1200,
            "price_per_ticket": 400,
            "number_of_gates": 4,
            "parking_available": True,
            "food_available": True,
            "wifi_available": True,
            "status": "active",
            "created_at": datetime.datetime.now().isoformat()
        },
        {
            "event_name": "Tech Conference 2026",
            "event_date": "2026-06-10",
            "start_time": "09:00",
            "end_time": "18:00",
            "venue_type": "Conference",
            "description": "Join industry leaders and innovators for the biggest tech conference of the year. Discover the future!",
            "seating_capacity": 8000,
            "available_seats": 5300,
            "price_per_ticket": 1500,
            "number_of_gates": 6,
            "parking_available": True,
            "food_available": True,
            "wifi_available": True,
            "status": "active",
            "created_at": datetime.datetime.now().isoformat()
        },
        {
            "event_name": "Basketball Championship",
            "event_date": "2026-07-05",
            "start_time": "17:00",
            "end_time": "22:00",
            "venue_type": "Sports",
            "description": "Watch the most competitive basketball championship with international teams. Non-stop action!",
            "seating_capacity": 7000,
            "available_seats": 2100,
            "price_per_ticket": 800,
            "number_of_gates": 6,
            "parking_available": True,
            "food_available": True,
            "wifi_available": True,
            "status": "active",
            "created_at": datetime.datetime.now().isoformat()
        },
        {
            "event_name": "Music Festival 2026",
            "event_date": "2026-08-15",
            "start_time": "12:00",
            "end_time": "23:59",
            "venue_type": "Concert",
            "description": "A complete day of music featuring 50+ artists across multiple genres. The ultimate music experience!",
            "seating_capacity": 15000,
            "available_seats": 8900,
            "price_per_ticket": 600,
            "number_of_gates": 8,
            "parking_available": True,
            "food_available": True,
            "wifi_available": True,
            "status": "active",
            "created_at": datetime.datetime.now().isoformat()
        },
        {
            "event_name": "Film Festival 2026",
            "event_date": "2026-07-20",
            "start_time": "10:00",
            "end_time": "22:00",
            "venue_type": "Workshop",
            "description": "Celebrate cinema with premiere screenings of award-winning and indie films. A cinephile's heaven!",
            "seating_capacity": 4500,
            "available_seats": 1800,
            "price_per_ticket": 350,
            "number_of_gates": 4,
            "parking_available": True,
            "food_available": True,
            "wifi_available": True,
            "status": "active",
            "created_at": datetime.datetime.now().isoformat()
        },
        {
            "event_name": "Marathon 2026",
            "event_date": "2026-09-01",
            "start_time": "05:00",
            "end_time": "12:00",
            "venue_type": "Sports",
            "description": "Run for a cause! Join thousands of runners in the annual marathon. Every step counts!",
            "seating_capacity": 50000,
            "available_seats": 35000,
            "price_per_ticket": 200,
            "number_of_gates": 10,
            "parking_available": True,
            "food_available": True,
            "wifi_available": True,
            "status": "active",
            "created_at": datetime.datetime.now().isoformat()
        }
    ]
    
    print("🌱 Seeding test events...")
    
    try:
        events_ref = db.child("events").get()
        existing_event_count = len(events_ref.val()) if events_ref.val() else 0
        print(f"📊 Existing events: {existing_event_count}")
        
        created_count = 0
        for i, event in enumerate(events, 1):
            # Generate event_id based on event name
            event_id = f"event_{i:02d}_{event['event_name'].replace(' ', '_').lower()}"
            
            db.child("events").child(event_id).set(event)
            print(f"✅ Event {i}/{len(events)} created: {event['event_name']}")
            created_count += 1
        
        print(f"\n🎉 Successfully created {created_count} test events!")
        print(f"📊 Total events in database: {existing_event_count + created_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error seeding events: {str(e)}")
        return False

if __name__ == "__main__":
    seed_test_events()
