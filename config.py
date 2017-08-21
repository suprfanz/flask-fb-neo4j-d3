from os import path

# App details
BASE_DIRECTORY = path.abspath(path.dirname(__file__))
DEBUG = True
SECRET_KEY = 'keep_it_like_a_secret'

# Add your own Database details
neo4j_password = 'neo4j'
neo4j_admin = 'neo4j'
neo4j_dbip = '192.186.1.1'
