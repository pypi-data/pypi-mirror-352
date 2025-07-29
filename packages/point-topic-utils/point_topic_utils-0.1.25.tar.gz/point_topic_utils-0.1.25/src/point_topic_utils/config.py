from dataclasses import dataclass
from typing import Optional
from point_topic_utils.get_secrets import get_secrets

mongodb_uri = get_secrets("mongodb_url_research_app")["mongodb_url_research_app"]

@dataclass
class MongoDBConfig:
    uri: str = mongodb_uri
    database: str = "research-app"
    collection: str = "OversightProjects"