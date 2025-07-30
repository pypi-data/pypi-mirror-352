import os
import subprocess
import time
from typing import List
from intctl.status import StatusManager
from tqdm import tqdm


def run(cmd: str, input: str = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        shell=True,
        input=input,
        capture_output=True,
        text=True
    )


def wait_for_cluster(project: str, region: str, cluster_name: str):
    print(f"🔍 Waiting for GKE cluster '{cluster_name}' to become available...")
    while True:
        check = run(
            f"gcloud container clusters describe {cluster_name} "
            f"--region={region} --project={project}"
        )
        if check.returncode == 0:
            print(f"✅ Cluster '{cluster_name}' is available.")
            break
        print(f"⏳ Still waiting for cluster '{cluster_name}'...")
        time.sleep(10)


def transfer_and_deploy(cfg: dict, status: StatusManager):
    status.start("deploy")

    # Step 0: Config
    source_project = cfg.get("source_project", "source-project-id")
    source_location = cfg.get("source_location", "europe-west2")
    target_project = cfg["project_id"]
    target_location = cfg["region"]
    workspace = cfg["workspace_uuid"]
    target_repo = f"intellithing-{workspace}".lower()
    cluster_name = f"int-{workspace}".lower()
    images = ["secret-manager", "project-manager", "status-manager"]

    # Step 1: Docker auth
    for loc in [source_location, target_location]:
        while True:
            print(f"🔐 Authenticating Docker for {loc}-docker.pkg.dev...")
            auth_cmd = (
                f"gcloud auth print-access-token | "
                f"docker login -u oauth2accesstoken --password-stdin {loc}-docker.pkg.dev"
            )
            result = run(auth_cmd)
            if result.returncode == 0:
                break
            print(f"❌ Docker auth failed for {loc}. Retrying in 10s...\n{result.stderr.strip()}")
            time.sleep(10)

    # Step 2: Pull, tag, and push Docker images
    for image in tqdm(images, desc="📦 Pulling & Pushing Docker Images", unit="image"):
        src = f"{source_location}-docker.pkg.dev/{source_project}/intellithing/{image}:latest"
        tgt = f"{target_location}-docker.pkg.dev/{target_project}/{target_repo}/{image}:latest"

        while True:
            tqdm.write(f"📦 Pulling image: {src}")
            pull = run(f"docker pull {src}")
            if pull.returncode == 0:
                break
            tqdm.write(f"❌ Failed to pull {src}. Retrying in 10s...\n{pull.stderr.strip()}")
            time.sleep(10)

        run(f"docker tag {src} {tgt}")

        while True:
            tqdm.write(f"🚀 Pushing image: {tgt}")
            push = run(f"docker push {tgt}")
            if push.returncode == 0:
                break
            tqdm.write(f"❌ Failed to push {tgt}. Retrying in 10s...\n{push.stderr.strip()}")
            time.sleep(10)

    # Step 3: Wait for cluster and get credentials
    wait_for_cluster(target_project, target_location, cluster_name)

    while True:
        print(f"📡 Fetching GKE credentials for '{cluster_name}'...")
        creds = run(
            f"gcloud container clusters get-credentials {cluster_name} "
            f"--region={target_location} --project={target_project}"
        )
        if creds.returncode == 0:
            break
        print(f"❌ Failed to get GKE credentials. Retrying in 10s...\n{creds.stderr.strip()}")
        time.sleep(10)

    # Step 4: Patch secret
    key = os.environ.get("GCP_SERVICE_ACCOUNT_KEY")
    env = cfg.get("environment", "dev")
    if not key:
        print("❌ GCP_SERVICE_ACCOUNT_KEY environment variable is missing.")
        status.fail("deploy")
        return

    while True:
        print("🔧 Patching gcp-creds secret...")
        patch_cmd = (
            f"kubectl patch secret gcp-creds -n intellithing --type='merge' "
            f"-p='{{\"stringData\": {{\"GCP_SERVICE_ACCOUNT_KEY\": \"{key}\", \"ENVIRONMENT\": \"{env}\"}}}}'"
        )
        patch = run(patch_cmd)
        if patch.returncode == 0:
            break
        print(f"❌ Failed to patch secret. Retrying in 10s...\n{patch.stderr.strip()}")
        time.sleep(10)

    # Step 5: Apply Kubernetes manifests
    repo_base = f"{target_location}-docker.pkg.dev/{target_project}/{target_repo}"

    for service in tqdm(images, desc="☸️ Deploying to Kubernetes", unit="service"):
        svc_dir = f"./k8s/{service}"
        deploy_yaml = os.path.join(svc_dir, "deployment.yaml")

        if os.path.exists(deploy_yaml):
            image_path = f"{repo_base}/{service}:latest"
            tqdm.write(f"☸️ Deploying {service} from {deploy_yaml}")
            with open(deploy_yaml, "r") as f:
                raw_yaml = f.read().replace("__IMAGE_TAG__", image_path)

            while True:
                apply_result = run("kubectl apply -f -", input=raw_yaml)
                if apply_result.returncode == 0:
                    break
                tqdm.write(f"❌ Failed to apply deployment.yaml for {service}. Retrying in 10s...\n{apply_result.stderr.strip()}")
                time.sleep(10)

        while True:
            tqdm.write(f"☸️ Applying all manifests in {svc_dir}")
            apply_all = run(f"kubectl apply -f {svc_dir}")
            if apply_all.returncode == 0:
                break
            tqdm.write(f"❌ Failed to apply Kubernetes manifests. Retrying in 10s...\n{apply_all.stderr.strip()}")
            time.sleep(10)

    status.complete("deploy")
    print("✅ Deployment complete.")
