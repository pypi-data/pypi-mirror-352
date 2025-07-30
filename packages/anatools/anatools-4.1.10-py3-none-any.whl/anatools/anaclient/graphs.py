"""
Graphs Functions
"""

def get_graphs(self, graphId=None, name=None, email=None, workspaceId=None, filters=None):
    """Queries the workspace graphs based off provided parameters. Checks on graphId, name, or owner in this respective order within the specified workspace.
    If only workspace ID is provided, this will return all the graphs in a workspace. 
    
    Parameters
    ----------
    graphid : str
        GraphID to filter on. Optional.
    name : str
        Name of the graph to filter on. Optional.
    email: str
        Owner of graphs to filter on. Optional.
    workspaceId : str    
        Workspace ID to filter on. If none is provided, the default workspace will get used.
    filters: dict
        Filters that limit output to entries that match the filter 
    
    Returns
    -------
    list[dict]
        A list of graphs based off provided query parameters if any parameters match.
    """
    if self.check_logout(): return
    if graphId is None: graphId = ''
    if name is None: name = ''
    if email is None: email = ''
    if workspaceId is None: workspaceId = self.workspace
    full = []
    done = False
    limit = 100
    cursor = None
    while not done:
        ret = self.ana_api.getGraphs(workspaceId=workspaceId, graphId=graphId, name=name, email=email, staged=False, limit=limit, cursor=cursor, filters=filters)
        if ret == False:
            return False
        if len(ret) == 0:
            done = True
        else:
            full.extend(ret)
            cursor = ret[-1]["graphId"]
            if len(ret) < limit:
                done = True
    return full


def create_graph(self, name, channelId, graph, description=None, workspaceId=None):
    """Generates a new graph based off provided parameters. Must provide valid json string to create a new graph.
    
    Parameters
    ----------
    name : str
        Name for the  that will get generated.
    channelId: str
        Id of channel to generate the graph with.
    graph: str
        The graph as a dictionary or `JSON` string. While `YAML` files are used in channel development, the Platform SDK and API only support `JSON`. 
        Ensure that the `YAML` file is valid in order for the `yaml.safe_load` to convert `YAML` to a dictionary for you. Otherwise,  provide a graph in `JSON` format.
    description: str
        Description of graph. Optional.
    workspaceId : str    
        Workspace ID create the graph in. If none is provided, the default workspace will get used. 
    
    Returns
    -------
    str
        The graph id if it was created sucessfully or an error message.
    """
    if self.check_logout(): return
    if name is None: raise ValueError('Name input must be defined.')
    if graph is None: raise ValueError('Graph input must be defined.')
    if channelId is None: raise ValueError('ChannelId input must be defined.')
    if workspaceId is None: workspaceId = self.workspace
    if type(graph) is dict:
        import json
        graph = json.dumps(graph)
    return self.ana_api.createGraph(workspaceId=workspaceId, channelId=channelId, graph=graph, name=name, description=description, staged=False)


def edit_graph(self, graphId, description=None, name=None, workspaceId=None):
    """Update graph description and name. 
    
    Parameters
    ----------
    graphId : str
        Graph id to update.
    description: str
        New description to update.
    name: str
        New name to update.
    workspaceId : str    
        Workspace ID of the graph's workspace. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        A success or error message based on graph's update.
    """
    if self.check_logout(): return
    if graphId is None: return
    if name is None and description is None: return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.editGraph(workspaceId=workspaceId, graphId=graphId, name=name, description=description, staged=False)


def delete_graph(self, graphId, workspaceId=None):
    """Delete a graph in a workspace.
    
    Parameters
    ----------
    graphId : str
        Graph id to delete.
    workspaceId : str    
        Workspace ID of the graph's workspace. If none is provided, the current workspace will get used. 
    
    Returns
    -------
    str
        A success or error message based on graph's delete.
    """
    if self.check_logout(): return
    if graphId is None: return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.deleteGraph(workspaceId=workspaceId, graphId=graphId)
    

def download_graph(self, graphId, workspaceId=None):
    """Download a graph.
    
    Parameters
    ----------
    graphId : str
        Graph ID of the graph to download.
    workspaceId : str    
        Workspace ID of the graph's workspace. If none is provided, the default workspace will get used. 
    
    Returns
    -------
    str
        A download URL that can be used in the browser or a failure message.
    """
    if self.check_logout(): return
    if graphId is None: return
    if workspaceId is None: workspaceId = self.workspace
    return self.ana_api.downloadGraph(workspaceId=workspaceId, graphId=graphId)


def get_default_graph(self, channelId):
    """Gets the default graph for a channel.
    
    Parameters
    ----------
    channelId:
        Id of channel to get the default graph for.
   
    Returns
    -------
    json
        json data representing the graph.
    """
    if self.check_logout(): return
    return self.ana_api.getDefaultGraph(channelId=channelId)


def set_default_graph(self, channelId, workspaceId, graphId=None, stagedGraphId=None):
    """Sets the default graph for a channel. User must be in the organization that manages the channel.
    
    Parameters
    ----------
    channel : str
        The name of the channel to update the default graph.
    workspaceId : str
        The ID of the Workspace that the graph is in.
    graphId: str
        The ID of the graph that you want to be the default for the channel. Optional.
    stagedGraphId: str
        The ID of the staged graph that you want to be the default for the channel. Optional.

    Returns
    -------
    str
        Status
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    if graphId is None and stagedGraphId is None: raise Exception('GraphID or StagedGraphId must be specified.')
    return self.ana_api.setChannelGraph(channelId=channelId, workspaceId=workspaceId, graphId=graphId ,stagedGraphId=stagedGraphId)
    