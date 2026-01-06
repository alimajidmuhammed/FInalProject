"""
Airport Service - Provides airport data and fuzzy search functionality.
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from rapidfuzz import fuzz, process

from config import ASSETS_DIR


class AirportService:
    """Manages airport data with fuzzy search capabilities."""
    
    def __init__(self):
        """Initialize airport service and load data."""
        self.airports: List[Dict] = []
        self.airports_by_code: Dict[str, Dict] = {}
        self._load_airports()
    
    def _load_airports(self):
        """Load airports from JSON file."""
        airports_file = ASSETS_DIR / "airports.json"
        
        if airports_file.exists():
            with open(airports_file, 'r', encoding='utf-8') as f:
                self.airports = json.load(f)
        else:
            # Use built-in major airports if file doesn't exist
            self.airports = self._get_default_airports()
            # Save for future use
            self._save_airports()
        
        # Build lookup by IATA code
        for airport in self.airports:
            if airport.get('iata'):
                self.airports_by_code[airport['iata']] = airport
    
    def _save_airports(self):
        """Save airports to JSON file."""
        airports_file = ASSETS_DIR / "airports.json"
        ASSETS_DIR.mkdir(parents=True, exist_ok=True)
        with open(airports_file, 'w', encoding='utf-8') as f:
            json.dump(self.airports, f, indent=2, ensure_ascii=False)
    
    def _get_default_airports(self) -> List[Dict]:
        """Return a comprehensive list of default airports."""
        return [
            # Middle East
            {"name": "Baghdad International Airport", "city": "Baghdad", "country": "Iraq", "iata": "BGW"},
            {"name": "Erbil International Airport", "city": "Erbil", "country": "Iraq", "iata": "EBL"},
            {"name": "Sulaimaniyah International Airport", "city": "Sulaimaniyah", "country": "Iraq", "iata": "ISU"},
            {"name": "Basra International Airport", "city": "Basra", "country": "Iraq", "iata": "BSR"},
            {"name": "Najaf International Airport", "city": "Najaf", "country": "Iraq", "iata": "NJF"},
            {"name": "Dubai International Airport", "city": "Dubai", "country": "United Arab Emirates", "iata": "DXB"},
            {"name": "Abu Dhabi International Airport", "city": "Abu Dhabi", "country": "United Arab Emirates", "iata": "AUH"},
            {"name": "Sharjah International Airport", "city": "Sharjah", "country": "United Arab Emirates", "iata": "SHJ"},
            {"name": "Doha Hamad International Airport", "city": "Doha", "country": "Qatar", "iata": "DOH"},
            {"name": "King Abdulaziz International Airport", "city": "Jeddah", "country": "Saudi Arabia", "iata": "JED"},
            {"name": "King Khalid International Airport", "city": "Riyadh", "country": "Saudi Arabia", "iata": "RUH"},
            {"name": "Kuwait International Airport", "city": "Kuwait City", "country": "Kuwait", "iata": "KWI"},
            {"name": "Bahrain International Airport", "city": "Manama", "country": "Bahrain", "iata": "BAH"},
            {"name": "Muscat International Airport", "city": "Muscat", "country": "Oman", "iata": "MCT"},
            {"name": "Queen Alia International Airport", "city": "Amman", "country": "Jordan", "iata": "AMM"},
            {"name": "Beirut Rafic Hariri International Airport", "city": "Beirut", "country": "Lebanon", "iata": "BEY"},
            {"name": "Ben Gurion Airport", "city": "Tel Aviv", "country": "Israel", "iata": "TLV"},
            {"name": "Imam Khomeini International Airport", "city": "Tehran", "country": "Iran", "iata": "IKA"},
            
            # Turkey
            {"name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey", "iata": "IST"},
            {"name": "Sabiha Gokcen International Airport", "city": "Istanbul", "country": "Turkey", "iata": "SAW"},
            {"name": "Antalya Airport", "city": "Antalya", "country": "Turkey", "iata": "AYT"},
            {"name": "Ankara Esenboga Airport", "city": "Ankara", "country": "Turkey", "iata": "ESB"},
            
            # Europe
            {"name": "London Heathrow Airport", "city": "London", "country": "United Kingdom", "iata": "LHR"},
            {"name": "London Gatwick Airport", "city": "London", "country": "United Kingdom", "iata": "LGW"},
            {"name": "Manchester Airport", "city": "Manchester", "country": "United Kingdom", "iata": "MAN"},
            {"name": "Paris Charles de Gaulle Airport", "city": "Paris", "country": "France", "iata": "CDG"},
            {"name": "Paris Orly Airport", "city": "Paris", "country": "France", "iata": "ORY"},
            {"name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany", "iata": "FRA"},
            {"name": "Munich Airport", "city": "Munich", "country": "Germany", "iata": "MUC"},
            {"name": "Berlin Brandenburg Airport", "city": "Berlin", "country": "Germany", "iata": "BER"},
            {"name": "Amsterdam Schiphol Airport", "city": "Amsterdam", "country": "Netherlands", "iata": "AMS"},
            {"name": "Madrid Barajas Airport", "city": "Madrid", "country": "Spain", "iata": "MAD"},
            {"name": "Barcelona El Prat Airport", "city": "Barcelona", "country": "Spain", "iata": "BCN"},
            {"name": "Rome Fiumicino Airport", "city": "Rome", "country": "Italy", "iata": "FCO"},
            {"name": "Milan Malpensa Airport", "city": "Milan", "country": "Italy", "iata": "MXP"},
            {"name": "Vienna International Airport", "city": "Vienna", "country": "Austria", "iata": "VIE"},
            {"name": "Zurich Airport", "city": "Zurich", "country": "Switzerland", "iata": "ZRH"},
            {"name": "Geneva Airport", "city": "Geneva", "country": "Switzerland", "iata": "GVA"},
            {"name": "Brussels Airport", "city": "Brussels", "country": "Belgium", "iata": "BRU"},
            {"name": "Copenhagen Airport", "city": "Copenhagen", "country": "Denmark", "iata": "CPH"},
            {"name": "Stockholm Arlanda Airport", "city": "Stockholm", "country": "Sweden", "iata": "ARN"},
            {"name": "Oslo Gardermoen Airport", "city": "Oslo", "country": "Norway", "iata": "OSL"},
            {"name": "Helsinki Vantaa Airport", "city": "Helsinki", "country": "Finland", "iata": "HEL"},
            {"name": "Dublin Airport", "city": "Dublin", "country": "Ireland", "iata": "DUB"},
            {"name": "Lisbon Portela Airport", "city": "Lisbon", "country": "Portugal", "iata": "LIS"},
            {"name": "Athens International Airport", "city": "Athens", "country": "Greece", "iata": "ATH"},
            {"name": "Warsaw Chopin Airport", "city": "Warsaw", "country": "Poland", "iata": "WAW"},
            {"name": "Prague Vaclav Havel Airport", "city": "Prague", "country": "Czech Republic", "iata": "PRG"},
            {"name": "Budapest Ferenc Liszt Airport", "city": "Budapest", "country": "Hungary", "iata": "BUD"},
            {"name": "Moscow Sheremetyevo Airport", "city": "Moscow", "country": "Russia", "iata": "SVO"},
            
            # Asia
            {"name": "Beijing Capital International Airport", "city": "Beijing", "country": "China", "iata": "PEK"},
            {"name": "Shanghai Pudong International Airport", "city": "Shanghai", "country": "China", "iata": "PVG"},
            {"name": "Hong Kong International Airport", "city": "Hong Kong", "country": "Hong Kong", "iata": "HKG"},
            {"name": "Tokyo Narita International Airport", "city": "Tokyo", "country": "Japan", "iata": "NRT"},
            {"name": "Tokyo Haneda Airport", "city": "Tokyo", "country": "Japan", "iata": "HND"},
            {"name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore", "iata": "SIN"},
            {"name": "Bangkok Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand", "iata": "BKK"},
            {"name": "Kuala Lumpur International Airport", "city": "Kuala Lumpur", "country": "Malaysia", "iata": "KUL"},
            {"name": "Seoul Incheon International Airport", "city": "Seoul", "country": "South Korea", "iata": "ICN"},
            {"name": "Delhi Indira Gandhi International Airport", "city": "Delhi", "country": "India", "iata": "DEL"},
            {"name": "Mumbai Chhatrapati Shivaji Airport", "city": "Mumbai", "country": "India", "iata": "BOM"},
            {"name": "Jakarta Soekarno-Hatta Airport", "city": "Jakarta", "country": "Indonesia", "iata": "CGK"},
            {"name": "Manila Ninoy Aquino Airport", "city": "Manila", "country": "Philippines", "iata": "MNL"},
            {"name": "Taipei Taiwan Taoyuan Airport", "city": "Taipei", "country": "Taiwan", "iata": "TPE"},
            {"name": "Hanoi Noi Bai Airport", "city": "Hanoi", "country": "Vietnam", "iata": "HAN"},
            
            # Africa
            {"name": "Cairo International Airport", "city": "Cairo", "country": "Egypt", "iata": "CAI"},
            {"name": "Johannesburg OR Tambo Airport", "city": "Johannesburg", "country": "South Africa", "iata": "JNB"},
            {"name": "Cape Town International Airport", "city": "Cape Town", "country": "South Africa", "iata": "CPT"},
            {"name": "Nairobi Jomo Kenyatta Airport", "city": "Nairobi", "country": "Kenya", "iata": "NBO"},
            {"name": "Casablanca Mohammed V Airport", "city": "Casablanca", "country": "Morocco", "iata": "CMN"},
            {"name": "Addis Ababa Bole Airport", "city": "Addis Ababa", "country": "Ethiopia", "iata": "ADD"},
            {"name": "Lagos Murtala Muhammed Airport", "city": "Lagos", "country": "Nigeria", "iata": "LOS"},
            
            # Americas
            {"name": "New York John F Kennedy Airport", "city": "New York", "country": "United States", "iata": "JFK"},
            {"name": "New York LaGuardia Airport", "city": "New York", "country": "United States", "iata": "LGA"},
            {"name": "Newark Liberty Airport", "city": "Newark", "country": "United States", "iata": "EWR"},
            {"name": "Los Angeles International Airport", "city": "Los Angeles", "country": "United States", "iata": "LAX"},
            {"name": "Chicago O'Hare International Airport", "city": "Chicago", "country": "United States", "iata": "ORD"},
            {"name": "San Francisco International Airport", "city": "San Francisco", "country": "United States", "iata": "SFO"},
            {"name": "Miami International Airport", "city": "Miami", "country": "United States", "iata": "MIA"},
            {"name": "Atlanta Hartsfield-Jackson Airport", "city": "Atlanta", "country": "United States", "iata": "ATL"},
            {"name": "Dallas Fort Worth Airport", "city": "Dallas", "country": "United States", "iata": "DFW"},
            {"name": "Denver International Airport", "city": "Denver", "country": "United States", "iata": "DEN"},
            {"name": "Seattle-Tacoma International Airport", "city": "Seattle", "country": "United States", "iata": "SEA"},
            {"name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada", "iata": "YYZ"},
            {"name": "Vancouver International Airport", "city": "Vancouver", "country": "Canada", "iata": "YVR"},
            {"name": "Mexico City International Airport", "city": "Mexico City", "country": "Mexico", "iata": "MEX"},
            {"name": "Sao Paulo Guarulhos Airport", "city": "Sao Paulo", "country": "Brazil", "iata": "GRU"},
            {"name": "Buenos Aires Ezeiza Airport", "city": "Buenos Aires", "country": "Argentina", "iata": "EZE"},
            {"name": "Santiago Arturo Merino Airport", "city": "Santiago", "country": "Chile", "iata": "SCL"},
            {"name": "Lima Jorge Chavez Airport", "city": "Lima", "country": "Peru", "iata": "LIM"},
            {"name": "Bogota El Dorado Airport", "city": "Bogota", "country": "Colombia", "iata": "BOG"},
            
            # Oceania
            {"name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia", "iata": "SYD"},
            {"name": "Melbourne Tullamarine Airport", "city": "Melbourne", "country": "Australia", "iata": "MEL"},
            {"name": "Brisbane Airport", "city": "Brisbane", "country": "Australia", "iata": "BNE"},
            {"name": "Auckland Airport", "city": "Auckland", "country": "New Zealand", "iata": "AKL"},
        ]
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Search airports by name, city, country, or IATA code.
        Uses fuzzy matching for best results.
        """
        if not query or len(query) < 2:
            return []
        
        query = query.strip().lower()
        
        # Create searchable strings for each airport
        searchable = []
        for airport in self.airports:
            search_str = f"{airport['name']} {airport['city']} {airport['country']} {airport['iata']}"
            searchable.append((search_str, airport))
        
        # Use rapidfuzz to find best matches
        results = process.extract(
            query,
            [s[0] for s in searchable],
            scorer=fuzz.WRatio,
            limit=limit
        )
        
        # Map back to airport objects
        matched_airports = []
        for match_str, score, idx in results:
            if score >= 50:  # Minimum match threshold
                matched_airports.append(searchable[idx][1])
        
        return matched_airports
    
    def get_by_iata(self, iata_code: str) -> Optional[Dict]:
        """Get airport by IATA code."""
        return self.airports_by_code.get(iata_code.upper())
    
    def get_airports_by_country(self, country: str) -> List[Dict]:
        """Get all airports in a country."""
        country_lower = country.lower()
        return [
            a for a in self.airports 
            if a['country'].lower() == country_lower
        ]
    
    def format_airport_display(self, airport: Dict) -> str:
        """Format airport for display in dropdown."""
        return f"{airport['city']}, {airport['country']} ({airport['iata']}) - {airport['name']}"
    
    def format_airport_short(self, airport: Dict) -> str:
        """Format airport for short display."""
        return f"{airport['city']} ({airport['iata']})"


# Global airport service instance
airport_service = AirportService()
