class City():
    def __init__(self, name: str, alt_names: list, latitude: float, longitude: float, timezone_id: str):
        self.name = name
        self.alt_names = alt_names
        self.latitude = latitude
        self.longitude = longitude
        self.timezone_id = timezone_id
    
    def __str__(self):
        return f"City: {self.name}"