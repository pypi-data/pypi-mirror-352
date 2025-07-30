allowed_organization_types = ['company', 'partner']
allowed_device_types = ['computer', 'connector', 'mobile']
allowed_protection_status_overview = ['isolated', 'inactive', 'critical', 'warning', 'allOk']
allowed_operations = ['isolateFromNetwork', 'releaseFromNetworkIsolation', 'assignProfile', 'scanForMalware', 'showMessage', 'turnOnFeature', 'collectDiagnosticFile']
allowed_engines = ['AMSI', 'activityMonitor', 'activityMonitorClientProtection', 'applicationControl', 'browsingProtection', 'cloudIdentityAzure', 'cloudWorkloadAzure', 'connectionControl', 'connector', 'dataGuard', 'deepGuard', 'deviceControl', 'edr', 'emailBreach', 'emailScan', 'fileScanning', 'firewall', 'inboxRuleScan', 'integrityChecker', 'oneDriveScan', 'realtimeScanning', 'reputationBasedBrowsing', 'setting', 'sharePointScan', 'systemEventsLog', 'tamperProtection', 'teamsScan', 'webContentControl', 'webTrafficScanning', 'xFence', 'xmRecommendation']
allowed_engine_groups = ['edr', 'epp', 'ecp', 'xm']
allowed_incident_statuses = ['new', 'acknowledged', 'inProgress', 'monitoring', 'closed', 'waitingForCustomer']
allowed_incident_resolutions = ['unconfirmed', 'confirmed', 'falsePositive', 'merged', 'autoUnconfirmed', 'autoFalsePositive', 'securityTest', 'acceptedRisk', 'acceptedBehavior']
allowed_risk_levels = ['info', 'low', 'medium', 'high', 'severe']
allowed_response_action_types = ['killThread', 'killProcess', 'fullMemoryDump', 'netstat', 'enumerateProcesses', 'endCurrentSession', 'resetPassword', 'blockUserAccess']
allowed_update_severities = ['critical', 'important', 'moderate', 'low', 'unclassified']
allowed_update_categories = ['security', 'nonSecurity', 'servicePack', 'securityTool', 'none']
allowed_features = ['debugLogging']
allowed_device_states = ['blocked', 'inactive']
allowed_devices_group_by = ['protectionStatus', 'patchOverallState', 'firewallState', 'malwareState']
allowed_security_events_severities = ['critical', 'warning', 'info']
allowed_security_events_group_by = ['engine', 'url', 'alertType', 'deviceId', 'infectionName', 'categories', 'appliedRule', 'filePath', 'description']
allowed_response_action_states = ['created', 'initializing', 'sending', 'running', 'cancelling', 'finished']
allowed_response_action_results = ['succeeded', 'failed', 'timeout', 'cancelled']
allowed_response_action_orders = ['asc', 'desc']

def check_allowed_values(allowed_values, value, list_allowed=True):
    if isinstance(value, (list, set, tuple)):
        if not list_allowed:
            raise ValueError(f"Invalid value: {value}, list are not allowed")
        if not all(v in allowed_values for v in value):
            return False
    elif value not in allowed_values:
        return False
    return True