"""
Volumes Functions
"""
import os
import traceback
from anatools.anaclient.helpers import generate_etag, multipart_upload_file

def get_volumes(self, volumeId=None, workspaceId=None, organizationId=None, filters=None):
    """Retrieves all volumes the user has access to.
    
    Parameters
    ----------
    volumeId : str
        The ID of a specific Volume.
    organizationId : str
        The ID of the organization that the volume belongs to.
    filters: dict
        Filters that limit output to entries that match the filter 
    
    Returns
    -------
    list[dict]
        Volume Info
    """
    if self.check_logout(): return
    full = []
    done = False
    limit = 100
    cursor = None
    while not done:
        ret = self.ana_api.getVolumes(organizationId=organizationId, workspaceId=workspaceId, volumeId=volumeId, limit=limit, cursor=cursor, filters=filters)
        if ret == False:
            return False
        if len(ret) == 0:
            done = True
        else:
            full.extend(ret)
            cursor = ret[-1]["volumeId"]
            if len(ret) < limit:
                done = True
    if full:
        for volume in full:
            self.volumes[volume['volumeId']] = volume['name']
    return full    


def get_managed_volumes(self, volumeId=None, organizationId=None):
    """Retrieves the managed volumes for an organization.
    
    Parameters
    ----------
    volumeId : str
        The ID of a specific Volume.
    organizationId : str
        The ID of the organization that the managed volume belongs to.
    
    Returns
    -------
    list[dict]
        Volume Info
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    full = []
    done = False
    limit = 100
    cursor = None
    while not done:
        ret = self.ana_api.getManagedVolumes(organizationId=organizationId, volumeId=volumeId, limit=limit, cursor=cursor)
        if ret == False:
            return False
        if len(ret) == 0:
            done = True
        else:
            full.extend(ret)
            cursor = ret[-1]["volumeId"]
            if len(ret) < limit:
                done = True
    return full


def create_managed_volume(self, name, description=None, organizationId=None):
    """Creates a new volume with the specified name in the organization. By default the permission on the volume is set to `write`.
    
    Parameters
    ----------
    name : str
        The name of the new volume. Note: this name needs to be unique per organization.
    description : str
        Description of the volume
    organizationId : str
        The ID of the organization that the managed volume will belong to.
    
    Returns
    -------
    str
        volumeId
    """
    if self.check_logout(): return
    if organizationId is None: organizationId = self.organization
    if name is None: raise Exception("Name must be specified.")
    return self.ana_api.createManagedVolume(organizationId=organizationId, name=name, description=description)

    
def delete_managed_volume(self, volumeId):
    """Removes the volume from the organization. Note that this will delete any remote data in the volume 
    and channels that rely on this volume will need to be updated.
    
    Parameters
    ----------
    volumeId : str
        The ID of a specific Volume to delete.
    
    Returns
    -------
    str
        Status
    """
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    return self.ana_api.deleteManagedVolume(volumeId=volumeId)


def edit_managed_volume(self, volumeId, name=None, description=None, permission=None):
    """Edits the volume in your current organization.
    
    Parameters
    ----------
    volumeId: str
        The volumeId that will be updated.
    name : str
        The new name of the new volume. Note: this name needs to be unique per organization.
    description : str
        Description of the volume
    permission : str
        Permission to set for the volume. Choose from: read, write, or view.
    
    Returns
    -------
    str
        Status True or False
    """
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    if name is None and description is None: raise Exception("Either name or description must be specified.")
    return self.ana_api.editManagedVolume(volumeId=volumeId, name=name, description=description, permission=permission)


def get_volume_data(self, volumeId, files=[], dir="", recursive=False):
    """Retrieves information about data from a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to get data for.
    files : str
        The specific files or directories to retrieve information about from the volume, if you wish to retrieve all then leave the list empty.
    dir : str
        Specific volume directory to retrieve information about. Optional. 
    recursive : bool
        Whether to recursively retrieve information about the volume. Optional.
    Returns
    -------
    str
       Status
    """
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    full = []
    done = False
    limit = 100
    cursor = 0
    while not done:
        ret = self.ana_api.getVolumeData(volumeId=volumeId, keys=files, dir=dir, recursive=recursive, limit=limit, cursor=str(cursor))
        if ret == False:
            return False
        if len(ret) == 0:
            done = True
        else:
            for fileinfo in ret['keys']:
                full.append({
                    'key': fileinfo['key'],
                    'size': fileinfo['size'],
                    'lastUpdated': fileinfo['updatedAt'],
                    'hash': fileinfo['hash']
                })
            cursor += limit
            if len(ret['keys']) < limit:
                done = True
    return full


def download_volume_data(self, volumeId, files=[], localDir=None, recursive=True, sync=False):
    """Download data from a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to download data of.
    files : str
        The specific files or directories to retrieve from the volume, if you wish to retrieve all then leave the list empty.
    localDir : str
        The location of the local directory to download the files to. If not specified, this will download the files to the current directory.
    recursive: bool
        Recursively download files from the volume.
    sync: bool
        Syncs data between the local directory and the remote location. Only creates folders in the destination if they contain one or more files.
    Returns
    -------
    str
       Status
    """
    import hashlib, requests, traceback, os
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    if localDir is None: localDir = os.getcwd()
    if not os.path.exists(localDir): os.makedirs(localDir, exist_ok=True)

    response = []
    for file in files or [""]:
        condition = True
        offset = 0
        limit = 100

        key_param = [] if file.endswith("/") or file == "" else [file]
        dir_param = file if file.endswith("/") else ""

        while condition:
            result = self.ana_api.getVolumeData(
                volumeId=volumeId, 
                keys=key_param,
                dir=dir_param,
                limit=limit, 
                recursive=recursive, 
                cursor=str(offset)
            )
            for fileinfo in result['keys']:
                if fileinfo['size']:
                    response.append({
                        'key': os.path.join(dir_param, fileinfo['key']),
                        'size': fileinfo['size'],
                        'lastUpdated': fileinfo['updatedAt'],
                        'hash': fileinfo['hash'],
                        'url': fileinfo['url'],
                    })
            if len(result['keys']) < limit: condition = False
            else: offset += limit

    source_hashes = list(map(lambda x: x['key'] + x['hash'], response))
    destination_files = []
    destination_hashes = []

    if sync == True:    
        for root, dirs, files in os.walk(localDir):
            for file in files:
                filepath = os.path.join(root, file).replace(localDir, '')
                destination_files.append(filepath)
                file_hash = hashlib.md5()
                with open(os.path.join(root, file),'rb') as f: 
                    while True:
                        chunk = f.read(128 * file_hash.block_size)
                        if not chunk:
                            break
                        file_hash.update(chunk)
                destination_hashes.append(filepath + file_hash.hexdigest())

    for index, hash in enumerate(source_hashes):
        if (sync == True and (hash in destination_hashes)):
            if self.interactive: 
                print(f"\x1b[1K\rsync: {response[index]['key']}'s hash exists in {localDir}", flush=True)
        elif sync == False or (hash not in destination_hashes):
            try:
                downloadresponse = requests.get(url=response[index]['url'])
                filename = os.path.join(localDir, response[index]['key'])
                if not os.path.exists(os.path.dirname(filename)):
                    os.makedirs(os.path.dirname(filename))
                with open(filename, 'wb') as outfile:
                    outfile.write(downloadresponse.content)
                if self.interactive: 
                    print(f"\x1b[1K\rdownload: {response[index]['key']} to {filename}", flush=True)
            except:
                traceback.print_exc()
                print(f"\x1b[1K\rdownload: failed to download {response[index]['key']}", flush=True)

    return


def upload_volume_data(self, volumeId, files=[], localDir=None, destinationDir=None, sync=False):
    """Upload data to a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to upload data to.
    files : list[str]
        The specific files or directories to push to the volume from the localDir. If you wish to push all data in the root directory, then leave the list empty.
    localDir : str
        The location of the local directory to upload the files from. If not specified, this will try to upload the files from the current directory.
    destinationDir : str
        The target directory in the volume where files will be uploaded. If not specified, files will be uploaded to the root of the volume.
    sync: bool
        Recursively uploads new and updated files from the source to the destination. Only creates folders in the destination if they contain one or more files.
    Returns
    -------
    str
       Status
    """
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    if localDir is None: localDir = os.getcwd()
    if not localDir.endswith('/'): localDir+='/'
    if not os.path.exists(localDir): raise Exception(f"Could not find directory {localDir}.")
    if destinationDir is not None:
        destinationDir = destinationDir.strip('/')
        if destinationDir: destinationDir += '/'

    source_files = []
    source_hashes = []
    faileduploads = []
        
    if len(files):
        for file in files:
            filepath = os.path.join(localDir, file)
            if os.path.isdir(filepath):
                for root, dirs, files in os.walk(filepath):
                    for file in files:
                        filepath = os.path.join(root, file).replace(localDir, '')
                        source_files.append(filepath)
                        if sync == True:
                            file_hash = generate_etag(os.path.join(root,file))
                            source_hashes.append(filepath + file_hash)
            elif os.path.isfile(filepath):
                source_files.append(file)
                if sync == True:
                    file_hash = generate_etag(filepath)
                    source_hashes.append(file + file_hash)
            else: print(f"Could not find {filepath}.")
    else:
        for root, dirs, files in os.walk(localDir):
            for file in files:
                filepath = os.path.join(root, file).replace(localDir, '')
                source_files.append(filepath)
                if sync == True:
                    file_hash = generate_etag(os.path.join(root,file))
                    source_hashes.append(filepath + file_hash)

    if sync == True:
        response = []
        condition = True
        offset = 0

        while condition:
            result = self.ana_api.getVolumeData(volumeId=volumeId, keys=[], dir=destinationDir or "", limit=100, offset=offset)
            for fileinfo in result['keys']:
                response.append({
                    'key':          fileinfo['key'],
                    'size':         fileinfo['size'],
                    'lastUpdated':  fileinfo['updatedAt'],
                    'hash':         fileinfo['hash'],
                    'url':          fileinfo['url'],
                })
            
            if (result['pageInfo']['totalItems'] > offset + 100):
                offset += 100
            else:
                condition = False

        destination_hashes = list(map((lambda x: x['key'] + x['hash']), [file for file in response if file['size'] != 0]))
        delete_files = []
        for index, object in enumerate(response):
            if object['key'] not in source_files:
                destination_file = (destinationDir or '') + object['key']
                delete_files.append(destination_file)  

        if (len(delete_files)):
            print(f"The following files will be deleted:", end='\n', flush=True)
            for file in delete_files:
                print(f"   {file}", end='\n', flush=True)
            answer = input("Delete these files [Y/n]: ")
            if answer.lower() == "y":
                self.refresh_token()
                self.ana_api.deleteVolumeData(volumeId=volumeId, keys=delete_files)

    for index, file in enumerate(source_files):
        destination_key = (destinationDir or '') + file
        print(f"\x1b[1K\rUploading {file} to the volume [{index+1} / {len(source_files)}]", end='\n' if self.verbose else '', flush=True)
        if (sync == True and (source_hashes[index] in destination_hashes)):
            print(f"\x1b[1K\rsync: {file}'s hash exists", end='\n' if self.verbose else '', flush=True)
        elif sync == False or (source_hashes[index] not in destination_hashes):
            try:
                self.refresh_token()
                filepath = os.path.join(localDir, file)
                filesize = os.path.getsize(filepath)
                fileinfo = self.ana_api.putVolumeData(volumeId=volumeId, key=destination_key, size=filesize)
                # print(f"\x1b[1K\rupload: {file} to the volume. [{index+1} / {len(source_files)}]", end='\n' if self.verbose else '', flush=True)
                parts = multipart_upload_file(filepath, int(fileinfo["partSize"]), fileinfo["urls"], f"Uploading {file} to the volume [{index+1} / {len(source_files)}]")
                self.refresh_token()
                finalize_success = self.ana_api.putVolumeDataFinalizer(volumeId, fileinfo['uploadId'], fileinfo['key'], parts)
                if not finalize_success:
                    faileduploads.append(file)
            except:
                traceback.print_exc()
                faileduploads.append(file)
                print(f"\x1b[1K\rupload: {file} failed", end='\n' if self.verbose else '', flush=True)
    print("\x1b[1K\rUploading files completed.", flush=True)
    if len(faileduploads): print('The following files failed to upload:', faileduploads, flush=True)
    return
            

def delete_volume_data(self, volumeId, files=[]):
    """Delete data from a volume.
    
    Parameters
    ----------
    volumeId : str
       VolumeId to delete files from.
    files : str
        The specific files to delete from the volume. If left empty, no files are deleted.
    
    Returns
    -------
    str
       Status
    """
    if self.check_logout(): return
    if volumeId is None: raise Exception('VolumeId must be specified.')
    return self.ana_api.deleteVolumeData(volumeId=volumeId, keys=files)


def mount_volumes(self, volumes):
    """Retrieves credentials for mounting volumes.
    
    Parameters
    ----------
    volumes : [str]
       Volumes to retrieve mount credentials for.

    Returns
    -------
    dict
        Credential information.
    """
    if self.check_logout(): return
    if not len(volumes): raise Exception('A list of volumeIds must be specified.')
    return self.ana_api.mountVolumes(volumes=volumes)
