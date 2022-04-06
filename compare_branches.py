import gitlab
import svn.remote
# import yaml
import os
from dotenv import load_dotenv

load_dotenv()

# Loading repository list
# with open('/home/mayank/migration-test/subdir/repo.yaml', 'r') as file:
#     repositories = yaml.safe_load(file)["repo"]

svn_repo_branch = {}

# Iterating over the SVN branches
# for repo in repositories:
repo="ilsubversion/sp"
data = svn.remote.RemoteClient('http://localhost:81/svn/{}/branches/'.format(repo))
branches = data.list()
for branch in branches:
    branch = branch.split("/")[0]
    svn_repo_branch[repo] = svn_repo_branch.get(repo, [])
    svn_repo_branch[repo].append(branch)
    svn_repo_branch[repo] = sorted(svn_repo_branch[repo])

print("SVN repository branches -> {}".format(svn_repo_branch))

# Authenticating to Gitlab with environment variables
gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))
gl.auth()

gitlab_repo_branch = {}

projects = gl.projects.list()

# Iterating over the Gitlab branches
for project in projects:
    branches = project.branches.list()
    for branch in branches:
        gitlab_repo_branch[project.name] = gitlab_repo_branch.get(project.name, [])
        gitlab_repo_branch[project.name].append(branch.name)
        gitlab_repo_branch[project.name] = sorted(gitlab_repo_branch[project.name])
print("GitLab repository branches -> {}".format(gitlab_repo_branch))

try:
    for repo, branches in svn_repo_branch.items():
        if not repo in gitlab_repo_branch:        
            raise Exception("Repository '{}' not found on Gitlab".format(repo))
        for branch in branches:
            if branch not in gitlab_repo_branch[repo]:
                raise Exception("Branch '{}' not present on GitLab in repository {}".format(branch, repo))

    print("All SVN branches of repository '{}' are present on GitLab.".format(repo))
except Exception as e:
    print(e)
