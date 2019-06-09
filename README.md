# postgresql_ansible
Ansible code related to postgresql database provisioning from declarative yaml.

The future goal is for this to be implemented in a fully automated jenkins pipeline to allow for self service database provisioning using GIT pull requests.</br>
Initially will need to have this manually triggered from an AWX job after pr merge.</br>
Built from a DBA perspective so developers can get new databases with minimal DBA intervention.</br>

__Current Features:__</br>
* Basic database properties declared in var files, 1 per db that can be used for initial provisioning of a database along with other attributes.
* Use of a template_version to allow implementation of what could be breaking changes to the playbooks while still allowing previously created database definitions to be re-processed.
* Tested processing on localhost only although via ssh so should work for remote connections.
* Uses the standard postgresql ansible modules to make changes.
* Adding extensions to databases.
* Creating logins and database level permissions.
* Schemas and any schema extensions.
* Roles (nologin) with object permissions within a schema defined.
 * This has been kept simple for the moment with the expection that any object perms would be implemented by dev as part of code deployment.
 * Will create specified permissions for all objects in the schema and then set default perms for new tables within that schema.
* Add logins to the specified roles.

__To Do:__</br>
* Implement dns cname creation for each database.
* File/Folder structure multi remote PostgreSQL cluster processing testing
* Additional metadata to be captured and posted to custom inventory via webapi for reporting.
 * e.g. Who's created the database, purpose, etc...
* Default privs needs improving as only doing for tables.


__Notes:__</br>
Only tested with explicit table type privs or all, need to test handling functions etc...</br>
Current test definitions are stored: _./clusters/ubuntu/*.yaml_</br>


__Examples:__</br>
```
ansible-playbook -i inventory/ playbooks/deploy_databases.yaml
```

__Setup notes__</br>
Install PostgreSQL (tested on vm using ubuntu 19.04) </br>
```
sudo apt-get install postgresql-11 postgresql-client-11
sudo -u postgres -i
/usr/lib/postgresql/11/bin/pg_ctl -D /var/lib/postgresql/11/main -l logfile start
```
