from imp import reload
from flask import Flask, jsonify, render_template
from pathlib import Path
from module.inventory import *

app = Flask(__name__)

inventory_root = Path(__file__).parent.joinpath('inventory')
defaults_file = inventory_root.joinpath('_defaults.yaml')

inventory = inventory_root

file_list = [path for path in inventory.rglob('*.yaml') if path != defaults_file and path.is_file]
environments = [path.name for path in inventory.iterdir() if path.is_dir()]

inventory_items = read_inventory_files(file_list)
inventory_defaults = read_yaml_file(str(defaults_file))

hosts = get_hosts(inventory_items, inventory_defaults)

@app.route("/")
def list_environments():
    return render_template('environments.html', data=environments)

if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)