import pandas as pd
import svn.remote
import gitlab
import os
from dotenv import load_dotenv
from pprint import pprint
from contextlib import suppress

load_dotenv()

# Authenticating to Gitlab with environment variables
gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))
gl.auth()

svn_repo="ilsubversion/sp/branches"
gitlab_repo_id=121

with suppress(FileNotFoundError):
    os.remove("file_compare_result.csv")

def print_files(repo, project):
    """
    This function will list all the files of SVN.

    :param repo: This is the link of SVN repository
    """
    branches = svn.remote.RemoteClient(repo)
    files_list = {}
    folder = ""
   
    compare_result = {"file": [], "source": [], "repo": [], "branch":[]}
    status={"repo":[], "branch":[], "status": []}

    df = None

    with suppress(FileNotFoundError):
        df = pd.read_csv("file_status.csv").to_dict()
        print(df)

    for branch in branches.list():
        try:
            key = None
            if df:
                for _key, _branch in df["branch"].items():
                    if branch == _branch:
                        key = str(_key)
                        break
        
            if key and df["status"][int(key)] == "success":
                status["repo"].append(project.name)
                status["branch"].append(branch)
                status["status"].append("success")
                continue
            else:

                # print("branches ; ", branch)
                branch_url = f"http://localhost:81/svn/ilsubversion/sp/branches/{branch}"
                client = svn.remote.RemoteClient(branch_url)

                svn_files = []
                gl_files = []

                entries = list(client.list_recursive())
                # print(entries)

                for files_set in entries:
                    folder = files_set[0]
                    svn_files.append(folder + "/" + files_set[1]["name"] if folder else files_set[1]["name"])

                # for project in projects:          
                items = project.repository_tree(path="", recursive=True, all=True, ref=branch.strip("/"))
                for item in items:
                    if item["type"] != "tree":
                        print(type(item))
                        gl_files.append(item["path"])

                difference = [file for file in svn_files if file not in gl_files]
                if difference:
                    compare_result["file"].append(difference)
                    compare_result["source"].append("gitlab")
                    compare_result["repo"].append(project.name)
                    compare_result["branch"].append(branch)
                branch_status="success"
        
        except Exception as e:
            print(e)
            branch_status="fails"
            break

        status["repo"].append(project.name)
        status["branch"].append(branch)
        status["status"].append(branch_status)

    df = pd.DataFrame(status)
    if os.path.exists("file_status.csv"):
        os.remove("file_status.csv")

    df.to_csv("file_status.csv", index=False)

    df = pd.DataFrame(compare_result)
    if os.path.exists("file_compare_result.csv"):
        df.to_csv("file_compare_result.csv", mode="a", index=False, header=False)
    else:
        df.to_csv("file_compare_result.csv", index=False)

files_list = print_files("http://localhost:81/svn/{}".format(svn_repo), gl.projects.get(gitlab_repo_id))