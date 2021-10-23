from concurrent import futures
import requests

import os
from kafka import KafkaProducer

import grpc

from connections_pb2 import (
    LocationConnection,
    PersonConnection,
    LocPersonConnection,
    ConnectionResponse,
)
import connections_pb2_grpc

def log2kafka(msg):
    try:
        #############
        # KAFKA CODE
        TOPIC_NAME = os.environ["KAFKA_TOPIC"]
        KAFKA_SERVER = os.environ["KAFKA_SERVER"] + ':' + os.environ["KAFKA_PORT"]

        producer = KafkaProducer(bootstrap_servers=KAFKA_SERVER)
        producer.send(TOPIC_NAME, value=msg.encode('utf-8'))
        producer.flush()
    except:
        kafkaisnotready=1
    #############

class ConnectionService(
    connections_pb2_grpc.ConnectionsServicer
):
    def find_contacts(self, request, context):
        # persons_connected = [
        #     PersonConnection(person_id=1, first_name="The Maltese ", last_name="Falcon", company_name="ABC"),
        #     PersonConnection(person_id=2, first_name="Murder on the ", last_name="Orient Express", company_name="PQR"),
        #     PersonConnection(person_id=3, first_name="The Hound of the ", last_name="Baskervilles", company_name="XYZ"),
        # ]
        print(request,'>>>NEW GRPC REQUEST>>>')        

        query = {'start_date':str(request.start_date.year)+'-'+str(request.start_date.month)+'-'+str(request.start_date.day), 
                'end_date':str(request.end_date.year)+'-'+str(request.end_date.month)+'-'+str(request.end_date.day),
                'distance':str(request.meters)}
        print(query)        

        try:
            API_PERSON_HOST = os.environ["API_PERSON_HOST"]
            API_PERSON_PORT = os.environ["API_PERSON_PORT"]
        except:
            API_PERSON_HOST = 'localhost'
            API_PERSON_PORT = '30001'
        url_apiperson = 'http://'+API_PERSON_HOST+':'+API_PERSON_PORT


        try:
            API_LOCATION_HOST = os.environ["API_LOCATION_HOST"]
            API_LOCATION_PORT = os.environ["API_LOCATION_PORT"]
        except:
            API_LOCATION_HOST = 'localhost'
            API_LOCATION_PORT = '30002'
        url_apilocation = 'http://'+API_LOCATION_HOST+':'+API_LOCATION_PORT
            
        print(url_apiperson)
        print(url_apilocation)
        log2kafka('/api/<<<NEW GRPC REQUEST>>>/person/'+str(request.person_id)+'/find_contacts/'+str(query))

        response = requests.get(url_apilocation+'/api/locations/person/'+str(request.person_id), params=query)
        print('log')
        connections = {}
        # print(response)
        if (response.status_code == 200):
            # print(response.json())
            exposed_locations = response.json()
            for loc in exposed_locations:
                # print('loc:'+str(loc['location_id']),'\n')
                # query = {'start_date':str(request.start_date.year)+'-'+str(request.start_date.month)+'-'+str(request.start_date.day), 
                #         'end_date':str(request.end_date.year)+'-'+str(request.end_date.month)+'-'+str(request.end_date.day)}
                response = requests.get(url_apilocation+'/api/locations/'+str(loc['location_id'])+'/persons', params=query)
                # print(response)
                if (response.status_code == 200):
                    # print(response.json())
                    person_connections = response.json()
                    for contact in person_connections:
                        if str(contact['person_id']) not in connections and str(contact['person_id']) != str(request.person_id):
                            # print('>> contact:'+str(contact['id']),'\n')
                            response = requests.get(url_apiperson+'/api/persons/'+str(contact['person_id']))
                            if (response.status_code == 200):
                                person = response.json()
                                # print('>>>',person)
                                connections[str(contact['person_id'])]={'location':contact, 'person':person}
                            else:
                                print(response)
                else:
                    print(response)
            # print(connections.items())
        else:
            print(response)
        print('final')

        persons_connected = []
        for key,item in connections.items():
            # print('>>>',key,item)
            # print(PersonConnection(person_id=item['id'], first_name=item['first_name'], last_name=item['last_name'], company_name=item['company_name']))
            loc = LocationConnection(
                        person_id=item['location']['person_id'], 
                        longitude=item['location']['longitude'], 
                        latitude=item['location']['latitude'], 
                        creation_time=item['location']['creation_time'], 
                        id=item['location']['id']
                    )
            # print(loc)
            per = PersonConnection(
                        id=item['person']['id'], 
                        first_name=item['person']['first_name'], 
                        last_name=item['person']['last_name'], 
                        company_name=item['person']['company_name']
                    )
            # print(per)
            persons_connected.append(
                LocPersonConnection(
                    location = loc,
                    person = per
                )
            )
            print(len(persons_connected))

        # print(persons_connected)
        print('<<<COMPLETED GRPC RESPONSE with ',str(len(persons_connected)),' items<<<')
        return ConnectionResponse(locpersons=persons_connected)

def serve():
    print('<<SERVE>>')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    connections_pb2_grpc.add_ConnectionsServicer_to_server(
        ConnectionService(), server
    )

    try:
        API_CONNECTION_GRPCPORT = os.environ["API_CONNECTION_GRPCPORT"]
    except:
        API_CONNECTION_GRPCPORT = '50051'

    print('Starting GRPC Server to listen client requests...At Port:',API_CONNECTION_GRPCPORT)

    server.add_insecure_port("[::]:"+API_CONNECTION_GRPCPORT)
    server.start()
    server.wait_for_termination()


# if __name__ == "__main__":
#     print('Entered the MAIN')
#     serve()
#     print('Ending MAIN')

print('Entered the MAIN')
serve()
print('Ending MAIN')
