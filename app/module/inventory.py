#! /usr/bin/env python3

from pathlib import Path
import yaml
import json
from collections import defaultdict
import argparse
from pydantic.utils import deep_update


# parser = argparse.ArgumentParser()
# group = parser.add_mutually_exclusive_group()
# group.add_argument('--list', action='store_true', help='Output all hosts info')
# group.add_argument('--host', type=str, action='store',
#                    help='Output specific host info')
# group.add_argument('--group', type=str, action='store',
#                    help='Output all hosts info in specified group')
# parser.add_argument_group(group)
# parser.add_argument('--env', type=str, required=False, default=None,
#                     help='Filter output by environment folder [default: None]')

# args = parser.parse_args()


def read_inventory_files(file_list):
    yaml_dict = defaultdict(dict)
    for file in file_list:
        item_name = '.'.join([file.stem, file.parts[-2]])
        with open(file, 'r') as stream:
            yaml_dict[item_name] = yaml.safe_load(stream)
            yaml_dict[item_name]['environment'] = file.parts[-2]
    return yaml_dict


def read_yaml_file(filepath):
    yaml_dict = defaultdict(dict)
    with open(filepath, 'r') as stream:
        yaml_dict = yaml.safe_load(stream)
    return yaml_dict


def host_type(type):
    types = {
        "standalone": 1,
        "manual_failover": 2,
        "auto_failover": 3
    }
    return(types[type])


def get_layout(inventory_item, defaults):
    # check if layout, otherwise use defaults
    layout = defaultdict(dict)
    if 'layout' in inventory_item:
        layout['regions'] = dict(inventory_item['layout'])
    else:
        layout['regions'][inventory_item['primary_region']] = dict(
            defaults[inventory_item['type']][inventory_item['primary_region']]['az_layout'])
        if inventory_item.get('dr_enabled', False):
            layout['regions'].update(
                defaults[inventory_item['type']][inventory_item['primary_region']]['dr'])

    layout['primary_region'] = inventory_item['primary_region']
    layout['primary_az'] = inventory_item['primary_az']

    host_count = 0
    host_order = []
    for region_key, region_value in layout['regions'].items():
        host_region_index = 0
        for az_key, az_count in region_value.items():
            for ix in range(az_count):
                host_region_index += 1
                if region_key == inventory_item['primary_region'] and az_key == inventory_item['primary_az']:
                    data = {"region": region_key,
                                          "az": az_key,
                                          "primary_region": True,
                                          "primary_az": True,
                                          "host_region_index": host_region_index
                                          }
                    if (len(host_order) > 0 and host_order[0].get("region", None) != inventory_item['primary_region'] and 
                        host_order[0].get("az", None) != inventory_item['primary_az']):
                        host_order.insert(0, data)
                    else:
                        host_order.append(data)
                elif region_key == inventory_item['primary_region'] and az_key != inventory_item['primary_az']:
                    host_order.append({"region": region_key,
                                       "az": az_key,
                                       "primary_region": True,
                                       "primary_az": False,
                                       "host_region_index": host_region_index
                                       })
                else:
                    host_order.append({"region": region_key,
                                       "az": az_key,
                                       "primary_region": False,
                                       "primary_az": False,
                                       "host_region_index": host_region_index
                                       })
                host_count += 1

    layout['order_list'] = host_order
    layout['host_count'] = host_count

    return layout


def get_hosts(inventory_items, defaults):
    hosts = defaultdict(dict)
    for k, v in inventory_items.items():
        host_info = deep_update(defaults[v['environment']], v)
        layout = get_layout(host_info, defaults)
        ix = 0
        for target in layout['order_list']:
            ix += 1
            inventory_name = '.'.join(
                [host_info['name'] + '-' + str(ix), host_info['environment']])
            host = host_info.copy()
            host['layout'] = layout
            host['host_index'] = ix
            host.update(target)
            host['layout'].pop('order_list', None)

            hosts[inventory_name] = host

    return hosts


# def main():

#     inventory_root = Path(__file__).parent.parent.joinpath('inventory')
#     defaults_file = inventory_root.joinpath('_defaults.yaml')

#     if args.env == None:
#         inventory = inventory_root
#     else:
#         inventory = inventory_root.joinpath(args.env)

#     file_list = [path for path in inventory.rglob(
#         '*.yaml') if path != defaults_file and path.is_file]

#     inventory_items = read_inventory_files(file_list)
#     inventory_defaults = read_yaml_file(str(defaults_file))

#     if args.host != None:
#         hosts = get_hosts(inventory_items, inventory_defaults, host=args.host)
#     elif args.group != None:
#         hosts = get_hosts(
#             inventory_items, inventory_defaults, group=args.group)
#     else:
#         hosts = get_hosts(inventory_items, inventory_defaults)

#     print(json.dumps(hosts, indent=4))


# if __name__ == "__main__":
#     main()
