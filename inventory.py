#! /usr/bin/env python3

from pathlib import Path
import yaml
import json
from collections import defaultdict
import argparse
from pydantic.utils import deep_update
from module.inventory import *


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument('--list', action='store_true', help='Output all hosts info')
group.add_argument('--host', type=str, action='store',
                   help='Output specific host info')
group.add_argument('--group', type=str, action='store',
                   help='Output all hosts info in specified group')
parser.add_argument_group(group)
parser.add_argument('--env', type=str, required=False, default=None,
                    help='Filter output by environment folder [default: None]')

args = parser.parse_args()




def main():

    inventory_root = Path(__file__).parent.joinpath('inventory')
    defaults_file = inventory_root.joinpath('_defaults.yaml')

    if args.env == None:
        inventory = inventory_root
    else:
        inventory = inventory_root.joinpath(args.env)

    file_list = [path for path in inventory.rglob(
        '*.yaml') if path != defaults_file and path.is_file]

    inventory_items = read_inventory_files(file_list)
    inventory_defaults = read_yaml_file(str(defaults_file))

    if args.host != None:
        hosts = get_hosts(inventory_items, inventory_defaults, host=args.host)
    elif args.group != None:
        hosts = get_hosts(
            inventory_items, inventory_defaults, group=args.group)
    else:
        hosts = get_hosts(inventory_items, inventory_defaults)

    print(json.dumps(hosts, indent=4))


if __name__ == "__main__":
    main()
