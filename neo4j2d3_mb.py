"""
graphjson module pull an event from neo4j and creates
graphjson formated file to be used with D3js
Written by Ray Bernard ray@suprfanz.com

"""

import json

from neo4j.v1 import GraphDatabase, basic_auth

from config import neo4j_password, neo4j_admin, neo4j_dbip


def create_guest_node():
    # fetches the guest nodes from neo4j
    insert_query_guest = '''
    MATCH (a:fb_guest)
    WITH collect({id: a.fb_usr_id, name: a.fb_guest_name, group: 1}) AS nodes RETURN nodes
    '''
    with  GraphDatabase.driver("bolt://{}:7687".format(neo4j_dbip),
                               auth=basic_auth("neo4j", "{}".format(neo4j_password))) as driver:
        with driver.session() as session:
            result = session.run(insert_query_guest)
            counter = 0
            for record in result:
                counter += 1
                return json.dumps(dict(record))


def create_event_node():
    # fetches the event nodes from neo4j
    insert_query_guest = '''
    MATCH (a:fb_event)
    WITH collect({id:a.fb_event_id, name:a.event_name, group:0}) AS nodes RETURN nodes 
    '''
    with  GraphDatabase.driver("bolt://{}:7687".format(neo4j_dbip),
                               auth=basic_auth("neo4j", "{}".format(neo4j_password))) as driver:
        with driver.session() as session:
            result = session.run(insert_query_guest)
            for record in result:
                return json.dumps(record['nodes'])


def create_guest_edge():
    # gets the guest relationships from neo4j
    insert_query_guest = '''
    MATCH (a:fb_guest)-[r:RSVP]->(b:fb_event)
    WITH collect({source: a.fb_usr_id,target: b.fb_event_id, value:r.value, rsvp:r.rsvp_status}) AS links RETURN links
    '''
    with  GraphDatabase.driver("bolt://{}:7687".format(neo4j_dbip),
                               auth=basic_auth("neo4j", "{}".format(neo4j_password))) as driver:
        with driver.session() as session:
            result = session.run(insert_query_guest)
            for record in result:
                return json.dumps(dict(record))


def db_json():
    # puts the data together in graphjson format
    guest_nodes = str(create_guest_node())[:-2]
    event_node = str((create_event_node()))[1:]
    guest_edges = str(create_guest_edge())[1:]
    print(guest_nodes)
    if guest_nodes == '{"nodes": [':
        graphjson = '{"nodes": [], "links": []}'
    else:
        graphjson = str(guest_nodes) + ',' + str(event_node) + ',' + str(guest_edges)

    print(graphjson)
    # put your file path to json data here
    with open(
            "C:\\Users\\yourname\\Documents\\path\\to\\flask-fb-neo4j-d3\\app\\static\\data\\neo4j2d3_new.json",
            "w") as f:
        f.write(graphjson)
    return graphjson


if __name__ == '__main__':
    db_json()
