"""
Channels API calls.
"""

def createRemoteDevelopment(self, channelId=None, channelVersion=None, instanceType=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "createRemoteDevelopment",
            "variables": {
                "channelId": channelId,
                "channelVersion": channelVersion,
                "instanceType": instanceType
            },
            "query": """mutation
                createRemoteDevelopment($channelId: String!, $channelVersion: String, $instanceType: String) {
                    createRemoteDevelopment(channelId: $channelId, channelVersion: $channelVersion, instanceType: $instanceType) {
                        organizationId
                        channelId
                        editorUrl
                        editorSessionId
                        instanceType
                        status {
                            state
                            message
                        }
                    }
                }"""})
    return self.errorhandler(response, "createRemoteDevelopment")


def deleteRemoteDevelopment(self, editorSessionId):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "deleteRemoteDevelopment",
            "variables": {
                "editorSessionId": editorSessionId,
            },
            "query": """mutation
                deleteRemoteDevelopment($editorSessionId: String!) {
                    deleteRemoteDevelopment(editorSessionId: $editorSessionId) {
                        organizationId
                        editorSessionId
                        status {
                            state
                            message
                        }
                    }
                }"""})
    return self.errorhandler(response, "deleteRemoteDevelopment")


def listRemoteDevelopment(self, organizationId=None):
    response = self.session.post(
        url = self.url, 
        headers = self.headers, 
        json = {
            "operationName": "listRemoteDevelopment",
            "variables": {
                "organizationId": organizationId
            },
            "query": """query
                listRemoteDevelopment($organizationId: String) {
                    listRemoteDevelopment(organizationId: $organizationId) {
                        organizationId
                        organization
                        channel
                        channelId
                        editorUrl
                        editorSessionId
                        instanceType
                        sshPort
                        status {
                            state
                            message
                        }
                        users
                        createdAt
                        createdBy
                        updatedAt
                    }
                }"""})
    return self.errorhandler(response, "listRemoteDevelopment")


def stopRemoteDevelopment(self, editorSessionId):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "stopRemoteDevelopment",
            "variables": {
                "editorSessionId": editorSessionId,
            },
            "query": """mutation
                stopRemoteDevelopment($editorSessionId: String!) {
                    stopRemoteDevelopment(editorSessionId: $editorSessionId) {
                        organizationId
                        editorSessionId
                        editorUrl
                        status {
                            state
                            message
                        }
                    }
                }"""})
    return self.errorhandler(response, "stopRemoteDevelopment")


def startRemoteDevelopment(self, editorSessionId):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "startRemoteDevelopment",
            "variables": {
                "editorSessionId": editorSessionId,
            },
            "query": """mutation
                startRemoteDevelopment($editorSessionId: String!) {
                    startRemoteDevelopment(editorSessionId: $editorSessionId) {
                        organizationId
                        editorSessionId
                        editorUrl
                        status {
                            state
                            message
                        }
                    }
                }"""})
    return self.errorhandler(response, "startRemoteDevelopment")


def inviteRemoteDevelopment(self, editorSessionId, email):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "inviteRemoteDevelopment",
            "variables": {
                "editorSessionId": editorSessionId,
                "email": email
            },
            "query": """mutation
                inviteRemoteDevelopment($editorSessionId: String!, $email: String!) {
                    inviteRemoteDevelopment(editorSessionId: $editorSessionId, email: $email)
                }"""
        })
    return self.errorhandler(response, "inviteRemoteDevelopment")


def createSSHKey(self, name, key):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "createSSHKey",
            "variables": {
                "name": name,
                "key": key
            },
            "query": """mutation
                createSSHKey($name: String!, $key: String!) {
                    createSSHKey(name: $name, key: $key)
                }"""})
    return self.errorhandler(response, "createSSHKey")


def deleteSSHKey(self, name):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "deleteSSHKey",
            "variables": {
                "name": name
            },
            "query": """mutation
                deleteSSHKey($name: String!) {
                    deleteSSHKey(name: $name)
                }"""})
    return self.errorhandler(response, "deleteSSHKey")


def getSSHKeys(self):
    response = self.session.post(
        url = self.url,
        headers = self.headers,
        json = {
            "operationName": "getSSHKeys",
            "variables": {},
            "query": """query
                getSSHKeys {
                    getSSHKeys {
                        name
                        key
                        createdAt
                    }
                }"""})
    return self.errorhandler(response, "getSSHKeys")