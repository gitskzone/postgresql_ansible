from imp import reload
from flask import Flask, jsonify, render_template, session, url_for, redirect
from pathlib import Path
from module.inventory import *
from github import Github
import os
import yaml


app = Flask(__name__)
app.config['SECRET_KEY'] = "SuperSecretTestKey"

github_branch = "dev"
inventory_path = "inventory"

def get_repo():
    github_token = os.environ.get('GITHUB_TOKEN')
    g = Github(github_token)
    repo = g.get_repo("gitskzone/postgresql_ansible")
    return repo

def get_env_defaults():
    repo = get_repo()
    contents = repo.get_contents('/'.join([inventory_path,"_defaults.yaml"]),ref=github_branch)
    yaml_dict = defaultdict(dict)
    yaml_dict = yaml.safe_load(contents.decoded_content.decode())
    return yaml_dict

def get_cluster_content(env,cluster):
    repo = get_repo()
    contents = repo.get_contents('/'.join([inventory_path,env,cluster]),ref=github_branch)
    yaml_dict = defaultdict(dict)
    item_name = '.'.join([cluster.replace('.yaml',''), env])
    yaml_dict[item_name] = yaml.safe_load(contents.decoded_content.decode())
    yaml_dict[item_name]['environment'] = env
    return yaml_dict

@app.route("/reload")
def reload():
    environment_list = get_environment_list()
    session['environment_list'] = environment_list
    return redirect(url_for('.list_environments'))

@app.route("/")
def list_environments():
    environment_list = session.get('environment_list',[])
    return render_template('list.html', data=environment_list, type="env")

@app.route("/env/<env>")
def list_clusters(env=None):
    cluster_list = get_cluster_list(env)
    session['env'] = env
    return render_template('list.html', data=cluster_list, type="cluster")


def get_environment_list():
    repo = get_repo()
    environment_list = []
    contents = repo.get_contents(inventory_path, ref=github_branch)
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            environment_list.append(file_content.name)

    return(environment_list)


def get_cluster_list(env):
    repo = get_repo()
    cluster_list = []
    contents = repo.get_contents('/'.join([inventory_path,env]), ref=github_branch)
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "file":
            cluster_list.append(file_content.name)

    return(cluster_list)

@app.route("/cluster/<cluster>")
def cluster(cluster=None):
    env = session.get("env","")
    defaults = get_env_defaults()
    cluster = get_cluster_content(env, cluster)
    hosts = get_hosts(cluster, defaults)
    return jsonify(hosts) #render_template('cluster.html', data=cluster)


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=True)
