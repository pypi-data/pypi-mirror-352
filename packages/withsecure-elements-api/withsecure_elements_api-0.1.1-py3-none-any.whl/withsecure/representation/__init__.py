import dataclasses_json
from datetime import datetime

from .device import DeviceRepresentation
from .incident import IncidentRepresentation
from .organization import OrganizationRepresentation


__all__ = [
    'DeviceRepresentation',
    'IncidentRepresentation',
    'OrganizationRepresentation'
]


dataclasses_json.cfg.global_config.encoders[datetime] = datetime.isoformat
dataclasses_json.cfg.global_config.decoders[datetime] = datetime.fromisoformat
