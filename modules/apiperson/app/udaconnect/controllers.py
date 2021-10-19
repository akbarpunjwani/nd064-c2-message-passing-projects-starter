from datetime import datetime

from app.udaconnect.models import Person
from app.udaconnect.schemas import (
    PersonSchema,
)
from app.udaconnect.services import PersonService
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

api = Namespace("ApiPerson", description="Persons registered for UdaConnect")  # noqa

# TODO: This needs better exception handling

@api.route("/persons")
class PersonsResource(Resource):
    @accepts(schema=PersonSchema)
    @responds(schema=PersonSchema)
    def post(self) -> Person:
        payload = request.get_json()
        new_person: Person = PersonService.create(payload)
        return new_person

    @responds(schema=PersonSchema, many=True)
    def get(self) -> List[Person]:        
        log2kafka('/api/persons/retrieve_all')
        persons: List[Person] = PersonService.retrieve_all()
        return persons


@api.route("/persons/<person_id>")
@api.param("person_id", "Unique ID for a given Person", _in="query")
class PersonResource(Resource):
    @responds(schema=PersonSchema)
    def get(self, person_id) -> Person:
        log2kafka('/api/person/'+str(person_id)+'/retrieve')
        person: Person = PersonService.retrieve(person_id)
        return person