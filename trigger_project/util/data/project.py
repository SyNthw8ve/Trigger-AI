from typing import List

from ...models.hardskill import Hardskill
from ...models.opening import Opening
from ...models.project import Project
from ...models.softskill import Softskill
from ...transformers.opening_transformer import OpeningTransformer

def sample_projects(start_id: int) -> List[Project]:
    eid = start_id + 1
    opening_transformer = OpeningTransformer()

    def create_solo() -> Project:
        nonlocal eid
        openings = [
            Opening(
                str(eid),
                hardSkills=[
                    Hardskill("Scraping"),
                    Hardskill("Computer Science"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Resilience"),
                ]
            )
        ]

        opening_instances = [
            opening_transformer.transform(opening)
            for opening in openings
        ]

        eid += len(opening_instances)

        return Project("SoloWork", openings=opening_instances)

    def create_altice() -> Project:
        nonlocal eid
        openings = [
            Opening(
                str(eid),
                hardSkills=[
                    Hardskill("Machine Learning"),
                    Hardskill("Python"),
                    Hardskill("Computer Science"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                ]
            ),
            Opening(
                str(eid + 1),
                hardSkills=[
                    Hardskill("Machine Learning"),
                    Hardskill("Python"),
                    Hardskill("Computer Science"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                ]
            )

        ]

        opening_instances = [
            opening_transformer.transform(opening)
            for opening in openings
        ]

        eid += len(opening_instances)

        return Project("Altice", openings=opening_instances)

    def create_trigger() -> Project:
        nonlocal eid
        openings = [
            Opening(
                str(eid),
                hardSkills=[
                    Hardskill("Software development"),
                    Hardskill("Web Application"),
                    Hardskill("JavaScript"),
                    Hardskill("Typescript"),
                    Hardskill("Web"),
                    Hardskill("MongoDB"),
                    Hardskill("Python"),
                    Hardskill("Machine Learning"),
                    Hardskill("Computer Science"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            ),
            Opening(
                str(eid + 1),
                hardSkills=[
                    Hardskill("Web Application"),
                    Hardskill("JavaScript"),
                    Hardskill("Typescript"),
                    Hardskill("Web"),
                    Hardskill("MongoDB"),
                    Hardskill("Angular"),
                    Hardskill("Python"),
                    Hardskill("Machine Learning"),
                    Hardskill("Computer Science"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            ),
            Opening(
                str(eid + 2),
                hardSkills=[
                    Hardskill("Figma"),
                    Hardskill("Illustrator"),
                    Hardskill("Colour Theory"),
                    Hardskill("Web"),
                    Hardskill("CSS"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            ),
            Opening(
                str(eid + 3),
                hardSkills=[
                    Hardskill("Figma"),
                    Hardskill("Illustrator"),
                    Hardskill("Boostrap"),
                    Hardskill("Web"),
                    Hardskill("HTML"),
                    Hardskill("CSS"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                    Softskill("Leadership"),
                ]
            ),
            Opening(
                str(eid + 4),
                hardSkills=[
                    Hardskill("Sociology"),
                    Hardskill("Personality Theory"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                    Softskill("Emotional Intelligence"),
                ]
            ),
            Opening(
                str(eid + 5),
                hardSkills=[
                    Hardskill("Business Planning"),
                    Hardskill("Developing Policies"),
                    Hardskill("Project Management Staff Development"),
                    Hardskill("Advertising"),
                ],
                softSkills=[
                    Softskill("Ethics"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                    Softskill("Emotional Intelligence"),
                ]
            )
        ]

        opening_instances = [
            opening_transformer.transform(opening)
            for opening in openings
        ]

        eid += len(opening_instances)

        return Project("Trigger", openings=opening_instances)

    def create_university_site() -> Project:
        nonlocal eid
        openings = [
            Opening(
                str(eid),
                hardSkills=[
                    Hardskill("Software development"),
                    Hardskill("Web Application"),
                    Hardskill("JavaScript"),
                    Hardskill("Typescript"),
                    Hardskill("Web"),
                    Hardskill("MongoDB"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            ),
            Opening(
                str(eid + 1),
                hardSkills=[
                    Hardskill("Web Application"),
                    Hardskill("JavaScript"),
                    Hardskill("Angular"),
                    Hardskill("Typescript"),
                    Hardskill("Web"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                    Softskill("Leadership"),
                ]
            ),
            Opening(
                str(eid + 2),
                hardSkills=[
                    Hardskill("Figma"),
                    Hardskill("Illustrator"),
                    Hardskill("Colour Theory"),
                    Hardskill("Web"),
                    Hardskill("CSS"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            ),
            Opening(
                str(eid + 3),
                hardSkills=[
                    Hardskill("Figma"),
                    Hardskill("Illustrator"),
                    Hardskill("Boostrap"),
                    Hardskill("Web"),
                    Hardskill("HTML"),
                    Hardskill("CSS"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                    Softskill("Leadership"),
                ]
            ),
        ]

        opening_instances = [
            opening_transformer.transform(opening) 
            for opening in openings
        ]

        eid += len(opening_instances)

        return Project("UESite", openings=opening_instances)

    def create_wind_farm() -> Project:
        nonlocal eid
        openings = [
            Opening(
                str(eid),
                hardSkills=[
                    Hardskill("Construction"),
                    Hardskill("Climbing"),
                ],
                softSkills=[
                    Softskill("Resilience"),
                    Softskill("Teamwork"),
                ]
            ),
            Opening(
                str(eid + 1),
                hardSkills=[
                    Hardskill("Construction"),
                    Hardskill("Climbing"),
                ],
                softSkills=[
                    Softskill("Resilience"),
                    Softskill("Teamwork"),
                ]
            ),
            Opening(
                str(eid + 2),
                hardSkills=[
                    Hardskill("Construction"),
                    Hardskill("Climbing"),
                ],
                softSkills=[
                    Softskill("Resilience"),
                    Softskill("Teamwork"),
                ]
            ),
            Opening(
                str(eid + 3),
                hardSkills=[
                    Hardskill("Construction"),
                    Hardskill("Climbing"),
                ],
                softSkills=[
                    Softskill("Resilience"),
                    Softskill("Teamwork"),
                ]
            ),
            Opening(
                str(eid + 4),
                hardSkills=[
                    Hardskill("Mechanical Engineering"),
                    Hardskill("Architecture"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            ),
            Opening(
                str(eid + 5),
                hardSkills=[
                    Hardskill("Mechanical Engineering"),
                    Hardskill("Architecture"),
                ],
                softSkills=[
                    Softskill("Complex Thinking"),
                    Softskill("Teamwork"),
                    Softskill("Leadership"),
                    Softskill("Communication"),
                ]
            ),
            Opening(
                str(eid + 6),
                hardSkills=[
                    Hardskill("Budgeting"),
                    Hardskill("Developing Policies"),
                    Hardskill("Finances"),
                    Hardskill("Advertising"),
                ],
                softSkills=[
                    Softskill("Ethics"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            )
        ]

        opening_instances = [
            opening_transformer.transform(opening)
            for opening in openings
        ]

        eid += len(opening_instances)

        return Project("ItsWindy", openings=opening_instances)

    def create_skyscraper_prototype() -> Project:
        nonlocal eid
        openings = [
            Opening(
                str(eid),
                hardSkills=[
                    Hardskill("Architecture"),
                    Hardskill("Visual Composition"),
                ],
                softSkills=[
                    Softskill("Proactivity"),
                    Softskill("Complex Thinking"),
                    Softskill("Resilience"),
                    Softskill("Teamwork"),
                ]
            ),
            Opening(
                str(eid + 1),
                hardSkills=[
                    Hardskill("Architecture"),
                    Hardskill("Visual Composition"),
                ],
                softSkills=[
                    Softskill("Proactivity"),
                    Softskill("Complex Thinking"),
                    Softskill("Resilience"),
                    Softskill("Teamwork"),
                    Softskill("Leadership"),
                ]
            ),
            Opening(
                str(eid + 2),
                hardSkills=[
                    Hardskill("Budgeting"),
                    Hardskill("Developing Policies"),
                    Hardskill("Finances"),
                    Hardskill("Advertising"),
                ],
                softSkills=[
                    Softskill("Ethics"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            )
        ]

        opening_instances = [
            opening_transformer.transform(opening)
            for opening in openings
        ]

        eid += len(opening_instances)

        return Project("Sky Evora", openings=opening_instances)

    def create_think_tank() -> Project:
        nonlocal eid
        openings = [
            Opening(
                str(eid),
                hardSkills=[
                    Hardskill("Architecture"),
                    Hardskill("Visual Composition"),
                ],
                softSkills=[
                    Softskill("Proactivity"),
                    Softskill("Complex Thinking"),
                    Softskill("Resilience"),
                    Softskill("Teamwork"),
                ]
            ),
            Opening(
                str(eid + 2),
                hardSkills=[
                    Hardskill("Budgeting"),
                    Hardskill("Developing Policies"),
                    Hardskill("Finances"),
                    Hardskill("Advertising"),
                ],
                softSkills=[
                    Softskill("Ethics"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            ),
            Opening(
                str(eid + 3),
                hardSkills=[
                    Hardskill("Psychology"),
                ],
                softSkills=[
                    Softskill("Ethics"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            )
            ,
            Opening(
                str(eid + 4),
                hardSkills=[
                    Hardskill("Math"),
                    Hardskill("Military Training"),
                ],
                softSkills=[
                    Softskill("Ethics"),
                    Softskill("Teamwork"),
                    Softskill("Communication"),
                ]
            )
        ]

        opening_instances = [
            opening_transformer.transform(opening)
            for opening in openings
        ]

        eid += len(opening_instances)

        return Project("ThinkTank", openings=opening_instances)

    return [
        create_solo(),  # ? transdisciplinarity expected, only 1 opening
        create_altice(),  # low transdisciplinarity expected
        create_trigger(),  # medium/high transdisciplinarity expected
        create_university_site(),  # low/medium transdisciplinarity expected
        create_wind_farm(),  # low/medium transdisciplinarity expected
        create_skyscraper_prototype(),  # low transdisciplinarity expected
        create_think_tank(),  # high transdisciplinarity expected
    ]
