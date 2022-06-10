# from imp import reload
from flask import Flask, jsonify, render_template, session, url_for, redirect, request
from pathlib import Path
from module.inventory import *
from github import Github
import os
import yaml
from flask_bootstrap import Bootstrap
# from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField, SelectField, BooleanField, FormField
# from wtforms.validators import DataRequired
# from module.forms import *
from redis_collections import Dict, List
from redis import StrictRedis


app = Flask(__name__)
app.config['SECRET_KEY'] = "SuperSecretTestKey"
Bootstrap(app)

github_branch = "dev"
inventory_path = "inventory"
yaml_dict = defaultdict(dict)

conn = StrictRedis(host='localhost', port=6379)
rd_clusters = Dict(redis=conn, writeback=True, key="clusters")
rd_defaults = Dict(redis=conn, writeback=True, key="defaults")
rd_envs = List(redis=conn, writeback=True, key="envs")


def get_repo():
    github_token = os.environ.get('GITHUB_TOKEN')
    g = Github(github_token)
    repo = g.get_repo("gitskzone/postgresql_ansible")
    return repo

# def get_env_defaults():
#     repo = get_repo()
#     contents = repo.get_contents('/'.join([inventory_path,"_defaults.yaml"]),ref=github_branch)
#     # yaml_dict = defaultdict(dict)
#     yaml_dict = yaml.safe_load(contents.decoded_content.decode())
#     return yaml_dict

def read_git_content():
    repo = get_repo()
    inventory = inventory_path
    clusters = defaultdict(dict)
    environments = set()
    defaults = defaultdict(dict)

    contents = repo.get_contents(inventory, ref=github_branch)
    
    while contents:
        file_content = contents.pop(0)
        if file_content.type == "dir":
            contents.extend(repo.get_contents(file_content.path, ref=github_branch))
        else:
            env_name = file_content.path.split('/')[-2]
            if file_content.name == '_defaults.yaml':
                defaults[env_name] = yaml.safe_load(file_content.decoded_content.decode())
            else:
                item_name = file_content.name.split('.')[0]
                clusters[env_name][item_name] = yaml.safe_load(file_content.decoded_content.decode())
                clusters[env_name][item_name]['environment'] = env_name
                environments.add(env_name)

    rd_clusters.clear()
    rd_clusters.update(clusters)

    rd_defaults.clear()
    rd_defaults.update(defaults)

    rd_envs.clear()
    rd_envs.extend(list(environments))

    return
                
# def get_cluster_content(env=None,cluster=None):
#     repo = get_repo()

#     if env != None:
#         inventory = '/'.join([inventory_path,env])
#     else:
#         inventory = inventory_path
#     if cluster == None:
#         contents = repo.get_contents(inventory, ref=github_branch)
#         while contents:
#             file_content = contents.pop(0)
#             if file_content.type == "dir":
#                 contents.extend(repo.get_contents(file_content.path, ref=github_branch))
#             else:
#                 if file_content.name != '_defaults.yaml':
#                     item_name = file_content.name.split('.')[0]
#                     yaml_dict[item_name] = yaml.safe_load(file_content.decoded_content.decode())
#                     yaml_dict[item_name]['environment'] = file_content.path.split('/')[-2]
#     else:
#         file_content = repo.get_contents('/'.join([inventory,cluster]),ref=github_branch)
#         item_name = file_content.name.split('.')[0]
#         yaml_dict[item_name] = yaml.safe_load(file_content.decoded_content.decode())
#         yaml_dict[item_name]['environment'] = file_content.path.split('/')[-2]
#     return yaml_dict

@app.route("/reload")
def reload():
    read_git_content()
    # environment_list = get_environment_list()
    # session['environment_list'] = environment_list
    return redirect(url_for('.clusters'))

# @app.route("/")
# def list_environments():
#     environment_list = session.get('environment_list',[])
#     return render_template('list_envs.html', data=environment_list)

# @app.route("/env/<env>")
# def list_clusters(env=None):
#     session['env'] = env
#     all_clusters = get_cluster_content(env)
#     #cluster_list = get_cluster_list(env)
#     cluster_list = [item for item in all_clusters]
#     # for k,v in all_clusters.items():
#     #     cluster_list.append(v['name'])

#     return render_template('list.html', data=cluster_list, type="cluster")

@app.route("/")
@app.route("/clusters/<env>")
@app.route("/clusters/<env>/<cluster>")
def clusters(env=None, cluster=None):

    if env == None and cluster == None:
        environment_list = rd_envs
        if len(rd_envs) == 0:
            return render_template('list_envs.html', data=[], msg="No data loaded")
        else:
            return render_template('list_envs.html', data=environment_list)
    elif env != None and cluster == None:
        all_clusters = rd_clusters[env]
        cluster_list = [item for item in all_clusters]
        return render_template('list_clusters.html', data=cluster_list, env=env)
    else:
        cluster_detail = rd_clusters[env][cluster]
        output_type = request.args.get('format', 'json')
        if output_type == 'yaml':
            output = yaml.dump(cluster_detail, default_flow_style=False, sort_keys=False)
        else:
            output = json.dumps(cluster_detail,indent=2, sort_keys=False)

        return render_template('show_cluster.html', data=output, env=env, cluster=cluster) 

        #return render_template('show_cluster.html', data=json.dumps(cluster_detail,indent=2), env=env, cluster=cluster) 


# @app.route("/")
# @app.route("/clusters/<env>")
# @app.route("/clusters/<env>/<cluster>")
# def clusters(env=None, cluster=None):

#     if env == None and cluster == None:
#         environment_list = session.get('environment_list',[])
#         return render_template('list_envs.html', data=environment_list)
#     elif env != None and cluster == None:
#         all_clusters = get_cluster_content(env)
#         cluster_list = [item for item in all_clusters]
#         return render_template('list_clusters.html', data=cluster_list, env=env)
#     else:
#         cluster_detail = yaml_dict[cluster]
#         # return jsonify(cluster_detail)
#         return render_template('show_cluster.html', data=json.dumps(cluster_detail,indent=2), env=env, cluster=cluster) 


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

# @app.route("/cluster/<cluster>")
# def cluster(cluster=None):
#     env = session.get("env","")
#     cluster_detail = yaml_dict[cluster]
#     # defaults = get_env_defaults()
#     # cluster = get_cluster_content(env, cluster)
#     # hosts = get_hosts(cluster, defaults)
#     return jsonify(cluster_detail) #render_template('cluster.html', data=cluster)






# @app.route('/create', methods=['GET', 'POST'])
# def create():
#     names = ['alpha','beta']
#     # you must tell the variable 'form' what you named the class, above
#     # 'form' is the variable name used in this template: index.html
#     form = NameForm()
#     message = ""
#     if form.validate_on_submit():
#         name = form.name.data
#         type = form.type.data
#         version = form.version.data
#         primary_region = form.primary_region.data
#         primary_az = form.primary_az.data
#         dr_enabled = form.dr_enabled.data
#         if name.lower() in names:
#             # empty the form field
#             form.name.data = ""
#             id = names.get(name,'Unknown')
#             # redirect the browser to another route and template
#             return redirect( url_for('actor', id=id) )
#         else:
#             message = "That actor is not in our database."
#     return render_template('create.html', names=names, form=form, message=message)

if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=False)
