from collections import Set
import json
from server.database.server_matches_model import ServerMatchesModel
from server.database.apply_scores_model import ApplyScoresModel
from trigger.models.opening import Opening
from trigger.models.user import User

from server.database.user_model import UserModel
from typing import Dict, List
from server.database.opening_model import OpeningModel
from trigger.util.readers.data_reader import DataReaderOpenings, DataReaderUsers
from server.database import names
from server.app import app
from server.jobs import rq
import unittest

import logging

logging.basicConfig(level=logging.ERROR)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

from bson.objectid import ObjectId

import os

from pymongo import MongoClient

def ensure_ss_and_hs(c: MongoClient, users: List[User], openings: List[Opening]):
    database = c["testing"]
    hs_collection = database[names.hardskills_collection_name]
    ss_collection = database[names.softskills_collection_name]

    hs_map: Dict[str, ObjectId] = {}
    ss_map: Dict[str, ObjectId] = {}

    unique_hs: Set[str] = set()
    unique_ss: Set[str] = set()

    for user in users:

        hss = user.hardSkills
        sss = user.softSkills

        for hs in hss:
            unique_hs.add(hs.name)

        for ss in sss:
            unique_ss.add(ss.name)
    
    for opening in openings:

        hss = opening.hardSkills
        sss = opening.softSkills

        for hs in hss:
            unique_hs.add(hs.name)

        for ss in sss:
            unique_ss.add(ss.name)

    hs_ids = hs_collection.insert_many([
        {
            'name': hs_name
        } for hs_name in unique_hs
    ]).inserted_ids

    for hs_id, hs_name in zip(hs_ids, unique_hs):
        hs_map[hs_name] = hs_id

    ss_ids = ss_collection.insert_many([
        {
            'name': ss_name
        } for ss_name in unique_ss
    ]).inserted_ids

    for ss_id, ss_name in zip(ss_ids, unique_ss):
        ss_map[ss_name] = ss_id

    return hs_map, ss_map

def add_users_to_db(c: MongoClient, hs_map: Dict[str, ObjectId], ss_map: Dict[str, ObjectId], users: List[User]):
    database = c["testing"]
    user_collection = database[UserModel.collection_name]
    user_ids: List[ObjectId] = []

    for user in users:
        r = user_collection.insert_one({
            'name': user.name,
            'hardSkills': [
                {
                    "hardskillId": hs_map[hs.name]
                } for hs in user.hardSkills
            ],
            'softSkills': [
                {
                    "softskillId": ss_map[ss.name]
                } for ss in user.softSkills
            ]
        })

        user_ids.append(r.inserted_id)

    return user_ids


def add_openings_to_db(c: MongoClient, hs_map: Dict[str, ObjectId], ss_map: Dict[str, ObjectId], openings: List[Opening]):
    database = c["testing"]
    
    opening_collection = database[OpeningModel.collection_name]

    opening_ids: List[ObjectId] = []

    for opening in openings:
        r = opening_collection.insert_one({
            'hardskills': [
                hs_map[hs.name]
                for hs in opening.hardSkills
            ],
            'softskills': [
                ss_map[ss.name]
                for ss in opening.softSkills
            ]
        })

        opening_ids.append(r.inserted_id)
        
    return opening_ids

class BasicTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with open("server/config.json") as f:
            cls.db_string: str = json.load(f)["database_host"]

        users = DataReaderUsers.populate("examples/openings_users_softskills_confirmed/users/users_1.txt")[:10]
        openings = DataReaderOpenings.populate("examples/openings_users_softskills_confirmed/openings/openings_1.txt")[:10]
        
        with MongoClient(cls.db_string) as c:
            hs_map, ss_map = ensure_ss_and_hs(c, users, openings)
            cls.hs_map = hs_map
            cls.ss_map = ss_map
            cls.user_ids = add_users_to_db(c, hs_map, ss_map, users) 
            cls.opening_ids = add_openings_to_db(c, hs_map, ss_map, openings)
        cls.p = 0
        cls.die = True


    @classmethod
    def tearDownClass(cls):
        if cls.die:
            with MongoClient(cls.db_string) as c:
                c.drop_database("testing")


    # executed prior to each test
    def setUp(self):
        global rq, app
        BasicTests.p += 1

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        app.config['RQ_QUEUES'] = [f'default{BasicTests.p}']
        app.config['RQ_WORKER_CLASS'] = 'server.trigger_worker.TriggerWorker'

        rq.default_queue = f'default{BasicTests.p}'
        rq.init_app(app)

        self.rq = rq

        self.app = app.test_client()


    # executed after each test
    def tearDown(self):
        pass


    def test_can_add_openings(self):
        
        for opening_id in self.opening_ids[:4]:
            response = self.app.post(f'/opening/{opening_id}', follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.get_data(as_text=True), "Scheduled")

        self.rq.get_worker(f"default{BasicTests.p}").work(burst=True)


    def test_can_remove_opening(self):
        oid = self.opening_ids[0]
        
        _ = self.app.post(f'/opening/{oid}', follow_redirects=True)

        response = self.app.delete(f'/opening/{oid}', follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "Scheduled")

        self.rq.get_worker(f"default{BasicTests.p}").work(burst=True)


    def test_calculate_score(self):

        oid = self.opening_ids[0]

        _ = self.app.post(f'/opening/{oid}', follow_redirects=True)

        uid = self.user_ids[3]

        response = self.app.post(f'/score/{uid}/{oid}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "Scheduled")

        if os.path.exists("server/tests/test_calculate_score"):
            os.remove("server/tests/test_calculate_score")

        self.rq.get_worker(f"default{BasicTests.p}").work(burst=True)

        while not os.path.exists("server/tests/test_calculate_score"):
            pass

        with MongoClient(self.db_string) as c:
            database = c["testing"]
            
            asc_collection = database[ApplyScoresModel.collection_name]

            self.assertIsNotNone(asc_collection.find_one({
                "user_id": uid,
                "opening_id": oid
            }))


    def test_calculate_matches(self):
        
        for oid in self.opening_ids:
            self.app.post(f'/opening/{oid}', follow_redirects=True)

        uid = self.user_ids[5]

        response = self.app.post(f'/user_match/{uid}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "Scheduled")

        if os.path.exists("server/tests/test_calculate_matches"):
            os.remove("server/tests/test_calculate_matches")

        self.rq.get_worker(f"default{BasicTests.p}").work(burst=True)

        while not os.path.exists("server/tests/test_calculate_matches"):
            pass

        with MongoClient(self.db_string) as c:
            database = c["testing"]
            
            asc_collection = database[ServerMatchesModel.collection_name]

            self.assertIsNotNone(asc_collection.find_one({
                "user_id": uid,
            }))


if __name__ == "__main__":
    unittest.main()
