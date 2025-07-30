class CamxFormatter(Formatter):
    def __init__(self, project, deviceId, edgeNodeId):
        self.project = project
        self.deviceId = deviceId
        self.edgeNodeId = edgeNodeId
        
    def wrap(self, x):
        payload = {
            # CAMX payload
            "assetId": self.deviceId,
            "dateTime": datetime.now(timezone.utc).isoformat(),
            "dataItemId": self.edgeNodeId,
            "value": None,
            "operatorId": "<AIMPF USER>",
            "itemInstanceId": str(uuid4()),
            "projectLabel": str(self.project),
        }
        try:
            payload["value"] = x
            return json.dumps(payload)
        except:
            payload["value"] = str(x)
            return json.dumps(payload)
    
    def unwrap(self, x):
        return json.loads(x)["value"]