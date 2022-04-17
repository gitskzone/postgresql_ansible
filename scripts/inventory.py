#! /usr/bin/env python3

import collections
from pathlib import Path
import yaml
import json
from collections import defaultdict


def host_type(type):
    types = {
        "standalone": 1,
        "manual_failover": 2,
        "auto_failover": 3
    }
    return(types[type])

def read_yaml_files(file_list):

    yaml_dict = defaultdict(dict)
    for file in file_list:
        item_name = '.'.join([file.stem,file.parts[-2]])
        with open(file, 'r') as stream:
            try:
                yaml_dict[item_name]=yaml.safe_load(stream)
                yaml_dict[item_name]['environment'] = file.parts[-2]

            except yaml.YAMLError as exc:
                print(exc)
    return yaml_dict

def get_hosts(clusters):
    hosts = defaultdict(dict)
    for k,v in clusters.items():
        for ix in range(host_type(v['type'])):
            inventory_name = '.'.join([v['name'],v['environment'],v['primary_dc'],v['primary_az']])
            hosts[inventory_name] = v
            hosts[inventory_name]['index'] = ix



    return hosts

def main():

    inventory = Path(__file__).parent.parent.joinpath('inventory')
    file_list = [path for path in inventory.rglob('*.yaml') if not '_defaults.yaml' in path.name and path.is_file]

    items = read_yaml_files(file_list)
    hosts = get_hosts(items)
    
    
    
    print(json.dumps(hosts, indent=4))



if __name__ == "__main__":
    main()