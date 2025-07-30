import os
import subprocess
import tempfile
import base64
import time
import typer
from typing import List
from intctl.status import StatusManager


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def create_service_account(cfg: dict, status: StatusManager):
    status.start("service_account")
    project = cfg["project_id"]
    sa_name = "intellithing"
    sa_email = f"{sa_name}@{project}.iam.gserviceaccount.com"

    # Step 1: Ensure the service account exists
    if run(f"gcloud iam service-accounts describe {sa_email} --project {project}").returncode == 0:
        print("✅ Service account exists.")
    else:
        print("🔧 Creating service account...")

        result = run(f"gcloud iam service-accounts create {sa_name} --project {project}")
        if result.returncode != 0:
            print("❌ Failed to create service account.")
            print(result.stderr.strip())
            print(f"""
🔐 The currently authenticated account does not have permission to create a service account.

Please do the following manually:
  1. Authenticate with a user who has sufficient IAM permissions:
     gcloud auth login

  2. Or create the service account manually:
     gcloud iam service-accounts create {sa_name} --project {project}

⏳ Waiting for service account '{sa_email}' to be created...
""")

            while True:
                time.sleep(10)
                check = run(f"gcloud iam service-accounts describe {sa_email} --project {project}")
                if check.returncode == 0:
                    print("✅ Service account created.")
                    break
                else:
                    print("⏳ Still waiting for service account...")

    # Step 2: Assign roles
    roles: List[str] = [
        "roles/apigateway.admin", "roles/artifactregistry.admin", "roles/cloudbuild.builds.editor",
        "roles/cloudfunctions.admin", "roles/cloudfunctions.developer", "roles/cloudsql.admin",
        "roles/composer.admin", "roles/compute.admin", "roles/compute.viewer", "roles/container.admin",
        "roles/logging.admin", "roles/monitoring.metricWriter", "roles/monitoring.viewer",
        "roles/secretmanager.admin", "roles/iam.serviceAccountUser", "roles/serviceusage.serviceUsageAdmin",
        "roles/storage.admin", "roles/storage.objectAdmin", "roles/storage.objectViewer",
        "roles/storage.bucketViewer", "roles/aiplatform.admin"
    ]

    failed_roles = []

    print("\n🔐 Assigning IAM roles to the service account...")

    for role in roles:
        result = run(
            f"gcloud projects add-iam-policy-binding {project} "
            f"--member=serviceAccount:{sa_email} --role={role}"
        )
        if result.returncode != 0:
            failed_roles.append(role)

    if failed_roles:
        print("\n⚠️ Some roles could not be assigned automatically.")
        for role in failed_roles:
            print(f"  - {role}")
        print(f"""
Please assign these roles manually to the service account:
  {sa_email}

You can do this via the IAM console or CLI.

⏳ Waiting until all roles are assigned...
""")

        while True:
            time.sleep(10)
            still_missing = []
            for role in failed_roles:
                check = run(
                    f"gcloud projects get-iam-policy {project} "
                    f"--flatten='bindings[].members' "
                    f"--filter='bindings.role={role} AND bindings.members=serviceAccount:{sa_email}' "
                    f"--format='value(bindings.role)'"
                )
                if role not in check.stdout.strip().splitlines():
                    still_missing.append(role)

            if not still_missing:
                print("✅ All roles successfully assigned.")
                break
            else:
                print(f"⏳ Still waiting for roles: {', '.join(still_missing)}")

    # Step 3: Create service account key
    print("\n🔑 Generating service account key...")
    fd, key_file = tempfile.mkstemp(suffix=".json")
    os.close(fd)

    while True:
        result = run(
            f"gcloud iam service-accounts keys create {key_file} "
            f"--iam-account {sa_email} --project {project}"
        )
        if result.returncode == 0:
            print("✅ Service account key created.")
            break
        else:
            print("❌ Failed to create key. Make sure you have 'iam.serviceAccountKeys.create' permission.")
            print(result.stderr.strip())
            print("⏳ Retrying in 10 seconds...")
            time.sleep(10)

    # Step 4: Upload to Secret Manager
    secret_name = f"{cfg['organization_uuid']}-{cfg['workspace_uuid']}-sa-key"

    describe_result = run(f"gcloud secrets describe {secret_name} --project {project}")
    if describe_result.returncode != 0:
        print(f"🔐 Creating secret {secret_name}...")
        run(f"gcloud secrets create {secret_name} --replication-policy=automatic --project {project}")
    else:
        print(f"✅ Secret {secret_name} already exists.")

    print("⬆️ Uploading service account key to Secret Manager...")
    run(f"gcloud secrets versions add {secret_name} --data-file={key_file} --project {project}")

    # Step 5: Encode key and store in env
    with open(key_file, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    os.environ["GCP_SERVICE_ACCOUNT_KEY"] = encoded

    print("✅ Service account setup complete.")
    status.complete("service_account")
