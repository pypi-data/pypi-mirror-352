"""
Workspace Functions
"""

def get_workspace(self):
    """Get the workspace ID of the current workspace."""
    return self.workspace

def set_workspace(self, workspaceId):
    """Set the workspace to the one you wish to work in.

    Parameters
    ----------
    workspaceId : str
        Workspace ID for the workspace you wish to work in.
    """
    from anatools.lib.print import print_color

    self.check_logout()
    if workspaceId is None: raise Exception('WorkspaceId must be specified.')
    workspaces = self.get_workspaces(workspaceId=workspaceId)
    if len(workspaces) == 0: raise Exception(f'Workspace with workspaceId {workspaceId} not found!')
    organizations = self.get_organizations(organizationId=workspaces[0]['organizationId'])
    if organizations[0]['expired']: raise Exception(f'Organization with organizationId {workspaces[0]["organizationId"]} is expired!')
    self.workspace = workspaces[0]['workspaceId']
    self.organization = workspaces[0]['organizationId']
    if self.interactive: print_color(f'The current organization is: {self.organization}\nThe current workspace is: {self.workspace}', '91e600')
    return True


def get_workspaces(self, organizationId=None, workspaceId=None, filters=None):
    """Shows list of workspaces with id, name, and owner data.
    
    Parameters
    ----------
    organizationId : str
        Organization ID to filter on. Optional
    workspaceId : str
        Workspace ID to filter on. Optional
    filters: dict
        Filters that limit output to entries that match the filter 

    Returns
    -------
    list[dict]
        Workspace data for all workspaces for a user.
    """  
    if self.check_logout(): return
    full = []
    done = False
    limit = 100
    cursor = None
    while not done:
        ret = self.ana_api.getWorkspaces(organizationId, workspaceId, limit=limit, cursor=cursor, filters=filters)
        if ret == False:
            return False
        if len(ret) == 0:
            done = True
        else:
            full.extend(ret)
            cursor = ret[-1]["workspaceId"]
            if len(ret) < limit:
                done = True
    if organizationId is None and workspaceId is None:
        self.workspaces = full
        return self.workspaces
    else:
        workspaces = full
        return workspaces


def create_workspace(self, name, channelIds=[], volumeIds=[], code=None, organizationId=None):
    """Create a new workspace with specific channels.
    
    Parameters
    ----------
    name : str    
        New workspace name.
    channelIds : list[str]
        List of channel ids to add to workspace.
    volumeIds: list[str]
        List of volume ids that the workspace will have access to.
    code: str
        Content code that used for creating a workspace
    organizationId : str
        Organization ID. Defaults to current if not specified.  
    
    Returns
    -------
    str
        Workspace ID if creation was successful. Otherwise returns message.
    """    
    if self.check_logout(): return
    if name is None: raise ValueError("Name must be provided")
    if code is None: code = ''
    if organizationId is None: organizationId = self.organization
    return self.ana_api.createWorkspace(organizationId=organizationId, name=name, channelIds = channelIds, volumeIds = volumeIds, code=code)


def delete_workspace(self, workspaceId=None, prompt=True):
    """Delete an existing workspace. 
    
    Parameters
    ----------
    workspaceId : str    
        Workspace ID for workspace to get deleted. Deletes current workspace if not specified. 
    prompt: bool
        Set to True if avoiding prompts for deleting workspace.
    
    Returns
    -------
    str
        Success or failure message if workspace was sucessfully removed.
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace 
    if prompt:
        response = input('This will remove any configurations, graphs and datasets associated with this workspace.\nAre you certain you want to delete this workspace? (y/n)  ')
        if response not in ['Y', 'y', 'Yes', 'yes']: return
    return self.ana_api.deleteWorkspace(workspaceId=workspaceId)


def edit_workspace(self, name=None, channelIds=None, volumeIds=None, ganIds=None, mapIds=None, workspaceId=None):
    """Edit workspace information. 
    
    Parameters
    ----------
    name : str    
        New name to replace old one.
    channelIds: list[str]
        Names of channels that the workspace will have access to.
    volumeIds: list[str]
        List of volume ids that the workspace will have access to.
    ganIds: list[str]
        List of GAN ids that the workspace will have access to.
    mapIds: list[str]
        List of map ids that the workspace will have access to.
    workspaceId : str    
        Workspace ID for workspace to update.
    
    Returns
    -------
    bool
        Success or failure message if workspace was sucessfully updated.
    """  
    if self.check_logout(): return
    if name is None and channelIds is None and volumeIds is None and ganIds is None and mapIds is None: return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.editWorkspace(workspaceId=workspaceId, name=name, channelIds=channelIds, volumeIds=volumeIds, ganIds=ganIds, mapIds=mapIds)


def remove_workspace_invitation(self, email, workspaceId=None, invitationId=None ):
    """Remove a invitation from an existing organization.
    
    Parameters
    ----------
    email : str
        Invitation email to remove.
    workspaceId: str
        Workspace ID to remove member from. Removes from current organization if not specified.
    inviteId: str
        Invitation ID to remove invitation from. Removes from current organization if not specified.
    
    Returns
    -------
    str
        Response status if member got removed from organization succesfully. 
    """
    if self.check_logout(): return
    if email is None: raise ValueError("Email must be provided.")
    if invitationId is None: raise ValueError("No invitation found.")
    if workspaceId is None: workspaceId = self.organization
    return self.ana_api.removeMember(email=email, workspaceId=workspaceId, organizationId=None, invitationId=invitationId)