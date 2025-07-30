"""
API Keys calls.
"""

def getAPIKeyContext(self, apiKey):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAPIKeyContext",
            "variables": {
                "apiKey": apiKey
            },
            "query": """query getAPIKeyContext($apiKey: String!) {
                            getAPIKeyContext(apiKey: $apiKey) {
                                name
                                scope
                                organizationId
                                workspaceId
                                createdAt
                                expiresAt
                            }
                        }"""})
    return self.errorhandler(response, "getAPIKeyContext")


def getAPIKeys(self):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAPIKeys",
            "query": """query getAPIKeys {
                            getAPIKeys {
                                name
                                scope
                                organizationId
                                workspaceId
                                createdAt
                                expiresAt
                            }
                        }"""})
    return self.errorhandler(response, "getAPIKeys")


def createAPIKey(self, name, scope="user", organizationId=None, workspaceId=None, expires=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createAPIKey",
            "variables": {
                "name": name,
                "scope": scope,
                "organizationId": organizationId,
                "workspaceId": workspaceId,
                "expiresAt": expires
            },
            "query": """mutation createAPIKey($name: String!, $scope: String, $organizationId: String, $workspaceId: String, $expiresAt: String) {
                            createAPIKey(name: $name, scope: $scope, organizationId: $organizationId, workspaceId: $workspaceId, expiresAt: $expiresAt)
                        }"""})
    return self.errorhandler(response, "createAPIKey")


def deleteAPIKey(self, name):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteAPIKey",
            "variables": {
                "name": name
            },
            "query": """mutation deleteAPIKey($name: String!) {
                            deleteAPIKey(name: $name)
                        }"""})
    return self.errorhandler(response, "deleteAPIKey")


def getAPIKeyData(self, name):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "getAPIKeyData",
            "variables": {
                "name": name
            },
            "query": """query getAPIKeyData($name: String!) {
                            getAPIKeyData(name: $name) {
                                name
                                scope
                                organizationId
                                workspaceId
                                createdAt
                                expiresAt
                            }
                        }"""})
    return self.errorhandler(response, "getAPIKeyData")
