import json
import grpc
from connections_pb2_grpc import ConnectionsStub
from connections_pb2 import ConnectionRequest, Date

from google.protobuf.json_format import MessageToJson

import logging
from datetime import datetime, timedelta
from typing import Dict, List

from app.udaconnect.models import Connection, Location, Person
from app.udaconnect.schemas import ConnectionSchema, LocationSchema, PersonSchema

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("udaconnect-api")

class ConnectionService:
    @staticmethod
    def find_contacts(person_id: int, start_date: datetime, end_date: datetime, meters=5
    ) -> List[Connection]:
        """
        Finds all Person who have been within a given distance of a given Person within a date range.

        This will run rather quickly locally, but this is an expensive method and will take a bit of time to run on
        large datasets. This is by design: what are some ways or techniques to help make this data integrate more
        smoothly for a better user experience for API consumers?
        """
        channel = grpc.insecure_channel("udaconnect-grpcconnections:50051")
        client = ConnectionsStub(channel)

        fromdate = Date(
            year = start_date.year,
            month = start_date.month,
            day = start_date.day)
        todate = Date(
            year = end_date.year,
            month = end_date.month,
            day = end_date.day)

        request = ConnectionRequest(
            person_id = int(person_id), 
            start_date = fromdate, 
            end_date = todate, 
            meters = int(meters))
        jsonobj = MessageToJson(client.find_contacts(request))
        jsonobj = jsonobj.replace("personId","person_id").replace('firstName','first_name').replace('lastName','last_name').replace('companyName','company_name')
        jsonobj = jsonobj.replace('creationTime','creation_time')
        jsonobj = json.loads(jsonobj)['locpersons']

        result: List[Connection] = []

        for contact in jsonobj:
            result.append(
                Connection(
                    location = Location(
                        id = int(contact['location']['id']),
                        person_id = int(contact['location']['person_id']),
                        longitude = str(contact['location']['longitude']),
                        latitude = str(contact['location']['latitude']),
                        creation_time = str(contact['location']['creation_time'])
                    ),
                    person = Person(
                        id = int(contact['person']['id']), 
                        first_name = str(contact['person']['first_name']),
                        last_name = str(contact['person']['last_name']),
                        company_name = str(contact['person']['company_name']),
                    )
                )
            )

        return result

    # @staticmethod
    # def find_contacts_fromDB(person_id: int, start_date: datetime, end_date: datetime, meters=5
    # ) -> List[Connection]:
    #     """
    #     Finds all Person who have been within a given distance of a given Person within a date range.

    #     This will run rather quickly locally, but this is an expensive method and will take a bit of time to run on
    #     large datasets. This is by design: what are some ways or techniques to help make this data integrate more
    #     smoothly for a better user experience for API consumers?
    #     """
    #     locations: List = db.session.query(Location).filter(
    #         Location.person_id == person_id
    #     ).filter(Location.creation_time < end_date).filter(
    #         Location.creation_time >= start_date
    #     ).all()

    #     # Cache all users in memory for quick lookup
    #     person_map: Dict[str, Person] = {person.id: person for person in PersonService.retrieve_all()}

    #     # Prepare arguments for queries
    #     data = []
    #     for location in locations:
    #         data.append(
    #             {
    #                 "person_id": person_id,
    #                 "longitude": location.longitude,
    #                 "latitude": location.latitude,
    #                 "meters": meters,
    #                 "start_date": start_date.strftime("%Y-%m-%d"),
    #                 "end_date": (end_date + timedelta(days=1)).strftime("%Y-%m-%d"),
    #             }
    #         )

    #     query = text(
    #         """
    #     SELECT  person_id, id, ST_X(coordinate), ST_Y(coordinate), creation_time
    #     FROM    location
    #     WHERE   ST_DWithin(coordinate::geography,ST_SetSRID(ST_MakePoint(:latitude,:longitude),4326)::geography, :meters)
    #     AND     person_id != :person_id
    #     AND     TO_DATE(:start_date, 'YYYY-MM-DD') <= creation_time
    #     AND     TO_DATE(:end_date, 'YYYY-MM-DD') > creation_time;
    #     """
    #     )
    #     result: List[Connection] = []
    #     for line in tuple(data):
    #         for (
    #             exposed_person_id,
    #             location_id,
    #             exposed_lat,
    #             exposed_long,
    #             exposed_time,
    #         ) in db.engine.execute(query, **line):
    #             location = Location(
    #                 id=location_id,
    #                 person_id=exposed_person_id,
    #                 creation_time=exposed_time,
    #             )
    #             location.set_wkt_with_coords(exposed_lat, exposed_long)

    #             result.append(
    #                 Connection(
    #                     person=person_map[exposed_person_id], location=location,
    #                 )
    #             )

    #     return result
