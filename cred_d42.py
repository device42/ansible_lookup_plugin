from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
import json, requests, imp, sys, csv, StringIO

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class LookupModule(LookupBase):

    @staticmethod
    def get_list_from_csv(text):
        f = StringIO.StringIO(text.decode("utf-8"))
        list_ = []
        dict_reader = csv.DictReader(f, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True, dialect='excel')
        for item in dict_reader:
            list_.append(item)

        return list_

    @staticmethod
    def prepare_hash(list_array):
        hash_string = '['
        for dictionary in list_array:
            hash_string += '{'
            for key in dictionary:
                hash_string += key + ": '" + dictionary[key] + "', "
            hash_string = hash_string[:-2]
            hash_string += '}, '

        return hash_string[:-2] + ']'
 
    def run(self, terms, variables=None, **kwargs):
        conf = imp.load_source('conf', 'conf')
        print terms
        if terms[1] == "password":
            return self.getUserPass(conf, terms[0], terms[2])
        elif terms[1] == "host":
            return self.getHostIP(conf, terms[0])
        elif terms[1] == "netports":
            return self.getNetports(conf, terms[0])
        
        
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

    def getNetports(self, conf, device):
        url = conf.D42_URL + "/services/data/v1.0/query/"

        post_data = {
            "query": '''SELECT n.port, n.hwaddress, n.port_type, n.port_speed, r.port as remote_port, v.name as primary_vlan_name, d.name as remote_device_name FROM view_netport_v1 n
                        LEFT JOIN view_netport_v1 r ON  n.remote_netport_fk = r.netport_pk
                        lEFT JOIN view_vlan_v1 v ON  n.primary_vlan_fk = v.vlan_pk
                        LEFT JOIN view_device_v1 d ON  r.device_fk = d.device_pk
                        WHERE n.device_fk = (SELECT device_pk FROM view_device_v1 WHERE name = '%s')''' % device,
            "header": "yes"
        }

        resp = requests.request("POST", 
                                url,
                                auth=(conf.D42_USER, conf.D42_PWD),
                                data=post_data,
                                verify=False)

        if resp.status_code != 200:
            raise AnsibleError("API Call failed with status code: " + resp.status_code)
        if not resp.text:
            raise AnsibleError("Something went wrong!")

        net_ports = self.get_list_from_csv(resp.text)
        return self.prepare_hash(net_ports)
