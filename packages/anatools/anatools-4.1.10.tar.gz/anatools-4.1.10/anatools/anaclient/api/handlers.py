"""
Helper functions to parse API calls.
"""
from anatools.lib.print import print_color


def errorhandler(self, response, call):
    responsedata = response.json()
    if self.verbose == 'debug': print(responsedata)
    try: 
        if responsedata['data'][call] is None: raise Exception()
        else: return responsedata['data'][call]
    except:
        if 'errors' in responsedata: raise Exception(responsedata['errors'][-1]['message'])
        else: raise Exception(f'There was an issue with the {call} API call.')