from datetime import datetime
# import grpc
# from connections_pb2_grpc import ConnectionsStub
# from connections_pb2 import ConnectionRequest, Date

from app.udaconnect.models import Connection, Location, Person
from app.udaconnect.schemas import (
    ConnectionSchema,
    LocationSchema, 
    PersonSchema
)

from app.udaconnect.services import ConnectionService
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

    try:
        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        producer.send(TOPIC_NAME, value=msg.encode('utf-8'))
        producer.flush()
    except:
        kafkaisnotready=1
    #############


DATE_FORMAT = "%Y-%m-%d"

api = Namespace("ApiConnection", description="Connections via geolocation.")  # noqa


@api.route("/connections/<person_id>/all")
@api.param("start_date", "Lower bound of date range", _in="query")
@api.param("end_date", "Upper bound of date range", _in="query")
@api.param("distance", "Proximity to a given user in meters", _in="query")
class ConnectionDataResource(Resource):
    @responds(schema=ConnectionSchema, many=True)
    def get(self, person_id) -> ConnectionSchema:
        start_date: datetime = datetime.strptime(
            request.args["start_date"], DATE_FORMAT
        )
        end_date: datetime = datetime.strptime(request.args["end_date"], DATE_FORMAT)
        distance: Optional[int] = int(request.args.get("distance", 5))

        log2kafka('/api/connections/'+str(person_id)+'/startdate:'+str(start_date)+'/enddate:'+str(end_date)+'/meters:'+str(distance)+'/find_contacts')
        results = ConnectionService.find_contacts(
            person_id=int(person_id),
            start_date=start_date,
            end_date=end_date,
            meters=int(distance),
        )
        return results
