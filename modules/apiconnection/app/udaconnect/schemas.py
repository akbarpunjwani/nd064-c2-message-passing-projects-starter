from dataclasses import field
from app.udaconnect.models import Connection, Location, Person
from marshmallow import Schema, fields

class LocationSchema(Schema):
    id = fields.Integer()
    person_id = fields.Integer()
    longitude = fields.String()
    latitude = fields.String()
    creation_time = fields.String()

class PersonSchema(Schema):
    id = fields.Integer()
    first_name = fields.String()
    last_name = fields.String()
    company_name = fields.String()

class ConnectionSchema(Schema):
    location = fields.Nested(LocationSchema)
    person = fields.Nested(PersonSchema)

