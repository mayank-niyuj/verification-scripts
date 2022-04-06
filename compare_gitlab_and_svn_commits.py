import os
from sys import set_coroutine_origin_tracking_depth
import gitlab
# import sqlite3
import svn.remote
from pprint import pprint
from dotenv import load_dotenv
import pandas as pd
from contextlib import suppress

load_dotenv()

gl = gitlab.Gitlab(os.getenv("GITLAB_URL"), os.getenv("GITLAB_TOKEN"))
gl.auth()

svn_repo="ilsubversion/sp"
gitlab_repo_id=121

with suppress(FileNotFoundError):
    os.remove("compare_result.csv")


def svn_commits(repo, project):
    '''
    This function will store timestamp, commit_message and user of SVN repository
    '''

    branches = svn.remote.RemoteClient(repo)
    # compare_result = {"commit_message": [], "source": []}
    compare_result = {"commit_message": [],"repo": [], "source": []}

    status={"repo":[], "branch":[], "status": []}

    df = None

    with suppress(FileNotFoundError):
        df = pd.read_csv("status.csv").to_dict()
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
            
                print("branches ; ", branch)
                branch_url = f"http://localhost:81/svn/ilsubversion/sp/branches/{branch}"
                client = svn.remote.RemoteClient(branch_url)
                svn_commit_details = {"commit_message": [], "time": [], "svn_user": []}
                gl_commit_details = {"commit_message": [], "time": [], "gl_user": []}

                for commit in client.log_default():
                    # print(commit)
                    timestamp = commit.date
                    commit_message = commit.msg
                    time = str(timestamp).split('.')[0]
                    svn_user = commit.author
                    svn_commit_details["commit_message"].append(commit_message+ " " +time)
                    svn_commit_details["time"].append(time)
                    svn_commit_details["svn_user"].append(svn_user)


                commits = project.commits.list(ref_name=branch[:-1])
                
                for commit in commits:
                    # print(commit)
                    commit_message = commit.title
                    time = " ".join(str(commit.committed_date).split("T")).split(".")[0]
                    gitlab_user = commit.author_name
                    gl_commit_details["commit_message"].append(commit_message + " " + time)
                    gl_commit_details["time"].append(time)
                    gl_commit_details["gl_user"].append(gitlab_user)

                print("SVN : ", svn_commit_details)
                print("GITLAB : ", gl_commit_details)

                difference = [message for message in svn_commit_details["commit_message"] if message not in gl_commit_details["commit_message"]]
                # print(difference)
                if difference:
                    compare_result["commit_message"].append(difference)
                    compare_result["repo"].append(project.name)
                    compare_result["source"].append("gitlab")
                branch_status="success"
            # break

        except Exception as e:
            print(e)
            branch_status="fails"
        
        # if key:    # pprint(compare_result)
        status["repo"].append(project.name)
        status["branch"].append(branch)
        status["status"].append(branch_status)

    pprint(status)
    df = pd.DataFrame(status)
    if os.path.exists("status.csv"):
        os.remove("status.csv")

    df.to_csv("status.csv", index=False)
        # df.to_csv("status.csv", mode="a", index=False, header=False)
    # else:
        # df.to_csv("status.csv", index=False)

    # pprint(compare_result)
    df = pd.DataFrame(compare_result)
    if os.path.exists("compare_result.csv"):
        df.to_csv("compare_result.csv", mode="a", index=False, header=False)
    else:
        df.to_csv("compare_result.csv", index=False)


# import pdb;pdb.set_trace()
data = svn_commits("http://localhost:81/svn/{}/branches/".format(svn_repo), gl.projects.get(gitlab_repo_id))

# cur.execute("select * from repos where is_success='FALSE'")
# rows = cur.fetchall()
# for row in rows:
#     print("======================================================================")
#     print("SVN", row)

#     print(cur.execute("select count(*) from gitlab_repos where name='%s'"%(row[1])))
#     if cur.fetchall()[0][0] > 0:
#         cur.execute("update repos SET is_success='TRUE' where name='%s';"%(row[1]))
#         con.commit()    
#     else:
#         print("Not Matched")



# con.commit()
# con.close()
