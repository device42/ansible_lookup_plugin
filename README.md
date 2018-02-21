# Ansible-Device42: Lookup Plugin

## Introduction 

This lookup plugin allows a playbook to fetch passwords or ip addresses for hosts from Device42. This can be especially interesting if users are trying to ssh into hosts to do some sort of task.

## Ansible Host Requirements
* Requests (http://docs.python-requests.org/en/master/)

## Configuration
```
* Rename conf.sample to conf
* In conf add D42 URL/credentials
```
```
# ====== Device42 account settings ========= #
D42_USER = 'device42 user'
D42_PWD = 'device42 password'
D42_URL = 'https:// device42 server IP address'
```
```
* Place conf file in same directory as playbook file
* Place cred_d42.py in ansible/lib/ansible/plugins/lookup/
```

## Usage

The lookup plugin can be called from your playbook by the following command: 
`lookup('plugin_name', 'device_name', 'type', 'optional_var')`

```
To get password call: lookup('cred_d42', 'device_name', 'password', 'username')
```
device_name and username need to be filled in
```
To get ip address call: lookup('cred_d42', 'device_name', 'host') 
```
device_name needs to be filled in