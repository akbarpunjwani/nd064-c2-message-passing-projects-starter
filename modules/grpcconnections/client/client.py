import os
import json
import grpc
from connections_pb2_grpc import ConnectionsStub
from connections_pb2 import ConnectionRequest, Date

from google.protobuf.json_format import MessageToJson

try:
    API_CONNECTION_GRPCHOST = os.environ["API_CONNECTION_GRPCHOST"]
    API_CONNECTION_GRPCPORT = os.environ["API_CONNECTION_GRPCPORT"]
except:
    API_CONNECTION_GRPCHOST = 'localhost'
    API_CONNECTION_GRPCPORT = '50051'

print('Sending request to GRPC Server ', API_CONNECTION_GRPCHOST,'...At Port:',API_CONNECTION_GRPCPORT)

channel = grpc.insecure_channel(API_CONNECTION_GRPCHOST+":"+API_CONNECTION_GRPCPORT)
client = ConnectionsStub(channel)

fromdate = Date(year=2020,month=1,day=1)
todate = Date(year=2020,month=12,day=30)

# /api/connections/5/all?start_date=2020-01-01&end_date=2020-12-30&distance=5
request = ConnectionRequest(person_id=5, start_date=fromdate, end_date=todate, meters=5)
jsonobj = MessageToJson(client.find_contacts(request))
jsonobj = jsonobj.replace("personId","person_id").replace('firstName','first_name').replace('lastName','last_name').replace('companyName','company_name')
jsonobj = jsonobj.replace('creationTime','creation_time')
print(json.loads(jsonobj)['locpersons'])
# (ConnectionsStub(grpc.insecure_channel('10.42.0.230:50051'))).find_contacts(request)
# print(type(jsonobj))

# import requests

# response=requests.get('http://localhost:30001/api/persons')
# print(response)
# print(response.json())

# query = {'start_date':'2019-01-01', 'end_date':'2020-12-30'}
# response = requests.get('http://localhost:30002/api/locations/person/5', params=query)
# print(response)
# if (response.status_code == 200):
#     # print(response.json())
#     exposed_locations = response.json()
#     connections = {}
#     for loc in exposed_locations:
#         print('loc:'+str(loc['location_id']),'\n')

#         query = {'start_date':'2019-01-01', 'end_date':'2020-12-30'}
#         response = requests.get('http://localhost:30002/api/locations/'+str(loc['location_id'])+'/persons', params=query)
#         # print(response)
#         if (response.status_code == 200):
#             # print(response.json())
#             person_connections = response.json()
#             for contact in person_connections:
#                 if str(contact['id']) not in connections:
#                     print('>> contact:'+str(contact['id']),'\n')
#                     response = requests.get('http://localhost:30001/api/persons/'+str(contact['id']))
#                     if (response.status_code == 200):
#                         person = response.json()
#                         print(person)
#                         connections[str(contact['id'])]=person
#     print(connections)

