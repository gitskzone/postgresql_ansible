# postgresql_ansible
ansible code related to postgresql provisioning


Install PostgreSQL (working on ubuntu 19.04)
sudo apt-get install postgresql-11 postgresql-client-11

/usr/lib/postgresql/11/bin/pg_ctl -D /var/lib/postgresql/11/main -l logfile start

declare -x PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin"