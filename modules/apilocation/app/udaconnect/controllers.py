from datetime import datetime

from app.udaconnect.models import Location, LocPersons, LocCoord
from app.udaconnect.schemas import (
    LocationSchema, 
    LocPersonSchema,
    LocCoordSchema
)
from app.udaconnect.services import LocationService
from flask import request
from flask_accepts import accepts, responds
from flask_restx import Namespace, Resource
from typing import Optional, List

import os
from kafka import KafkaProducer
def log2kafka(msg):
    #############
    # KAFKA CODE
    TOPIC_NAME = os.environ["KAFKA_TOPIC"]
    KAFKA_SERVER = os.environ["KAFKA_SERVER"] + ':' + os.environ["KAFKA_PORT"]

    producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
    producer.send(TOPIC_NAME, value=msg.encode('utf-8'))
    producer.flush()
    #############


DATE_FORMAT = "%Y-%m-%d"

api = Namespace("UdaConnect", description="Connections via geolocation.")  # noqa

# TODO: This needs better exception handling

@api.route("/locations")
@api.route("/locations/<location_id>")
@api.param("location_id", "Unique ID for a given Location", _in="query")
class LocationResource(Resource):
    @accepts(schema=LocationSchema)
    @responds(schema=LocationSchema)
    def post(self) -> Location:
        request.get_json()
        location: Location = LocationService.create(request.get_json())
        return location

    @responds(schema=LocationSchema)
    def get(self, location_id) -> Location:
        log2kafka('/api/locations/retrieve/'+str(location_id))
        location: Location = LocationService.retrieve(location_id)
        return location

@api.route("/locations/<location_id>/persons")
@api.param("start_date", "Lower bound of date range", _in="query")
@api.param("end_date", "Upper bound of date range", _in="query")
@api.param("distance", "Proximity to a given user in meters", _in="query")
class LocationResource(Resource):
    @responds(schema=LocPersonSchema, many=True)
    def get(self, location_id) -> LocPersonSchema:
        start_date: datetime = datetime.strptime(
            request.args["start_date"], DATE_FORMAT
        )
        end_date: datetime = datetime.strptime(request.args["end_date"], DATE_FORMAT)
        distance: Optional[int] = request.args.get("distance", 5)

        log2kafka('/api/locations/find_persons/locid:'+str(location_id)+'/start_date:'+str(start_date)+'/end_date:'+str(end_date)+'/meters:'+str(distance))
        results = LocationService.find_persons(
            location_id=location_id,
            start_date=start_date,
            end_date=end_date,
            meters=distance,
        )
        return results


@api.route("/locations/person/<person_id>")
@api.param("person_id", "Unique ID for a given Person", _in="query")
@api.param("start_date", "Lower bound of date range", _in="query")
@api.param("end_date", "Upper bound of date range", _in="query")
class LocationResource(Resource):
    @responds(schema=LocCoordSchema, many=True)
    def get(self, person_id) -> LocCoordSchema:
        start_date: datetime = datetime.strptime(
            request.args["start_date"], DATE_FORMAT
        )
        end_date: datetime = datetime.strptime(request.args["end_date"], DATE_FORMAT)
        log2kafka('/api/locations/find_locations/personid:'+str(person_id)+'/start_date:'+str(start_date)+'/end_date:'+str(end_date))
        loccoordinates: LocCoord = LocationService.find_locations(
            person_id,
            start_date=start_date,
            end_date=end_date,
            )
        return loccoordinates


