from dataclasses import dataclass
from datetime import datetime
from typing import Optional,Any
from dataclasses_json import LetterCase, dataclass_json

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class DeviceRepresentation:
    client: Any = None

    # Informations de base
    id: Optional[str] = None
    type: Optional[str] = None
    state: Optional[str] = None
    name: Optional[str] = None
    online: Optional[bool] = None
    serial_number: Optional[str] = None
    computer_model: Optional[str] = None
    
    # Informations système
    os: Optional['OS'] = None
    bios_version: Optional[str] = None
    system_drive_total_size: Optional[int] = None
    system_drive_free_space: Optional[int] = None
    physical_memory_total_size: Optional[int] = None
    physical_memory_free: Optional[int] = None
    disc_encryption_enabled: Optional[bool] = None
    
    # Informations réseau
    dns_address: Optional[str] = None
    firewall_state: Optional[str] = None
    ip_addresses: Optional[str] = None
    ipv6_addresses: Optional[str] = ''
    public_ip_address: Optional[str] = ''
    mac_addresses: Optional[str] = ''
    wins_address: Optional[str] = ''
    public_internet: bool = False
    
    # Informations utilisateur
    last_user: Optional[str] = ''
    current_user_admin: bool = False
    user_principal_name: Optional[str] = ''
    active_directory_group: Optional[str] = ''
    
    # Informations de sécurité
    client_version: Optional[str] = ''
    malware_state: Optional[str] = ''  # TODO: Créer enum MalwareState
    malware_db_version: Optional[str] = ''
    malware_db_update_timestamp: Optional[datetime] = None
    protection_status_overview: Optional[str] = ''  # TODO: Créer enum ProtectionStatus
    protection_status: Optional[str] = ''  # TODO: Créer enum ProtectionStatus
    dataguard_state: Optional[str] = ''  # TODO: Créer enum DataguardState
    device_control_state: Optional[str] = ''  # TODO: Créer enum DeviceControlState
    application_control_state: Optional[str] = ''  # TODO: Créer enum ApplicationControlState
    
    # Informations de mise à jour
    patch_overall_state: Optional[str] = ''
    patch_last_scan_timestamp: Optional[datetime] = None
    patch_last_install_timestamp: Optional[datetime] = None
    
    # Informations de profil
    profile_name: Optional[str] = ''
    profile_state: Optional[str] = ''
    registration_timestamp: Optional[datetime] = None
    status_update_timestamp: Optional[datetime] = None
    
    # Informations supplémentaires
    company: Optional['Company'] = None
    vm_risk_score: Optional[int] = None
    edr_incidents: Optional['EdrIncidents'] = None
    subscription: Optional['Subscription'] = None


@dataclass
class Company:
    id: Optional[str]  = None
    name: Optional[str] = None
    type: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class OS:
    name: str = None
    version: str = None
    security_patch: Optional[str] = None


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class EdrIncidents:
    risk_low: int = 0
    risk_medium: int = 0
    risk_high: int = 0
    risk_severe: int = 0    

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class Subscription:
    key: str
    name: str
    product_variant: str