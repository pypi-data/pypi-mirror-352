from dataclasses import dataclass

@dataclass
class TrainData:
    line: str
    train_id: str
    first_station: str
    last_station: str
    planned_departure: str
    current_departure: str
    track: str
    message: str
    train_station: str