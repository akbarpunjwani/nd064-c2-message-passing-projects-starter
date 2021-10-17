from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

# from app import db  # noqa
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
from shapely.geometry.point import Point

@dataclass
class Connection:
    location: Location
    person: Person

@dataclass
class Location:
    id: int = -1
    person_id: int = -1
    longitude: str = None
    latitude: str = None
    creation_time: str = None

@dataclass
class Person:
    id: int = -1
    first_name: str = None
    last_name: str = None
    company_name: str = None