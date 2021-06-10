'''
Interacting with DBMSs.
'''

import json
import mysql.connector
from neo4j import GraphDatabase
from redis import Redis
from pymongo import MongoClient
from hashlib import sha256

from sample_data import SampleData, DB_NAME

class LOGIN_RESULT:
    SUCC = 'successful'
    NOT_FOUND = 'not-found'
    WRONG = 'wrong'

class AVATAR:
    FOLDER = 'assets/avatars/'
    DEFAULT = FOLDER + 'default.png'

class Wrapper:
    '''
    Should manually catch exception from any db operation when using this class!
    '''

    def __init__(self):
        self.mysql = self.mysqlCur = None
        self.neo4j = self.neo4jSess = None
        self.redis = None
        self.mongo = self.mongoDb = None
        self.connected = False
        self.sampleData = None
        pass

    def connect(self, credentials_path: str) -> None:
        with open(credentials_path, 'r') as f:
            credentials = json.load(f)

            for i in ['mysql', 'neo4j', 'redis', 'mongo']:
                info = credentials[i]

                if i == 'mysql':
                    self.mysql = mysql.connector.connect(user=info['acc'], password=info['pass'])
                    self.mysqlCur = self.mysql.cursor()

                if i == 'neo4j':
                    self.neo4j = GraphDatabase.driver(info['uri'], auth=(info['acc'], info['pass']))
                    self.neo4jSess = self.neo4j.session()

                if i == 'redis': # Using Memurai 
                    self.redis = Redis(host=info['host'], port=info['port'], db=0)

                if i == 'mongo': 
                    self.mongo = MongoClient(info['uri'])

        self.connected = True
        self.sampleData = SampleData(self.mysqlCur, self.neo4jSess, self.mongo, self.redis, credentials)
        self.credentials = credentials   

    def disconnect(self) -> None:
        try:
            if self.connected:
                self.mysql.close()
                self.neo4j.close()
                self.mongo.close()
                # Redis (Memurai) handles the connection itself, no need to close manually
                self.mysql = self.mysqlCur = self.neo4j = self.neo4jSess = self.redis = self.mongo = None
                self.sampleData = None
                self.connected = False
        except:
            pass # ignore

    def createSampleData(self) -> None:
        self.sampleData.createAll()    
        self.mysql.commit()

    def pickupDatabase(self) -> None:
        self.mysql.database = DB_NAME.UNDERSCORE_VERSION
        self.neo4jSess = self.neo4j.session(database=DB_NAME.CAMEL_VERSION)
        self.mongoDb = self.mongo[DB_NAME.UNDERSCORE_VERSION]
        # No need to select database for Redis

    def getEmployees(self) -> list:
        neo4jSess = self.neo4jSess
        res = neo4jSess.run('MATCH (n:Employee)-[:IS]->(j), (n)-[:IN]->(d), (n)-[:WORKS_AT]->(b) RETURN n, j, d, b')
        return res.data()

    def getJobs(self) -> list:
        neo4jSess = self.neo4jSess
        res = neo4jSess.run('MATCH (j:JobTitle) RETURN j')
        jobs = []
        for j in res.data():
            jobs.append(j['j']['name'])
        return jobs

    def getBranches(self) -> list:
        neo4jSess = self.neo4jSess
        res = neo4jSess.run('MATCH (b:Branch) RETURN b')
        branches = []
        for b in res.data():
            branches.append(b['b']['name'])
        return branches

    def getDepartments(self) -> list:
        neo4jSess = self.neo4jSess
        res = neo4jSess.run('MATCH (d:Department) RETURN d')
        deps = []
        for d in res.data():
            deps.append(d['d']['name'])
        return deps

    def changeEmp(self, eid, name, birth, male, job, dep, branch) -> None:
        neo4jSess = self.neo4jSess
        res = neo4jSess.run('MATCH (n:Employee {id: \'%s\'}) RETURN n' % eid)

        if len(res.data()) == 0: # new emp
            neo4jSess.run('CREATE (n:Employee {id: \'%s\'})' % eid)
        else: # existing emp
            neo4jSess.run('MATCH (n:Employee {id: \'%s\'})-[jr:IS]->(j), (n)-[dr:IN]->(d), (n)-[wr:WORKS_AT]->(b) DELETE jr, dr, wr' % eid)

        neo4jSess.run('MATCH (n:Employee {id: \'%s\'}), (j:JobTitle {name: \'%s\'}), (d:Department {name: \'%s\'}), (b:Branch {name: \'%s\'}) SET n.name=\'%s\', n.birth=date(\'%s\'), n.male=\'%s\' WITH n, j, d, b CREATE (n)-[:IS]->(j), (n)-[:IN]->(d), (n)-[:WORKS_AT]->(b)' % (eid, job, dep, branch, name, birth, male)) 

    def delEmp(self, eid: str) -> None:
        self.neo4jSess.run('MATCH (n:Employee {id: \'%s\'}) DETACH DELETE n' % eid)

    def getProducts(self):
        mysqlCur = self.mysqlCur
        mysqlCur.execute('SELECT p.ID, p.PName, p.OnSale, p.OnSaleFrom, p.Price, t.BriefName FROM Product AS p JOIN ProductType as t ON p.PType = t.ID ORDER BY p.ID ASC;')
        return mysqlCur.fetchall()

    def getProductTypes(self) -> list:
        mysqlCur = self.mysqlCur
        mysqlCur.execute('SELECT t.Briefname FROM ProductType AS t;')
        res = mysqlCur.fetchall()
        ts = [t[0] for t in res]
        return ts

    def getNewProdID(self) -> int:
        mysqlCur = self.mysqlCur
        mysqlCur.execute('SELECT max(p.ID) FROM Product as p')
        res = mysqlCur.fetchall()[0][0]
        return res + 1

    def changeProd(self, pid, name, on, sfrom, price, ptype) -> None:
        mysqlCur = self.mysqlCur

        mysqlCur.execute('SELECT t.ID FROM ProductType AS t WHERE t.BriefName = \'%s\'' % ptype)
        t = mysqlCur.fetchall()[0][0]

        mysqlCur.execute('SELECT p.ID FROM Product AS p WHERE p.ID = %s' % pid)
        if len(mysqlCur.fetchall()) == 0:
            mysqlCur.execute('INSERT INTO Product(ID, PName, OnSale, OnSaleFrom, Price, PType) VALUES (%s, \'%s\', %d, \'%s\', %s, %d)' % (pid, name, on, sfrom, price, t))
        else:
            mysqlCur.execute('UPDATE Product SET PName=\'%s\', OnSale=%d, OnSaleFrom=\'%s\', Price=%s, PType=%d WHERE ID = %s' % (name, on, sfrom, price, t, pid))
        self.mysql.commit()

    def delProd(self, pid: int) -> None:
        mysqlCur = self.mysqlCur
        mysqlCur.execute('DELETE FROM Product AS p WHERE p.ID = %s;' % pid)
        self.mysql.commit()

    def memLogin(self, acc: str, pw: str):
        col = self.mongoDb['mems']
        res = col.find({'username': acc})

        if res.count() == 0:
            return LOGIN_RESULT.NOT_FOUND, {}
        
        acc = res[0]
        hashed = acc['password']
        if hashed == sha256(bytes(pw, encoding='UTF-8')).hexdigest():
            return LOGIN_RESULT.SUCC, acc
        
        return LOGIN_RESULT.WRONG, {}

    def getMemAvatarPath(self, uid: str) -> str:
        redis = self.redis
        key = '%s-avatar_path' % uid

        path = redis.get(key)
        if path is None:
            path = AVATAR.DEFAULT
        else:
            path = path.decode('UTF-8')
        return path

    def saveMemInfo(self, dat: dict) -> None:
        redis = self.redis
        col = self.mongoDb['mems']

        col.update_one({ 'id': dat['id'] }, { '$set': { 'id': dat['id'], 'username': dat['username'], 'password': dat['password'], 'level': dat['level'], 'fullname': dat['fullname'], 'birth': dat['birth'], 'phone': dat['phone'], 'email': dat['email'], 'address': dat['address'] } }, upsert=True)

        redis.set('%s-avatar_path' % dat['id'], dat['ava'])

    def __del__(self):
        self.disconnect()