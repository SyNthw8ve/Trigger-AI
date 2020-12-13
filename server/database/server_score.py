from mongoengine import Document
from mongoengine.base.fields import ObjectIdField
from mongoengine.fields import FloatField


class ServerScore(Document):
    user_id = ObjectIdField(required=True)
    opening_id = ObjectIdField(required=True)
    similarity_score = FloatField(min_value=0, max_value=1, required=True)
    quality_score = FloatField(min_value=0, max_value=1, required=True)
    final_score = FloatField(min_value=0, max_value=1, required=True)
