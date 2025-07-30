from pydantic import AwareDatetime, BaseModel


class Observation(BaseModel):
    node_id: str
    observation_type: str
    data: dict[AwareDatetime, float]
