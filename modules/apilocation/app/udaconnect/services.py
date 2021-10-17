import logging
from datetime import datetime, timedelta
from typing import Dict, List

from sqlalchemy.sql.sqltypes import Integer, String

from app import db
from app.udaconnect.models import Location, LocPersons, LocCoord
from app.udaconnect.schemas import LocationSchema, LocPersonSchema, LocCoordSchema
from geoalchemy2.functions import ST_AsText, ST_Point
from sqlalchemy.sql import text

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")

class LocationService:
    @staticmethod
    def retrieve(location_id) -> Location:
        location, coord_text = (
            db.session.query(Location, Location.coordinate.ST_AsText())
            .filter(Location.id == location_id)
            .one()
        )

        # Rely on database to return text form of point to reduce overhead of conversion in app code
        location.wkt_shape = coord_text
        return location

    @staticmethod
    def create(location: Dict) -> Location:
        validation_results: Dict = LocationSchema().validate(location)
        if validation_results:
            logger.warning(f"Unexpected data format in payload: {validation_results}")
            raise Exception(f"Invalid payload: {validation_results}")

        new_location = Location()
        new_location.person_id = location["person_id"]
        new_location.creation_time = location["creation_time"]
        new_location.coordinate = ST_Point(location["latitude"], location["longitude"])
        db.session.add(new_location)
        db.session.commit()

        return new_location

    @staticmethod
    def find_persons(location_id: int, start_date: datetime, end_date: datetime, meters=5
    ) -> List[LocPersons]:
        """
        Finds all Person who have been within a given distance of a given Person within a date range.
        """
        locations: List = db.session.query(Location).filter(
            Location.id == location_id
        ).all()

        # Prepare arguments for queries
        data = []
        for location in locations:
            data.append(
                {
                    "location_id": location_id,
                    "longitude": location.longitude,
                    "latitude": location.latitude,
                    "meters": meters,
                    "start_date": start_date.strftime("%Y-%m-%d"),
                    "end_date": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
                }
            )

        query = text(
            """
        SELECT  person_id, ST_X(MAX(coordinate)), ST_Y(MAX(coordinate)), MAX(creation_time)
        FROM    location
        WHERE   ST_DWithin(coordinate::geography,ST_SetSRID(ST_MakePoint(:latitude,:longitude),4326)::geography, :meters)
        AND     TO_DATE(:start_date, 'YYYY-MM-DD') <= creation_time
        AND     TO_DATE(:end_date, 'YYYY-MM-DD') > creation_time
        GROUP BY person_id;
        """
        )
        result: List[LocPersons] = []        
        for line in tuple(data):
            for (
                exposed_person_id,
                exposed_lat,
                exposed_long,
                exposed_time,
            ) in db.engine.execute(query, **line):
                result.append(
                    LocPersons(
                        person_id = exposed_person_id,
                        latitude = exposed_lat,
                        longitude = exposed_long,                
                        creation_time = exposed_time,
                        id = -1,
                        )
                )        

        return result

    @staticmethod
    def find_locations(person_id: int, start_date: datetime, end_date: datetime
    ) -> List[LocCoord]:
        """
        Finds all coordinates of locations w.r.t given Person & within a date range.
        """
        locations: List = db.session.query(Location).filter(
            Location.person_id == person_id
        ).all()

        # Prepare arguments for queries
        data = []
        data.append(
            {
                "person_id": person_id,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            }
        )

        query = text(
            """
        SELECT  person_id, MAX(id), ST_X(coordinate), ST_Y(coordinate), MAX(creation_time) 
        FROM    location
        WHERE   person_id = :person_id
        AND     TO_DATE(:start_date, 'YYYY-MM-DD') <= creation_time
        AND     TO_DATE(:end_date, 'YYYY-MM-DD') > creation_time
        GROUP BY person_id, coordinate;

        """
        )
        result: List[LocCoord] = []        
        for line in tuple(data):
            for (
                exposed_person_id,
                location_id,                
                exposed_lat,
                exposed_long,
                exposed_time,
            ) in db.engine.execute(query, **line):
                location = Location(
                    id = location_id,
                    person_id = exposed_person_id,
                    creation_time = exposed_time,
                )
                location.set_wkt_with_coords(exposed_lat, exposed_long)
                
                result.append(
                    LocCoord(
                        location_id = location.id,
                        coordinate = location.coordinate,
                        wkt_shape = location._wkt_shape,
                        longitude = location.longitude,
                        latitude = location.latitude,
                        )
                )        

        return result