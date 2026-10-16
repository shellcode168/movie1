import os, json, time, random, datetime
from github import Github, GithubException

TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
NODE_ID = os.getenv("NODE_INDEX", "1")
QUEUE_FILE = "tasks_queue/current_batch.json"

def run():
    if not TOKEN or not REPO_NAME:
        print("未检测到 GITHUB_TOKEN，跳过运行。")
        return
    repo = Github(TOKEN).get_repo(REPO_NAME)
    for _ in range(5):
        try:
            c = repo.get_contents(QUEUE_FILE)
            data = json.loads(c.decoded_content.decode("utf-8"))
            task = next((t for t in data["tasks"] if t["status"] == "PENDING" and t["priority"] == "NORMAL"), None)
            if not task:
                print(f"🟢 [Node #{NODE_ID}] 暂无待抢常规任务。")
                return
            task["status"] = f"COMPLETED_BY_ACTION_NODE_{NODE_ID}"
            task["completed_at"] = datetime.datetime.utcnow().isoformat()
            repo.update_file(c.path, f"Node #{NODE_ID} completed {task['task_id']} [skip ci]", json.dumps(data, indent=2, ensure_ascii=False), c.sha)
            print(f"✔ [Node #{NODE_ID}] 成功认领并完成: {task['task_id']}")
            break
        except GithubException as e:
            if e.status == 409:
                time.sleep(random.uniform(0.5, 2.5))
            else:
                raise e

if __name__ == "__main__":
    run()
