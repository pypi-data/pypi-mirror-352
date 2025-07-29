from dataclasses import dataclass

@dataclass
class AuthData:
    client_id: str
    client_secret: str

@dataclass
class DatabaseConfig:
    hostname: str
    user: str
    password: str
    database: str