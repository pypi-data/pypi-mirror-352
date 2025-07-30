"""
Image Functions
"""

def get_image_annotation(self, workspaceId=None, datasetId=None, filename=None):
    """Retrieves the annotation for an image.
    
    Parameters
    ----------
    workspaceId: str
        Workspace ID containing the image. If not specified then the default
        workspace is used.
    datasetId: str
        Dataset ID containing the image
    filename
        Name of the image file the annotation is for
    
    Returns
    -------
    dict
        Information about the image annotation
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    if datasetId is None: raise ValueError("DatasetId must be defined.")
    if filename is None: raise ValueError("Filename must be defined.")
    return self.ana_api.getImageAnnotation(workspaceId, datasetId, filename)


def get_image_mask(self, workspaceId=None, datasetId=None, filename=None):
    """Retrieves the mask for an image.
    
    Parameters
    ----------
    workspaceId: str
        Workspace ID containing the image. If not specified then the default
        workspace is used.
    datasetId: str
        Dataset ID containing the image
    filename
        Name of the image file the mask is for
    
    Returns
    -------
    dict
        Information about the image annotation
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    if datasetId is None: raise ValueError("DatasetId must be defined.")
    if filename is None: raise ValueError("Filename must be defined.")
    return self.ana_api.getImageMask(workspaceId, datasetId, filename)


def get_image_metadata(self, workspaceId=None, datasetId=None, filename=None):
    """Retrieves the metadata for an image.
    
    Parameters
    ----------
    workspaceId: str
        Workspace ID containing the image. If not specified then the default
        workspace is used.
    datasetId: str
        Dataset ID containing the image
    filename
        Name of the image file the metadata is for
    
    Returns
    -------
    dict
        Information about the image annotation
    """
    if self.check_logout(): return
    if workspaceId is None: workspaceId = self.workspace
    if datasetId is None: raise ValueError("DatasetId must be defined.")
    if filename is None: raise ValueError("Filename must be defined.")
    return self.ana_api.getImageMetadata(workspaceId, datasetId, filename)
