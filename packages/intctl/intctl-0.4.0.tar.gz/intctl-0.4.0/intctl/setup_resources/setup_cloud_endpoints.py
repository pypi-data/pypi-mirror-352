import os
import subprocess
import time
from intctl.status import StatusManager


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def setup_cloud_endpoints(cfg: dict, status: StatusManager) -> None:
    status.start("cloud_endpoints")

    project = cfg["project_id"]
    workspace = cfg["workspace_uuid"]
    service_name = f"intellithing-{workspace}.endpoints.{project}.cloud.goog"
    spec_path = "k8s/openapi-spec.yaml"

    if not os.path.exists(spec_path):
        print(f"❌ OpenAPI spec not found at {spec_path}. Please create one.")
        status.fail("cloud_endpoints")
        return

    print("🛠 Enabling required APIs...")
    run(f"gcloud services enable endpoints.googleapis.com servicemanagement.googleapis.com --project={project}")

    # Deploy OpenAPI spec to Cloud Endpoints
    print(f"🚀 Deploying OpenAPI spec to Cloud Endpoints service '{service_name}'...")
    result = run(
        f"gcloud endpoints services deploy {spec_path} --project={project}"
    )
    if result.returncode != 0:
        print("❌ Failed to deploy to Cloud Endpoints:")
        print(result.stderr.strip())
        status.fail("cloud_endpoints")
        return

    # Confirm the service is available
    print(f"⏳ Verifying that the service '{service_name}' is active...")
    while True:
        result = run(f"gcloud endpoints services describe {service_name} --project={project}")
        if result.returncode == 0:
            print(f"✅ Cloud Endpoints service '{service_name}' is deployed and active.")
            break
        print("⏳ Waiting for Cloud Endpoints service to become active...")
        time.sleep(10)

    status.complete("cloud_endpoints")

# base URL: intellithing-{workspace}.endpoints.{project}.cloud.goog