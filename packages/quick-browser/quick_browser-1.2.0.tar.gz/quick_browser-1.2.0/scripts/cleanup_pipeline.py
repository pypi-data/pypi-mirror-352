import requests

# Konfiguration
GITEA_TOKEN = "a0b99df9e9b5742d8f322a196054bb29f28c1272"
GITEA_API_URL = "https://git.noircoding.de/api/v1"
OWNER = "noirpi"
REPO = "quick-browser"

HEADERS = {
    "Authorization": f"token {GITEA_TOKEN}",
    "Content-Type": "application/json",
}

def get_failed_workflows(page=1, per_page=30):
    url = f"{GITEA_API_URL}/repos/{OWNER}/{REPO}/actions/runs"
    params = {
        "status": "failure",
        "page": page,
        "limit": per_page
    }
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    return resp.json()

def delete_workflow(run_id):
    url = f"{GITEA_API_URL}/repos/{OWNER}/{REPO}/actions/runs/{run_id}"
    resp = requests.delete(url, headers=HEADERS)
    if resp.status_code == 204:
        print(f"✅ Workflow run {run_id} deleted.")
    else:
        print(f"❌ Failed to delete workflow run {run_id}. Status: {resp.status_code}")

def main():
    page = 1
    while True:
        data = get_failed_workflows(page=page)
        runs = data.get("workflow_runs") or data.get("runs") or data.get("actions_runs") or data.get("actions") or []
        if not runs:
            print("No more failed workflow runs found.")
            break

        for run in runs:
            run_id = run["id"]
            print(f"Deleting failed workflow run {run_id}...")
            delete_workflow(run_id)

        page += 1

if __name__ == "__main__":
    main()
