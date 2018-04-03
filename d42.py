from ansible.errors import AnsibleError
from ansible.plugins.lookup import LookupBase
import json, requests, imp, sys, csv, StringIO, os

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

    def run(self, terms, variables=None, **kwargs):
        conf = {
            'D42_URL': os.environ['D42_URL'],
            'D42_USER': os.environ['D42_USER'],
            'D42_PWD': os.environ['D42_PWD']
        }
        if terms[1] == "password":
            return self.getUserPass(conf, terms[0], terms[2])
        elif terms[1] == "doql":
            return self.runDoql(conf, terms[0],  terms[2])

    def getUserPass(self, conf, device, username):
        url = conf['D42_URL'] + "/api/1.0/passwords/?plain_text=yes&device=" + device + "&username=" + username
        resp = requests.request("GET",
                                url,
                                auth=(conf['D42_USER'], conf['D42_PWD']),
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

    def runDoql(self, conf, query, header):
        url = conf['D42_URL'] + "/services/data/v1.0/query/"

        post_data = {
            "query": query.replace("@", "'"),
            "header": 'yes' if header else 'no'
        }

        resp = requests.request("POST",
                                url,
                                auth=(conf['D42_USER'], conf['D42_PWD']),
                                data=post_data,
                                verify=False)

        if resp.status_code != 200:
            raise AnsibleError("API Call failed with status code: " + resp.status_code)
        if not resp.text:
            pass

        if not header:
            return [resp.text,]

        return self.get_list_from_csv(resp.text)