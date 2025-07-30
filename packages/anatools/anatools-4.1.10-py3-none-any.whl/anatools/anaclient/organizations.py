"""
Organization Functions
"""

def get_organization(self):
    """Get organization id of current organization. 
    
    Returns
    -------
    str
        Organization ID of current workspace.
    """
    if self.check_logout(): return
    return self.organization


def set_organization(self, organizationId, workspaceId=None):
    """Set the organization (and optionally a workspace) to the one you wish to work in.

    Parameters
    ----------
    organizationId : str
        Organization ID for the organization you wish to work in.
    workspaceId : str, optional
        Workspace ID for the workspace you wish to work in. Uses default workspace if this is not set.
    """
    from anatools.lib.print import print_color

    self.check_logout()
    if organizationId is None: raise Exception('OrganizationId must be specified.')
    organizations = self.get_organizations(organizationId=organizationId)
    if len(organizations) == 0: raise Exception(f'Organization with organizationId {organizationId} not found!')
    elif organizations[0]['expired']: raise Exception(f'Organization with organizationId {organizationId} is expired!')
    self.organization = organizations[0]['organizationId']
    workspaces = self.get_workspaces(organizationId=self.organization)
    if len(workspaces) == 0:
        if self.interactive: raise Exception("No workspaces available, please contact support@rendered.ai.");
    if workspaceId:
        if workspaceId not in [w['workspaceId'] for w in workspaces]:
            raise Exception(f"Workspace {workspaceId} not found in organization {organizationId}.")
        self.workspace = workspaceId
    self.workspace = workspaces[0]['workspaceId']
    if self.interactive: print_color(f'The current organization is: {self.organization}\nThe current workspace is: {self.workspace}', '91e600')
    return True


def get_organizations(self, organizationId=None):
    """Shows the organizations the user belongs to and the user's role in that organization.
    
    Returns
    -------
    list[dict]
        Information about the organizations you belong to. 
    """  
    if self.check_logout(): return
    full = []
    done = False
    limit = 100
    cursor = None
    while not done:
        ret = self.ana_api.getOrganizations(organizationId, limit=limit, cursor=cursor)
        if ret == False:
            return False
        if len(ret) == 0:
            done = True
        else:
            full.extend(ret)
            cursor = ret[-1]["organizationId"]
            if len(ret) < limit:
                done = True
    if organizationId is None:
        self.organizations = full
        return self.organizations
    else:
        organizations = full
        return organizations


def edit_organization(self, name, organizationId=None):
    """Update the organization name. Uses current organization if no organizationId provided.
    
    Parameters
    ----------
    name : str
        Name to update organization to.
    organizationId : str
        Organization Id to update.
    
    Returns
    -------
    bool
        True if organization was edited successfully, False otherwise.
    """  
    if self.check_logout(): return
    if name is None: return
    if organizationId is None: organizationId = self.organization
    return self.ana_api.editOrganization(organizationId, name)


def get_organization_members(self, organizationId=None):
    """Get users of an organization.
    
    Parameters
    ----------
    organizationId : str
        Organization ID. Defaults to current if not specified.
    
    Returns
    -------
    list[dict]
        Information about users of an organization.
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    full = []
    done = False
    limit = 100
    cursor = None
    while not done:
        ret = self.ana_api.getMembers(organizationId=organizationId, limit=limit, cursor=cursor)
        if ret == False:
            return False
        if len(ret) == 0:
            done = True
        else:
            full.extend(ret)
            cursor = ret[-1]["userId"]
            if len(ret) < limit:
                done = True
    return full

def get_organization_invites(self, organizationId=None):
    """Get invitations of an organization.
    
    Parameters
    ----------
    organizationId : str
        Organization ID. Defaults to current if not specified.
    
    Returns
    -------
    list[dict]
        Information about invitations of an organization.
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    return self.ana_api.getInvitations(organizationId=organizationId)


def add_organization_member(self, email, role, organizationId=None):
    """Add a user to an existing organization.
    
    Parameters
    ----------
    email: str
        Email of user to add.
    role : str
        Role for user. 
    organizationId : str
        Organization ID to add members too. Uses current if not specified.
    
    Returns
    -------
    str
        Response status if user got added to workspace succesfully. 
    """
    if self.check_logout(): return
    if email is None: raise ValueError("Email must be provided.")
    if role is None: raise ValueError("Role must be provided.")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.addMember(email=email, role=role, organizationId=organizationId, workspaceId=None)


def remove_organization_member(self, email, organizationId=None):
    """Remove a member from an existing organization.
    
    Parameters
    ----------
    email : str
        Member email to remove.
    organizationId: str
        Organization ID to remove member from. Removes from current organization if not specified.
    
    Returns
    -------
    str
        Response status if member got removed from organization succesfully. 
    """
    if self.check_logout(): return
    if email is None: raise ValueError("Email must be provided.")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.removeMember(email=email, organizationId=organizationId, workspaceId=None)

def remove_organization_invitation(self, email, organizationId=None, invitationId=None ):
    """Remove a invitation from an existing organization.
    
    Parameters
    ----------
    email : str
        Invitation email to remove.
    organizationId: str
        Organization ID to remove member from. Removes from current organization if not specified.
    invitationId: str
        Invitation ID to remove invitation from. Removes from current organization if not specified.
    
    Returns
    -------
    str
        Response status if member got removed from organization succesfully. 
    """
    if self.check_logout(): return
    if email is None: raise ValueError("Email must be provided.")
    if invitationId is None: raise ValueError("No invitation found.")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.removeMember(email=email, organizationId=organizationId, workspaceId=None, invitationId=invitationId)


def edit_organization_member(self, email, role, organizationId=None):
    """Edit a member's role. 
    
    Parameters
    ----------
    email : str
        Member email to edit.
    role: str
        Role to assign. 
    organizationId: str
        Organization ID to remove member from. Edits member in current organization if not specified.
    
    Returns
    -------
    str
        Response if member got edited succesfully. 
    """
    if self.check_logout(): return
    if email is None: raise ValueError("Email must be provided.")
    if role is None: raise ValueError("Role must be provided.")
    if organizationId is None: organizationId = self.organization
    return self.ana_api.editMember(email=email, role=role, organizationId=organizationId)
