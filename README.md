# Ansible-Device42: Lookup Plugin

## Introduction

This lookup plugin allows a playbook to fetch passwords or ip addresses for hosts from Device42. This can be especially interesting if users are trying to ssh into hosts to do some sort of task.

## Ansible Host Requirements
* Requests (http://docs.python-requests.org/en/master/)

## Configuration

Please set system environment variables:
```
D42_USER = 'device42 user'
D42_PWD = 'device42 password'
D42_URL = 'https:// device42 server IP address'
```

```
* Place d42.py in ansible/lib/ansible/plugins/lookup/
```

## Usage

```
To get password call: lookup('d42', 'device_name', 'password', 'username')
```
device_name and username need to be filled in
```
To run any doql request: lookup('d42', 'SELECT ... FROM ...', 'doql', False)
```
doql query need to be filled in + last boolean argument should add headers to the doql if True and show just plain csv result if False
