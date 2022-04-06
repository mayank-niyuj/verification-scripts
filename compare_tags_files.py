import pandas as pd
import svn.remote
import gitlab
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

# Authenticating to Gitlab with environment variables
gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))
gl.auth()

# Mention the path of svn branches,tags and trunk if it's not on root directory
svn_repo="ilsubversion/sp"

# Mention the GitLab project id which you have migrated from SVN
gitlab_repo_id=121

def print_files(repo, project):
    """
    This function will list all the files of SVN.

    :param repo: This is the link of SVN repository
    """
    tags = svn.remote.RemoteClient(repo)
    files_list = {}
    folder = ""
   
    compare_result = {"file": [], "source": [], "repo": [],"tag":[]}
    status={"repo":[], "tag":[], "status": []}

    for tag in tags.list():
        try:

            # print("tags ; ", tag)
            tag_url = f"http://localhost:81/svn/ilsubversion/sp/tags/{tag}"
            client = svn.remote.RemoteClient(tag_url)

            svn_files = []
            gl_files = []

            entries = list(client.list_recursive())
            # print(entries)

            for files_set in entries:
                folder = files_set[0]
                svn_files.append(folder + "/" + files_set[1]["name"] if folder else files_set[1]["name"])

            # for project in projects:          
            items = project.repository_tree(path="", recursive=True, all=True, ref=tag.strip("/"))
            for item in items:
                if item["type"] != "tree":
                    gl_files.append(item["path"])

            difference = [file for file in svn_files if file not in gl_files]
            if difference:
                compare_result["file"].append(difference)
                compare_result["source"].append("gitlab")
                compare_result["repo"].append(project.name)
                compare_result["tag"].append(tag)
            tag_status="success"
            
        except Exception as e:
            print(e)
            tag_status="fails"
            break

        status["repo"].append(project.name)
        status["tag"].append(tag)
        status["status"].append(tag_status)

    df = pd.DataFrame(status)
    if os.path.exists("tag_file_status.csv"):
        df.to_csv("tag_file_status.csv", mode="a", index=False, header=False)
    else:
        df.to_csv("tag_file_status.csv", index=False)

    pprint(compare_result)
    df = pd.DataFrame(compare_result)
    if os.path.exists("tag_file_compare_result.csv"):
        df.to_csv("tag_file_compare_result.csv", mode="a", index=False, header=False)
    else:
        df.to_csv("tag_file_compare_result.csv", index=False)

files_list = print_files("http://localhost:81/svn/{}".format(svn_repo), gl.projects.get(gitlab_repo_id))