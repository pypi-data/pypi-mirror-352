import subprocess
import time
from intctl.status import StatusManager


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def create_kubernetes_cluster(cfg: dict, status: StatusManager) -> None:
    status.start("kubernetes")
    project = cfg["project_id"]
    region = cfg["region"]
    workspace = cfg["workspace_uuid"]
    cluster_name = f"int-{workspace}".lower()

    print(f"🔍 Checking if Kubernetes cluster '{cluster_name}' exists...")

    exists = run(
        f"gcloud container clusters describe {cluster_name} "
        f"--region={region} --project={project}"
    )
    if exists.returncode == 0:
        print(f"✅ Cluster '{cluster_name}' already exists in region '{region}'.")
        status.complete("kubernetes")
        return

    print(f"🚀 Creating Autopilot GKE cluster '{cluster_name}' in {region}...")

    result = run(
        f"gcloud container clusters create-auto {cluster_name} "
        f"--region={region} --project={project}"
    )

    if result.returncode == 0:
        print(f"✅ Cluster '{cluster_name}' created.")
        status.complete("kubernetes")
        return

    print("❌ Failed to create GKE cluster.")
    print(result.stderr.strip())

    print(f"""
🔐 You might not have permission, or there may be quota/policy issues.

Please create the cluster manually using the following command:

  gcloud container clusters create-auto {cluster_name} \\
      --region={region} --project={project}

⏳ Waiting until the cluster '{cluster_name}' is created...
""")

    # Retry loop to poll for existence
    while True:
        time.sleep(10)
        check = run(
            f"gcloud container clusters describe {cluster_name} "
            f"--region={region} --project={project}"
        )
        if check.returncode == 0:
            print(f"✅ Cluster '{cluster_name}' has been created.")
            break
        else:
            print("⏳ Still waiting for cluster...")

    status.complete("kubernetes")
