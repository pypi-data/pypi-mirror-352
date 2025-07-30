"""
Previews API calls.
"""

def getPreview(self, workspaceId, previewId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getPreview",
            "variables": {
                "workspaceId": workspaceId,
                "previewId": previewId
            },
            "query": """query 
                getPreview($workspaceId: String!, $previewId: String!) {
                    getPreview(workspaceId: $workspaceId, previewId: $previewId) {
                        previewId
                        workspaceId
                        status
                        thumbnail
                        updatedAt
                    }
                }"""})
    return self.errorhandler(response, "getPreview")


def createPreview(self, workspaceId, graphId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createPreview",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId
            },
            "query": """mutation 
                createPreview($workspaceId: String!, $graphId: String!) {
                    createPreview(workspaceId: $workspaceId, graphId: $graphId)
                }"""})
    return self.errorhandler(response, "createPreview")

