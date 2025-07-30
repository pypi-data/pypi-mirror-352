"""
Machine Learning Functions
"""
import json
import os
from anatools.anaclient.helpers import multipart_upload_file
from anatools.lib.download import download_file

def get_ml_architectures(self):
    """Retrieves the machine learning model architectures available on the platform.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        Machine learning model architectures
    """
    if self.check_logout(): return
    return self.ana_api.getMLArchitectures()


def get_ml_models(self, workspaceId=None, datasetId=None, modelId=None, filters=None):
    """Retrieves the machine learning model architectures available on the platform.
    
    Parameters
    ----------
    workspaceId : str
        Workspace ID
    datasetId : str
        Dataset ID
    modelId : str
        Model ID
    filters: dict
        Filters that limit output to entries that match the filter 
    Returns
    -------
    dict
        Machine learning model architectures
    """
    if workspaceId is None: workspaceId = self.workspace
    if self.check_logout(): return
    full = []
    done = False
    limit = 100
    cursor = None
    while not done:
        ret = self.ana_api.getMLModels(workspaceId, datasetId, modelId, limit=limit, cursor=cursor, filters=filters)
        if ret == False:
            return False
        if len(ret) == 0:
            done = True
        else:
            full.extend(ret)
            cursor = ret[-1]["modelId"]
            if len(ret) < limit:
                done = True
    return full


def create_ml_model(self, datasetId, architectureId, name, description, parameters, workspaceId=None):
    """Creates a new machine learning model.
    
    Parameters
    ----------
    architectureId : str
        Architecture ID
    datasetId : str
        Dataset ID
    name : str
        Model name
    description : str
        Model description
    paramters : str
        JSON string of model parameters
    workspaceId : str
        Workspace ID
    Returns
    -------
    str
        Machine learning model ID
    """
    if workspaceId is None: workspaceId = self.workspace
    if self.check_logout(): return
    return self.ana_api.createMLModel(workspaceId, datasetId, architectureId, name, description, parameters)


def delete_ml_model(self, modelId, workspaceId=None):
    """Deletes or cancels a machine learning model.
    
    Parameters
    ----------
    modelId : str
        Model ID
    workspaceId : str
        Workspace ID
    Returns
    -------
    bool
        Success / failure
    """
    if workspaceId is None: workspaceId = self.workspace
    if self.check_logout(): return
    return self.ana_api.createMLModel(workspaceId, modelId)


def edit_ml_model(self, modelId, name, description, workspaceId=None):
    """Edit the name or description of a machine learning model.
    
    Parameters
    ----------
    modelId : str
        Model ID
    name : str
        Model name
    description : str
        Model description
    workspaceId : str
        Workspace ID
    Returns
    -------
    bool
        Success / failure
    """
    if workspaceId is None: workspaceId = self.workspace
    if self.check_logout(): return
    return self.ana_api.createMLModel(workspaceId, modelId, name, description)


def download_ml_model(self, modelId, checkpoint=None, localDir=None, workspaceId=None):
    """Download the machine learning model.
    
    Parameters
    ----------
    modelId : str
        Model ID
    checkpoint : str
        Checkpoint to download. If not specified, the final model will be downloaded
    localDir : str
        Local directory to save the model
    workspaceId : str
        Workspace ID
    Returns
    -------
    bool
        Success / failure
    """
    if workspaceId is None: workspaceId = self.workspace
    if modelId is None: raise Exception('modelId must be specified.')
    if localDir is None: localDir = os.getcwd()
    if self.check_logout(): return
    url = self.ana_api.downloadMLModel(workspaceId=workspaceId, modelId=modelId, checkpoint=checkpoint)
    fname = url.split('?')[0].split('/')[-1]
    return download_file(url=url, fname=fname, localDir=localDir) 


def upload_ml_model(self, name, description, modelfile, parameters, workspaceId=None):
    """Upload a machine learning model.
    
    Parameters
    ----------
    name : str
        Model name
    description : str
        Model description
    modelfile : str
        The filepath of the compressed file containing the model, classes and spec.
    parameters : str
        Model training parameters
    workspaceId : str
        Workspace ID
    Returns
    -------
    bool
        Success / failure
    """
    if workspaceId is None: workspaceId = self.workspace
    if description is None: description = ''
    if name is None: raise ValueError("Name must be defined.")
    if modelfile is None: raise ValueError("Filename must be defined.")
    if self.check_logout(): return

    filesize = os.path.getsize(modelfile)
    fileinfo = self.ana_api.uploadMLModel(workspaceId=workspaceId, name=name, size=filesize, description=description, parameters=parameters)
    modelId = fileinfo['modelId']
    parts = multipart_upload_file(modelfile, fileinfo["partSize"], fileinfo["urls"], f"Uploading ml model {modelfile}")
    self.refresh_token()
    finalize_success = self.ana_api.uploadMLModelFinalizer(workspaceId, fileinfo['uploadId'], fileinfo['key'], parts)
    if not finalize_success: raise Exception(f"Failed to upload dataset {modelfile}.")
    else: print(f"\x1b[1K\rUpload completed successfully!", flush=True)
    return modelId


def get_ml_inferences(self, inferenceId=None, datasetId=None, modelId=None, workspaceId=None, filters=None):
    """Get the inferences of a machine learning model.
    
    Parameters
    ----------
    inferenceId : str
        Inference ID
    datasetId : str
        Dataset ID
    modelId : str
        Model ID
    workspaceId : str
        Workspace ID
    filters: dict
        Filters that limit output to entries that match the filter 
    Returns
    -------
    dict
        Inference data
    """
    if workspaceId is None: workspaceId = self.workspace
    if self.check_logout(): return
    full = []
    done = False
    limit = 100
    cursor = None
    while not done:
        ret = self.ana_api.getMLInferences(workspaceId, inferenceId, datasetId, modelId, limit=limit, cursor=cursor, filters=filters)
        if ret == False:
            return False
        if len(ret) == 0:
            done = True
        else:
            full.extend(ret)
            cursor = ret[-1]["inferenceId"]
            if len(ret) < limit:
                done = True
    return full


def get_ml_inference_metrics(self, inferenceId, workspaceId=None):
    """Get the metrics from an inference job.
    
    Parameters
    ----------
    inferenceId : str
        Inference ID
    workspaceId : str
        Workspace ID
    Returns
    -------
    dict
        Metric data
    """
    if workspaceId is None: workspaceId = self.workspace
    if self.check_logout(): return
    metrics = self.ana_api.getMLInferenceMetrics(workspaceId, inferenceId)
    return json.loads(metrics)


def create_ml_inference(self, datasetId, modelId, mapId, workspaceId=None):
    """Create a new machine learning inference job.
    
    Parameters
    ----------
    datasetId : str
        Dataset ID
    modelId : str
        Model ID
    mapId : str
        Map ID
    workspaceId : str
        Workspace ID
    Returns
    -------
    str
        Inference ID
    """
    if workspaceId is None: workspaceId = self.workspace
    if self.check_logout(): return
    return self.ana_api.createMLInference(workspaceId, datasetId, modelId, mapId)


def delete_ml_inference(self, inferenceId, workspaceId=None):
    """Deletes or cancels a machine learning inference job.
    
    Parameters
    ----------
    inferenceId : str
        Inference ID
    workspaceId : str
        Workspace ID
    Returns
    -------
    bool
        Success / failure
    """
    if workspaceId is None: workspaceId = self.workspace
    if self.check_logout(): return
    return self.ana_api.deleteMLInference(workspaceId, inferenceId)


def download_ml_inference(self, inferenceId, localDir=None, workspaceId=None):
    """Download the inference detections.
    
    Parameters
    ----------
    inferencId : str
        Inference ID
    localDir : str
        Local directory to save the model
    workspaceId : str
        Workspace ID
    Returns
    -------
    bool
        Success / failure
    """
    if workspaceId is None: workspaceId = self.workspace
    if inferenceId is None: raise Exception('inferenceId must be specified.')
    if localDir is None: localDir = os.getcwd()
    if self.check_logout(): return
    url = self.ana_api.downloadMLInference(workspaceId=workspaceId, inferenceId=inferenceId)
    fname = url.split('?')[0].split('/')[-1]
    return download_file(url=url, fname=fname, localDir=localDir) 