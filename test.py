from github import Github
import os

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')

# using an access token
g = Github(GITHUB_TOKEN)

# Github Enterprise with custom hostname
#g = Github(base_url="https://github.com/api/v3", login_or_token=GITHUB_TOKEN)
branch = "dev"
inventory_path = "inventory"

repo = g.get_repo("gitskzone/postgresql_ansible")
#repo.get_branch(branch="dev")
contents = repo.get_contents(inventory_path, ref=branch)
while contents:
    file_content = contents.pop(0)
    if file_content.type == "dir":
        contents.extend(repo.get_contents(file_content.path, ref=branch))
    else:
        print(file_content.decoded_content.decode())

