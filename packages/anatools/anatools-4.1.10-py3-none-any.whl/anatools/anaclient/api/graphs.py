"""
Graphs API calls.
"""

def getGraphs(self, workspaceId, graphId=None, name=None, email=None, staged=True, limit=100, cursor=None, filters=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getGraphs",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId,
                "name": name,
                "email": email,
                "staged": staged,
                "limit": limit,
                "cursor": cursor,
                "filters": filters
            },
            "query": """query 
                getGraphs($workspaceId: String!, $graphId: String, $name: String, $email: String, $staged: Boolean, $limit: Int, $cursor: String, $filters: GraphFilter) {
                    getGraphs(workspaceId: $workspaceId, graphId: $graphId, name: $name, member: $email, staged: $staged, limit: $limit, cursor: $cursor, filters: $filters) {
                        graphId:graphid
                        name
                        channelId
                        user
                        description
                    }
                }"""})
    return self.errorhandler(response, "getGraphs")


def createGraph(self, workspaceId, channelId, graph, name, description, staged):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createGraph",
            "variables": {
                "workspaceId": workspaceId,
                "channelId": channelId,
                "graph": graph,
                "name": name,
                "description": description,
                "staged": staged
            },
            "query": """mutation 
                createGraph($workspaceId: String!, $channelId: String!, $graph: String!, $name: String!, $description: String, $staged: Boolean) {
                    createGraph(workspaceId: $workspaceId, channelId: $channelId, graph: $graph, name: $name, description: $description, staged: $staged)
                }"""})
    return self.errorhandler(response, "createGraph")


def deleteGraph(self, workspaceId, graphId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteGraph",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId
            },
            "query": """mutation 
                deleteGraph($workspaceId: String!, $graphId: String!) {
                    deleteGraph(workspaceId: $workspaceId, graphId: $graphId)
                }"""})
    return self.errorhandler(response, "deleteGraph")


def editGraph(self, workspaceId, graphId, name=None, description=None, tags=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "editGraph",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId,
                "name": name,
                "description": description,
                "graph": graph,
                "tags": tags
            },
            "query": """mutation 
                editGraph($workspaceId: String!, $graphId: String!, $name: String, $description: String, $graph: String, $tags: [String]) {
                    editGraph(workspaceId: $workspaceId, graphId: $graphId, name: $name, description: $description, graph: $graph, tags: $tags)
                }"""})
    return self.errorhandler(response, "editGraph")


def downloadGraph(self, workspaceId, graphId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "downloadGraph",
            "variables": {
                "workspaceId": workspaceId,
                "graphId": graphId
            },
            "query": """mutation 
                downloadGraph($workspaceId: String!, $graphId: String!) {
                    downloadGraph(workspaceId: $workspaceId, graphId: $graphId)
                }"""})
    return self.errorhandler(response, "downloadGraph")


def getDefaultGraph(self, channelId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getDefaultGraph",
            "variables": {
                "channelId": channelId,
            },
            "query": """query 
                getDefaultGraph($channelId: String!) {
                    getDefaultGraph(channelId: $channelId)
                }"""})
    return self.errorhandler(response, "getDefaultGraph")
    