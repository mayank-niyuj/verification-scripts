import gitlab
import svn.remote
# import yaml
import os
from dotenv import load_dotenv

load_dotenv()

# Loading repository list
# with open('/home/mayank/migration-test/subdir/repo.yaml', 'r') as file:
#     repositories = yaml.safe_load(file)["repo"]

svn_repo_tag = {}

# Iterating over the SVN tags
# for repo in repositories:
repo="ilsubversion/sp"
data = svn.remote.RemoteClient('http://localhost:81/svn/{}/tags/'.format(repo))
tags = data.list()
for tag in tags:
    tag = tag.split("/")[0]
    svn_repo_tag[repo] = svn_repo_tag.get(repo, [])
    svn_repo_tag[repo].append(tag)
    svn_repo_tag[repo] = sorted(svn_repo_tag[repo])

print("SVN repo tags -> {}".format(svn_repo_tag))

# Authenticating to Gitlab with environment variables
gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))
gl.auth()

gitlab_repo_tag = {}

projects = gl.projects.list()

# Iterating over the Gitlab tags
for project in projects:
    tags = project.tags.list()
    for tag in tags:
        gitlab_repo_tag[project.name] = gitlab_repo_tag.get(project.name, [])
        gitlab_repo_tag[project.name].append(tag.name)
        gitlab_repo_tag[project.name] = sorted(gitlab_repo_tag[project.name])
print("GitLab repository tags -> {}".format(gitlab_repo_tag))

try:
    for repo, tags in svn_repo_tag.items():
        if not repo in gitlab_repo_tag:        
            raise Exception("Repository '{}' not found on Gitlab".format(repo))
        for branch in tags:
            if branch not in gitlab_repo_tag[repo]:
                raise Exception("Tag '{}' not present on GitLab in repository {}".format(branch, repo))

    print("All SVN tags of repository {} are present on GitLab.".format(repo))
except Exception as e:
    print(e)
