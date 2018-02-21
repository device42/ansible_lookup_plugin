from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
import json, requests, imp

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):
        conf = imp.load_source('conf', 'conf')
        if terms[1] == "password":
            return self.getUserPass(conf, terms[0], terms[2])
        elif terms[1] == "host":
            return self.getHostIP(conf, terms[0])
        
        
    def getUserPass(self, conf, device, username):
        url = conf.D42_URL + "/api/1.0/passwords/?plain_text=yes&device=" + device + "&username=" + username
        resp = requests.request("GET", 
                                url,
                                auth=(conf.D42_USER, conf.D42_PWD), 
                                verify=False)
        
        if resp.status_code != 200:
            raise AnsibleError("API Call failed with status code: " + resp.status_code)
        if not resp.text:
            raise AnsibleError("Something went wrong!")        
        
        req = json.loads(resp.text)
        req = req["Passwords"]
        if req:
            if len(req) > 1:
                raise AnsibleError("Multiple users found for device: %s" % device)
            return [req[0]["password"]]
        else:
            raise AnsibleError("No password found for user: %s and device: %s" % (username, device))
            
    def getHostIP(self, conf, device):
        url = conf.D42_URL + "/api/1.0/devices/name/" + device
        resp = requests.request("GET", 
                                url,
                                auth=(conf.D42_USER, conf.D42_PWD), 
                                verify=False)
        
        if resp.status_code != 200:
            raise AnsibleError("API Call failed with status code: " + resp.status_code)
        if not resp.text:
            raise AnsibleError("Something went wrong!")

        req = json.loads(resp.text)
        if req["ip_addresses"]:
            req = req["ip_addresses"][0]
            return [req["ip"]]
        else:
            raise AnsibleError("No IP address found for device: %s" % device)