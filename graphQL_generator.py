from os import system
from typing import Dict
from util.readers.reader import DataReaderUsers, DataReaderOpenings
import random
from python_graphql_client import GraphqlClient

# Asynchronous request
import asyncio
from bson.objectid import ObjectId


client = GraphqlClient(endpoint="http://localhost:3000/graphql")

users_path = "examples/openings_users/users/users_2.txt"
openings_path = "examples/openings_users/openings/openings_2.txt"

users = DataReaderUsers.populate(filename=users_path)
openings = DataReaderOpenings.populate(filename=openings_path)

set_of_soft_skill_names = set()
set_of_hard_skill_names = set()

for opening in openings:
    for soft_skill in opening.softSkills:
        set_of_soft_skill_names.add(soft_skill.name)

    for hard_skill in opening.hardSkills:
        set_of_hard_skill_names.add(hard_skill.name)

for user in users:
    for soft_skill in user.softSkills:
        set_of_soft_skill_names.add(soft_skill.name)

    for hard_skill in user.hardSkills:
        set_of_hard_skill_names.add(hard_skill.name)

soft_skill_name_to_id_string : Dict[str, str] = {}
for soft_skill_name in set_of_soft_skill_names:
    mutation_query = """
        mutation ($name: String!) {
            newSoftskill(
            softskill:
                {
                    name:$name
                }
            )
            {
                _id
            }
        }
    """
    variables = {"name": soft_skill_name}

    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(client.execute_async(query=mutation_query, variables=variables))
    print(data)

    soft_skill_name_to_id_string[soft_skill_name] = data['data']['newSoftskill']['_id']

print(soft_skill_name_to_id_string)

hard_skill_name_to_id_string : Dict[str, str] = {}
for hard_skill_name in set_of_hard_skill_names:
    mutation_query = """
        mutation ($name: String!) {
            registerHardSkill(
            skill:
                {
                    name:$name
                }
            )
            {
                _id
            }
        }
    """
    variables = {"name": hard_skill_name}

    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(client.execute_async(query=mutation_query, variables=variables))
    print(data)

    hard_skill_name_to_id_string[hard_skill_name] = data['data']['registerHardSkill']['_id']

print(hard_skill_name_to_id_string)

for user in users:

    password_parts = [
        random.choice(["A", "B", "C", "D", "0", "1"])
        for _ in range(10)
    ]

    password = ''.join(password_parts)

    mutation_query = """
        mutation ($email:String!, $name: String!, $password:String!, $ss: [UserSoftskillInput!], $hs: [ID!]) {
            newUser(
            user:
                {
                    email:$email,
                    name: $name,
                    password: $password,
                    softSkills: $ss,
                    hardSkills: $hs
                }
            )
            {
                _id
            }
        }
    """

    variables = {
        "name": user.name,
        "email": user.name + "@unique.com",
        "password": password,
        "ss": [
            {
                "score": 10,
                "softskillId": str(ObjectId(soft_skill_name_to_id_string[softSkill.name])),
                "visible": True
            }
            for softSkill in user.softSkills
        ],
        "hs": [
            str(ObjectId(hard_skill_name_to_id_string[hardSkill.name]))
            for hardSkill in user.hardSkills
        ],
    }


    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(client.execute_async(query=mutation_query, variables=variables))
    a_user_id_string: str = data['data']['newUser']['_id']
    print(data)


mutation_query = """
        mutation ($manager: ID!) {
            newProject(
            project:
                {
                    description: "A description",
                    location: {
                        address: "Avenida da Liberdade",
                        position: {
                            latitude: 10,
                            longitude:24
                        }    
                    },
                    manager: $manager,
                    scope: "Do all the things",
                    title: "Here is a title"
                }
            )
            {
                _id
            }
        }
    """

variables = {
    "manager": a_user_id_string,
}

loop = asyncio.get_event_loop()
data = loop.run_until_complete(client.execute_async(query=mutation_query, variables=variables))
print(data)
a_project_id_str: str = data['data']['newProject']['_id']

for opening in openings:
    mutation_query = """
            mutation ($area: String!, $project_id: ID!, $ss: [ID!], $hs: [ID!]) {
                createOpening(
                opening:
                    {
                        area: $area,
                        availability: {
                            type: FullTime
                        },
                        project: $project_id,
                        softskills: $ss,
                        hardskills: $hs
                    }
                )
                {
                    _id
                }
            }
        """

    variables = {
        "area": opening.area,
        "project_id": a_project_id_str,
        "ss": [
            str(ObjectId(soft_skill_name_to_id_string[softSkill.name]))
            for softSkill in opening.softSkills
        ],
        "hs": [
            str(ObjectId(hard_skill_name_to_id_string[hardSkill.name]))
            for hardSkill in opening.hardSkills
        ]
    }

    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(client.execute_async(query=mutation_query, variables=variables))
    print(data)