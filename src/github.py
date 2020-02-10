import requests, time, psycopg2

github_accounts = {
        0: ['Githubfake01', '5RNsya*z#&aA'],
        1: ['GithubFake02', '9dJeg^Bp^g63'],
	    2: ['Github-Fake03', '2A$p3$zy%aaD'],
	    3: ['GithubFake04', '4Yg3&MQN9x%F'],
        4: ['GithubFake05', 'Cm82$$bFa!xb'],
        5: ['GithubFake06', '2t*u2Y8P^tTk'],
        6: ['GithubFake07', 'Hk1233**012'],
        7: ['GithubFake08', 'PO11sd*^%$']}

def parse_skills(text:str, database):
    text_skills = []
    items = []
    related_files = []
    lines = text.split("\n")
    for line in lines:
        if line[1:7] == "import":
            item = line[8:-1].lstrip().split(".")[-1]
            if item in database[0]:
                items.append(item)
                related_files.append([])
                text_skills.append([])
            else:
                continue
        else:
            continue
    return (items, text_skills, related_files)

def get_skills_db():
    conn = psycopg2.connect(
        user='postgres',
        password='1234',
        host='127.0.0.1',
        port='5432',
        database='dev'
    )
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM actor LIMIT 10')
    for row in cursor: print(row)
    conn.close()
    
    return ([], [])

def get_pull_requests(owner="Jabref", 
                      repo="jabref", 
                      min_val=0, 
                      max_val=100, 
                      limit=100, 
                      merged="true", 
                      state="closed", 
                      get_skills=True
                    ):
    empty = False
    index = min_val
    general_list = []
    pr_list = []
    skills_list = []
    db = []
    db = get_skills_db()

    while not empty:
        print(index)
        username = github_accounts[index%8][0]
        token = github_accounts[index%8][1]
        response = requests.get("https://api.github.com/repos/Jabref/jabref/pulls/%i?state=%s&merged=%s" % (index,state,merged), auth=(username,token))
        result = response.json()
        
        try:
            commit_response = requests.get("https://api.github.com/repos/JabRef/jabref/commits/%s" % result["head"]["sha"], auth=(username,token))
            commit_result = commit_response.json()
        except:
            pass

        try:
            status_response = requests.get("https://api.github.com/repos/JabRef/jabref/statuses/%s" % result["head"]["sha"], auth=(username,token))
            status_result = status_response.json()[0]
        except:
            status_result = {"state": "N/A"}
        

        def result_value(value, default):
            try:
                if len(value) == 1:
                    return result[value[0]]
                elif len(value) == 2:
                    return result[value[0]][value[1]]
                elif len(value) == 3:
                    return result[value[0]][value[1]][value[2]]
                elif len(value) == 4:
                    return result[value[0]][value[1]][value[2]][value[3]]
                else:
                    return default
            except:
                return default

        # General PR
        try:
            general = [
                index,
                result_value(["user", "login"], "N/A"),
                result_value(["user", "id"], "N/A"),
                result_value(["state"], "N/A"),
                result_value(["created_at"], "N/A"),
                result_value(["closed_at"], "N/A"),
                result_value(["title"], "N/A"),
                result_value(["body"], "N/A"),
                result_value(["comments"], "N/A"),
                result_value(["review_comments"], "N/A"),
                result_value(["additions"], "N/A"),
                result_value(["deletions"], "N/A"),
                result_value(["commits"], "N/A"),
                result_value(["changed_files"], "N/A")
            ]
        except Exception as ex:
            general = ["pull errored", str(ex)]

        def commit_value(value, default):
            try:
                if len(value) == 1:
                    return commit_result[value[0]]
                elif len(value) == 2:
                    return commit_result[value[0]][value[1]]
                elif len(value) == 3:
                    return commit_result[value[0]][value[1]][value[2]]
                elif len(value) == 4:
                    return commit_result[value[0]][value[1]][value[2]][value[3]]
                else:
                    return value
            except:
                return default

        # Per PR
        try:
            files = "["
            patch = "["
            for file in commit_result["files"]:
                files = files + file["filename"] + ", "
                patch = patch + file["patch"] + ", "
            files = files + "]"
            patch = patch + "]"
        except:
            pass

        try:
            data = []
            for file in commit_result["files"]:
                data.append(parse_skills(file["patch"], db))
            print(data)
        except:
            pass

        try:
            pr = [
                commit_value(["commit", "author", "name"], "N/A"),
                commit_value(["commit", "committer", "name"], "N/A"),
                index,
                commit_value(["sha"], "N/A"),
                commit_value(["commit", "message"], "N/A"),
                files,
                patch,
                commit_value(["stats", "additions"], "N/A"),
                commit_value(["stats", "deletions"], "N/A"),
                status_result["state"],
                commit_value(["stats", "total"], "N/A")
            ]
        except Exception as ex:
            pr = ["pull errored", str(ex)]
        
        try:
            result["message"]
        except:
            general_list.append(general)
            pr_list.append(pr)

        if int(response.headers["X-RateLimit-Remaining"]) < limit:
            time.sleep(int(response.headers["X-RateLimit-Reset"]))

        if index >= max_val:
            empty = True
        index += 1

    return (general_list, pr_list, skills_list)