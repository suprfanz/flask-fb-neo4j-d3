# -*- coding: utf-8 -*-
"""
This Class creates the user in neo4j via the Facebook API when they register and checks if they exist when they login..
Written by Ray Bernard
"""

from neo4j.v1 import GraphDatabase, basic_auth

from config import neo4j_password, neo4j_dbip


class User(object):
    def __init__(self, id, name, profile_url, access_token):
        self.id = id
        self.name = name
        self.profile_url = profile_url
        self.access_token = access_token

        self.session = GraphDatabase.driver("bolt://{}:7687".format(neo4j_dbip),
                                            auth=basic_auth("neo4j", "{}".format(neo4j_password))).session()

    def create_user(self):
        # creates the user
        insert_query = '''
        MERGE (n:user{id:{id}, name:{name},profile_url:{profile_url}, access_token:{access_token}})

        '''
        self.session.run(insert_query, parameters={"id": self.id,
                                                   "name": self.name,
                                                   "profile_url": self.profile_url,
                                                   "access_token": self.access_token
                                                   })
        # self.session.close()

    def check_user(self):
        # checks if the user exists already
        insert_query = '''
        MATCH (n:user)
        WHERE n.id = {id}
        RETURN n.id AS id, n.name AS name, n.access_token AS access_token, n.profile_url AS profile_url
        '''
        result = self.session.run(insert_query, parameters={"id": self.id})
        self.session.close()
        for record in result:
            return dict(record)


if __name__ == '__main__':
    id = '11111'
    name = 'Cosmic jen'
    access_token = '66666666666'
    profile_url = 'http://www.jen.com'

    user = User(id, name, profile_url, access_token)
    user.create_user()
