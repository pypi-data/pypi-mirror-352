"""The client module is used for connecting to Rendered.ai's Platform API."""

envs = {
    'prod': {
        'name': 'Rendered.ai Platform',
        'url':  'https://deckard.rendered.ai',
        'statusAPI': 'https://api.rendered.ai/system',
        'api':  'https://api.rendered.ai/graphql' },
    'test': {
        'name': 'Rendered.ai Test Platform',
        'url':  'https://deckard-test.web.app',
        'statusAPI': 'https://api.test.rendered.ai/system',
        'api':  'https://api.test.rendered.ai/graphql' },
    'dev': {
        'name': 'Rendered.ai Development Platform',
        'url':  'https://deckard.dev.rendered.ai/',
        'statusAPI': 'https://api.dev.rendered.ai/system',
        'api':  'https://api.dev.rendered.ai/graphql' }
}

class AuthFailedError(Exception):
    pass

class client:

    def __init__(self, email=None, password=None, APIKey=None, environment=None, endpoint=None, local=False, interactive=True, verbose=None):
        from anatools.anaclient.api import api
        from anatools.lib.print import print_color
        from datetime import datetime
        import getpass
        import yaml
        import os
        import requests
        self.verbose = verbose
        self.interactive = interactive

        # check home directory for api key
        if email is None and APIKey is None and os.environ.get('RENDEREDAI_API_KEY') is None:
            if os.path.exists(os.path.expanduser('~/.renderedai/config.yaml')):
                with open(os.path.expanduser('~/.renderedai/config.yaml'), 'r') as f:
                    config = yaml.safe_load(f)
                    APIKey = config['apikey']
                    environment = config['environment']
                    if self.interactive: print_color("Loaded API Key from ~/.renderedai/config.yaml", '91e600')
        
        # check environment
        if environment: self.environment = environment.lower()
        elif os.environ.get('RENDEREDAI_ENVIRONMENT'): self.environment = os.environ.get('RENDEREDAI_ENVIRONMENT').lower()
        else: self.environment = 'prod'
        if self.environment not in envs.keys():  raise Exception("Invalid environment argument.")
        
        # set client endpoints
        if local:
            os.environ['NO_PROXY'] = '127.0.0.1'
            self.__url = 'http://127.0.0.1:3000/graphql'
            self.__status_url = None
            self.__environment = 'Local'
            if self.interactive: print_color(f"Local is set to: {self.__url}", 'ffff00')
        elif endpoint:
            self.__url = endpoint
            self.__status_url = None
            self.__environment = 'Rendered.ai'
        elif os.environ.get('RENDEREDAI_ENDPOINT'):
            self.__url = os.environ.get('RENDEREDAI_ENDPOINT')
            self.__status_url = None
            self.__environment = 'Rendered.ai'
        else: 
            self.__url = envs[self.environment]['api']
            self.__status_url = envs[self.environment]['statusAPI']
            self.__environment = envs[self.environment]['name']

        self.ana_api = api(self.__url, self.__status_url, None, self.verbose)

        # initialize client variables
        self.user = None
        self.organizations = None
        self.organization = None
        self.workspaces = None
        self.workspace = None
        self.channels = {}
        self.volumes = {}

        # configure client context
        if email or (APIKey is None and os.environ.get('RENDEREDAI_API_KEY') is None):
            if not email:
                self.__email = input(f'Enter your credentials for {self.__environment}.\nEmail: ')
            else: self.__email = email
            if not password: self.__password = getpass.getpass()
            else: self.__password = password
            try: 
                self.user = self.ana_api.login(self.__email, self.__password)
                if self.user is False: raise AuthFailedError()
            except AuthFailedError as e:
                print_color(f'Failed to login to {self.__environment} with email {self.__email}.', 'ff0000')
                raise AuthFailedError()
            except requests.exceptions.ConnectionError as e:
                print_color(f'Could not connect to API to login. Try again or contact support@rendered.ai for assistance.', 'ff0000')
                raise AuthFailedError()
            except requests.exceptions.JSONDecodeError as e:
                print_color(f'Failed to login with email {self.__email} and endpoint {self.__url}. Please confirm this is the correct email and endpoint, contact support@rendered.ai for assistance.', 'ff0000')
                raise AuthFailedError()
            self.__logout = False
            self.ana_api = api(self.__url, self.__status_url, {'uid':self.user['uid'], 'Authorization': f'Bearer {self.user["idtoken"]}'}, self.verbose)
            
            # ask to create an api key if using email/password
            if self.interactive:
                resp = input('Would you like to create an API key to avoid logging in next time? (y/n): ')
                while resp.lower() not in ['y', 'n']:
                    resp = input('Invalid input, please respond with y or n: ')
                if resp.lower() == 'y':
                    print("What kind of scope would you like this API key to have?")
                    print("  [0] User - Full access to all organizations and workspaces you have access to.")
                    print("  [1] Organization - Access to a particular organization and any of it's workspaces.")
                    print("  [2] Workspace - Access to a particular workspace.")
                    resp = input('Please enter the number for the scope: ')
                    while resp.lower() not in ['0', '1', '2']:
                        resp = input('Invalid input, please respond with 0, 1, or 2: ')
                    datestr = datetime.now().isoformat()
                    if resp.lower() == '0':
                        apikey = self.create_api_key(name=f"anatools-{datestr}", scope='user')
                    elif resp.lower() == '1':
                        self.organizations = self.get_organizations()
                        organizations = [org for org in self.organizations if not org['expired']]
                        if len(organizations) == 0: raise Exception("No valid organizations found. Please contact sales@rendered.ai for support.")
                        print("Which organization would you like this API key to be associated with?")
                        for i, org in enumerate(organizations):
                            print(f"  [{i}] {org['name']}")
                        resp = input('Please enter a number for the organization: ')
                        while resp.lower() not in [str(i) for i in range(len(organizations))]:
                            resp = input(f"Invalid input, please respond with a number between 0 and {len(organizations)}: ")
                        self.organization = organizations[int(resp)]['organizationId']
                        apikey = self.create_api_key(name=f"anatools-{datestr}", scope='organization', organizationId=self.organization)
                    else:
                        self.organizations = self.get_organizations()
                        organizations = [org for org in self.organizations if not org['expired']]
                        if len(organizations) == 0: raise Exception("No valid organizations found. Please contact sales@rendered.ai for support.")
                        print("Which organization is the workspace is in?")
                        for i, org in enumerate(organizations):
                            print(f"  [{i}] {org['name']}")
                        resp = input('Please enter a number for the organization: ')
                        while resp.lower() not in [str(i) for i in range(len(organizations))]:
                            resp = input(f"Invalid input, please respond with a number between 0 and {len(organizations)}: ")
                        self.organization = organizations[int(resp)]['organizationId']
                        workspaces = self.get_workspaces(organizationId=self.organization)
                        if len(workspaces) == 0: raise Exception("No valid workspaces found in this organization. Please contact sales@rendered.ai for support.")
                        print("Which workspace would you like this API key to be associated with?")
                        for i, workspace in enumerate(workspaces):
                            print(f"  [{i}] {workspace['name']}")
                        resp = input('Please enter a number for the workspace: ')
                        while resp.lower() not in [str(i) for i in range(len(workspaces))]:
                            resp = input(f"Invalid input, please respond with a number between 0 and {len(workspaces)-1}: ")
                        self.workspace = workspaces[int(resp)]['workspaceId']
                        apikey = self.create_api_key(name=f"anatools-{datestr}", scope='workspace', workspaceId=self.workspace)
                    os.makedirs(os.path.expanduser('~/.renderedai'), exist_ok=True)
                    with open(os.path.expanduser('~/.renderedai/config.yaml'), 'w') as f:
                        yaml.dump({'apikey': apikey, 'environment': self.environment}, f)
                    print_color("API Key saved to ~/.renderedai/config.yaml", '91e600')

            if self.organization is None: 
                self.organizations = self.get_organizations()
                if len(self.organizations) == 0: raise Exception("No organizations found. Please contact sales@rendered.ai for support.")
                organizations = [org for org in self.organizations if not org['expired']]
                if len(organizations) == 0: raise Exception("No valid organizations found. Please contact sales@rendered.ai for support.")
                self.organization = organizations[0]['organizationId']

            # get workspaces
            self.workspaces = self.get_workspaces()
            if self.workspace is None:
                if len(self.workspaces): 
                    self.workspace = self.workspaces[0]['workspaceId']
                    self.organization = self.workspaces[0]['organizationId']
                else: raise Exception("No workspaces available. Please contact support@rendered.ai for support.")

            if self.interactive and self.workspace:
                workspace = [w for w in self.workspaces if w['workspaceId'] == self.workspace][0]['name']
                organization = [o for o in self.organizations if o['organizationId'] == self.organization][0]['name']
                print_color(f'Signed into {self.__environment} with {self.__email}.\nThe current organization is: {organization}\nThe current workspace is: {workspace}', '91e600')
        else:
            if APIKey: self.__APIKey = APIKey
            else:
                if self.interactive: print_color("Using environment variable RENDEREDAI_API_KEY key to login", '91e600')
                self.__APIKey = os.environ.get('RENDEREDAI_API_KEY')
            self.sign_in_apikey()
            if self.interactive:
                if self.organizations: 
                    organization = [o for o in self.organizations if o['organizationId'] == self.organization][0]['name']
                    print_color(f'The current organization is: {organization}', '91e600')
                if self.workspaces:
                    workspace = [w for w in self.workspaces if w['workspaceId'] == self.workspace][0]['name']
                    print_color(f'The current workspace is: {workspace}', '91e600')


    def sign_in_apikey(self):
        from anatools.anaclient.api import api
        from anatools.lib.print import print_color
        from datetime import datetime
        import requests

        self.__logout = False
        try:
            self.ana_api = api(self.__url, self.__status_url, {'apikey': self.__APIKey}, self.verbose)
            apikeydata = self.ana_api.getAPIKeyContext(apiKey=self.__APIKey)
            if not apikeydata:
                print_color("Invalid API Key", 'ff0000')
                raise AuthFailedError()
            if apikeydata.get('expiresAt'):
                apikey_date = datetime.strptime(apikeydata['expiresAt'], "%Y-%m-%dT%H:%M:%S.%fZ")
                current_date = datetime.now()
                if apikey_date < current_date:
                    print_color(f"API Key expired at {apikey_date}", 'ff0000')
                    raise AuthFailedError()
        except requests.exceptions.ConnectionError as e:
            raise Exception("Failed to reach Rendered.ai endpoint for login.")        

        # workspace scope
        if apikeydata.get('workspaceId'):
            self.workspace = apikeydata['workspaceId']
            self.workspaces = self.get_workspaces(workspaceId=apikeydata['workspaceId'])
            self.organization = self.workspaces[0]['organizationId']
            return

        # organization scope
        elif apikeydata.get('organizationId'):
            self.organization = apikeydata['organizationId']
            self.organizations = self.get_organizations(organizationId=self.organization)
            self.workspaces = self.get_workspaces(organizationId=self.organization)
            if len(self.workspaces): self.workspace = self.workspaces[0]['workspaceId']
            else: 
                response = input("No workspaces available. Would you like to create a new one? (y/n)")
                if response.lower() == 'y': 
                    self.create_workspace(name="Workspace")
                    self.workspaces = self.get_workspaces()
                    self.workspace = self.workspaces[0]['workspaceId']
                else: raise Exception("No workspaces available. Please contact support@rendered.ai for support.")

        # user scope
        else:
            self.organizations = self.get_organizations()
            if len(self.organizations): self.organization = self.organizations[0]['organizationId']
            else: raise Exception("No organizations found. Please contact sales@rendered.ai for support.")
            self.workspaces = self.get_workspaces()
            if len(self.workspaces): self.workspace = self.workspaces[0]['workspaceId']
            else: 
                response = input("No workspaces available. Would you like to create a new one? (y/n)")
                if response.lower() == 'y': 
                    self.create_workspace(name="Workspace")
                    self.workspaces = self.get_workspaces()
                    self.workspace = self.workspaces[0]['workspaceId']
                else: raise Exception("No workspaces available. Please contact support@rendered.ai for support.")
            self.organization = self.workspaces[0]['organizationId']

        validorgs = False
        for org in self.organizations:
            if not org['expired']: validorgs = True
        if not validorgs: raise Exception("No valid organizations found. Please contact sales@rendered.ai for support.")


    def refresh_token(self):
        import time
        import requests
        from anatools.anaclient.api import api
        from anatools.lib.print import print_color
        if self.user:
            if int(time.time()) > int(self.user['expiresAt']):
                self.user = self.ana_api.login(self.__email, self.__password)
                self.ana_api = api(self.__url, self.__status_url, {'uid': self.user['uid'], 'Authorization': f'Bearer {self.user["idtoken"]}'}, self.verbose)
                try:
                    notification = self.ana_api.getSystemNotifications()
                    self.__notificationId = notification['notificationId']
                    if notification and notification['notificationId'] != self.__notificationId:
                        self.__notificationId = notification['notificationId']
                        print_color(notification['message'], 'ffff00')
                except requests.exceptions.ConnectionError as e:
                        print_color(f"Could not get notifications: {e}", 'ffff00')
        
                
    def check_logout(self):
        if self.__logout: print('You are currently logged out, login to access the Rendered.ai Platform.'); return True
        self.refresh_token()
        return False


    def logout(self):
        """Logs out of the ana sdk and removes credentials from ana."""
        if self.check_logout(): return
        self.__logout = True
        del self.__password, self.__url, self.user


    def login(self, email=None, password=None, environment=None, endpoint=None, local=False, interactive=True, verbose=None):
        """Log in to the SDK. 
        
        Parameters
        ----------
        email: str
            Email for the login. Will prompt if not provided.
        password: str
            Password to login. Will prompt if not provided.
        environment: str
            Environment to log into. Defaults to production.
        endpoint: str
            Custom endpoint to log into.
        local: bool
            Used for development to indicate pointing to local API.
        interactive: bool
            Set to False for muting the login messages.
        verbose: str
            Flag to turn on verbose logging. Use 'debug' to view log output.
        
        """
        self.__init__( email, password, environment, endpoint, local, interactive, verbose)


    def get_system_status(self, serviceId=None, display=True):
        """Fetches the system status, if no serviceId is provided it will fetch all services. 
        
        Parameters
        ----------
        serviceId: str
            The identifier of the service to fetch the status of.
        display: bool
            Boolean for either displaying the status or returning as a dict.
        """
        from anatools.lib.print import print_color
        services = self.ana_api.getSystemStatus(serviceId)
        if services and display:
            spacing = max([len(service['serviceName']) for service in services])+4
            print('Service Name'.ljust(spacing, ' ')+'Status')
            for service in services:
                print(service['serviceName'].ljust(spacing, ' '), end='')
                if service['status'] == 'Operational': print_color('Operational', '91e600')
                elif service['status'] == 'Degraded': print_color('Degraded', 'ffff00')
                elif service['status'] == 'Down': print_color('Down', 'ff0000')
                else: print('?')
            return
        return services



    
    from .organizations import get_organization, set_organization, get_organizations, edit_organization, get_organization_members, get_organization_invites, add_organization_member, edit_organization_member, remove_organization_member, remove_organization_invitation
    from .workspaces    import get_workspace, set_workspace, get_workspaces, create_workspace, edit_workspace, delete_workspace, remove_workspace_invitation
    from .graphs        import get_graphs, create_graph, edit_graph, delete_graph, download_graph, get_default_graph, set_default_graph
    from .staged_graphs import get_staged_graphs, create_staged_graph, edit_staged_graph, delete_staged_graph, download_staged_graph
    from .datasets      import get_datasets, get_dataset_jobs, create_dataset, edit_dataset, delete_dataset, download_dataset, cancel_dataset, upload_dataset, get_dataset_runs, get_dataset_log, get_dataset_files, create_mixed_dataset
    from .channels      import get_channels, get_channel_nodes, get_managed_channels, create_managed_channel, edit_managed_channel, delete_managed_channel, build_managed_channel, deploy_managed_channel, get_deployment_status, get_channel_documentation, upload_channel_documentation, get_node_documentation, profile_channel
    from .volumes       import get_volumes, get_managed_volumes, create_managed_volume, edit_managed_volume, delete_managed_volume, get_volume_data, download_volume_data, upload_volume_data, delete_volume_data, mount_volumes
    from .analytics     import get_analytics, download_analytics, get_analytics_types, create_analytics, delete_analytics
    from .annotations   import get_annotations, get_annotation_formats, get_annotation_maps, create_annotation, download_annotation, delete_annotation , get_managed_maps, create_managed_map, edit_managed_map, delete_managed_map, download_managed_map
    from .gan           import get_gan_models, get_gan_datasets, create_gan_dataset, delete_gan_dataset, create_managed_gan, delete_gan_model, get_managed_gans, edit_managed_gan, delete_managed_gan, download_managed_gan
    from .umap          import get_umaps, create_umap, delete_umap
    from .api_keys      import get_api_keys, create_api_key, delete_api_key, get_api_key_data
    from .llm           import get_llm_response, create_llm_prompt, delete_llm_prompt, get_llm_base_channels, get_llm_channel_node_types
    from .editor        import create_remote_development, delete_remote_development, list_remote_development, stop_remote_development, start_remote_development, prepare_ssh_remote_development, remove_ssh_remote_development, invite_remote_development, get_ssh_keys, register_ssh_key, deregister_ssh_key
    from .ml            import get_ml_architectures, get_ml_models, create_ml_model, delete_ml_model, edit_ml_model, download_ml_model, upload_ml_model, get_ml_inferences, get_ml_inference_metrics, create_ml_inference, delete_ml_inference, download_ml_inference
    from .inpaint       import get_inpaints, get_inpaint_logs, create_inpaint, delete_inpaint
    from .preview       import get_preview, create_preview 
    from .image         import get_image_annotation, get_image_mask, get_image_metadata