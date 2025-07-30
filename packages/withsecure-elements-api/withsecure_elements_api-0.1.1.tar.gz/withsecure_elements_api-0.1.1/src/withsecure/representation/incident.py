from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config
from datetime import datetime

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class IncidentRepresentation:
    id: str = field(metadata=config(field_name="incidentId"))
    organization_id: str
    severity: str
    risk_level: str
    risk_score: float
    incident_public_id: str
    created_timestamp: datetime
    name: str
    initial_received_timestamp: datetime
    resolution: str
    updated_timestamp: datetime
    status: str
    categories: list[str]
    sources: list[str]
