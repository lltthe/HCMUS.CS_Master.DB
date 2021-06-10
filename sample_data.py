from os import stat
from mysql.connector.cursor import MySQLCursor
import neo4j
from pymongo import MongoClient
from redis import Redis
import json
from datetime import datetime

class PATH:
    DAT_FOLDER = './dat-scripts/'
    MYSQL_DATA_SCRIPT = DAT_FOLDER + 'create_sample_data.sql'
    NEO4J_DATA_SCRIPT = DAT_FOLDER + 'create_sample_data.cypher'
    MONGO_DATA_FILE = DAT_FOLDER + 'mongo_sample_data.json'
    REDIS_DATA_FILE = DAT_FOLDER + 'redis_sample_data.json'

class DB_NAME:
    UNDERSCORE_VERSION = 'hcmus_master_coffeehouse_sample'
    CAMEL_VERSION = 'HCMUSMasterCoffeeHouseSample' # Neo4j hates everything but simple db names

class SampleData():
    '''
    Should manually catch exception from any db operation when using this class!
    '''

    def __init__(self, mysqlCur: MySQLCursor, neo4jSess: neo4j.Session, mongo: MongoClient, redis: Redis, credentials: dict):
        self.mysqlCur = mysqlCur
        self.credentials = credentials
        self.neo4jSess = neo4jSess
        self.mongo = mongo
        self.redis = redis

    def createAll(self) -> None:
        self.createMySQL()
        self.createNeo4j()
        self.createMongo()
        self.createRedis()

    def createMySQL(self) -> None:
        statement = ''
        with open(PATH.MYSQL_DATA_SCRIPT, 'r', encoding='UTF-8') as f:
            for line in f:
                line = line.strip()
                if line == '' or line.startswith('--'):
                    continue
                statement += ' ' + line
                if line.endswith(';'):
                    self.mysqlCur.execute(statement)
                    statement = ''

    def createNeo4j(self) -> None:
        statement = ''
        with open(PATH.NEO4J_DATA_SCRIPT, 'r', encoding='UTF-8') as f:
            for line in f:
                line = line.strip()
                if line == '':
                    continue
                statement += ' ' + line
                if line.endswith(';'):
                    self.neo4jSess.run(statement)
                    statement = ''

    def createMongo(self) -> None:
        f = open(PATH.MONGO_DATA_FILE, 'r', encoding='UTF-8')

        self.mongo.drop_database(DB_NAME.UNDERSCORE_VERSION)
        mgdb = self.mongo[DB_NAME.UNDERSCORE_VERSION] # Delayed until 1 collection, 1 record created

        dat = json.load(f)
        for c in dat:
            col = mgdb[c]
            for r in dat[c]:
                doc = dat[c][r]
                if c == 'mems':
                    doc['birth'] = datetime.strptime(doc['birth'], '%Y-%m-%d')
                col.insert_one(doc)

        f.close()

    def createRedis(self) -> None:
        f = open(PATH.REDIS_DATA_FILE, 'r', encoding='UTF-8')
        redis = self.redis

        dat = json.load(f)
        for key in dat:
            redis.set(key, dat[key])

    def checkDataAvailability(self) -> dict:
        return {'mysql': self.isMySQLDataAvailable(), 'neo4j': self.isNeo4jDataAvailable(), 'mongo': self.isMongoDataAvailable, 'redis': self.isRedisDataAvailable}

    def isMySQLDataAvailable(self) -> bool:
        mysqlCur = self.mysqlCur
        mysqlCur.execute("show databases like %s", (DB_NAME.UNDERSCORE_VERSION,))
        res = mysqlCur.fetchall()
        if len(res) == 0:
            return False
        return True 

    def isNeo4jDataAvailable(self) -> bool:
        neo4jSess = self.neo4jSess
        res = neo4jSess.run('show database %s' % DB_NAME.CAMEL_VERSION)
        if len(res.data()) == 0:
            return False
        return True   

    def isMongoDataAvailable(self) -> bool:
        if DB_NAME.UNDERSCORE_VERSION in self.mongo.list_database_names():
            return True
        return False

    def isRedisDataAvailable(self) -> bool:
        return True # Currently no sample data, no need to check