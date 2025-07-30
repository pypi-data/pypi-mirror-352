import os
import subprocess
import secrets
import string
import time
from intctl.status import StatusManager


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def create_postgres(cfg: dict, status: StatusManager):
    status.start("postgres")
    project = cfg["project_id"]
    region = cfg["region"]
    org = cfg["organization_uuid"]
    workspace = cfg["workspace_uuid"]
    instance = f"intellithing-pg-{workspace}".lower()
    instance = instance[:80] if instance[0].isalpha() else "pg-" + instance[:77]

    # Step 1: Check if instance exists
    if run(f"gcloud sql instances describe {instance} --project={project}").returncode == 0:
        print(f"✅ Cloud SQL instance '{instance}' already exists.")
        status.complete("postgres")
        return

    # Step 2: Create or retrieve DB password from Secret Manager
    print("🔍 Checking for existing DB password...")
    pw_secret = f"{org}-{workspace}-pg-password"
    res = run(f"gcloud secrets versions access latest --secret={pw_secret} --project={project}")
    if res.returncode == 0:
        password = res.stdout.strip()
        print("✅ Reusing existing password from Secret Manager.")
    else:
        print("🔐 Generating new password...")
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(20))
        result = run(
            f"echo -n '{password}' | gcloud secrets create {pw_secret} "
            f"--data-file=- --replication-policy=automatic --project={project}"
        )
        if result.returncode != 0:
            print("❌ Failed to create password secret.")
            print(result.stderr.strip())
            print("Please create the secret manually and re-run the command.")
            return

    # Step 3: Ensure the username secret exists
    user_secret = f"{org}-{workspace}-pg-username"
    if run(f"gcloud secrets describe {user_secret} --project={project}").returncode != 0:
        result = run(
            f"echo -n 'postgres' | gcloud secrets create {user_secret} "
            f"--data-file=- --replication-policy=automatic --project={project}"
        )
        if result.returncode != 0:
            print("❌ Failed to create username secret.")
            print(result.stderr.strip())
            print("Please create the secret manually and re-run the command.")
            return

    # Step 4: Attempt to create the Cloud SQL instance
    print("🚀 Creating Cloud SQL instance...")
    result = run(
        f"gcloud sql instances create {instance} "
        f"--database-version=POSTGRES_15 --tier=db-f1-micro --region={region} "
        f"--root-password={password} --storage-size=10 --storage-type=SSD "
        f"--availability-type=ZONAL --no-backup --authorized-networks=0.0.0.0/0 "
        f"--project={project} --quiet"
    )

    if result.returncode != 0:
        print("❌ Failed to create Cloud SQL instance.")
        print(result.stderr.strip())
        print(f"""
🔧 You may not have sufficient permissions to create a Cloud SQL instance, or the instance name may conflict.

Please create the instance manually using:

  gcloud sql instances create {instance} \\
    --database-version=POSTGRES_15 --tier=db-f1-micro --region={region} \\
    --root-password={password} --storage-size=10 --storage-type=SSD \\
    --availability-type=ZONAL --no-backup --authorized-networks=0.0.0.0/0 \\
    --project={project}

⏳ Waiting for instance '{instance}' to become available...
""")

        # Poll for manual creation
        while True:
            time.sleep(10)
            check = run(f"gcloud sql instances describe {instance} --project={project}")
            if check.returncode == 0:
                print(f"✅ Cloud SQL PostgreSQL instance '{instance}' is now available.")
                break
            else:
                print("⏳ Still waiting for Cloud SQL instance...")

    else:
        print(f"🎉 Cloud SQL PostgreSQL instance '{instance}' created.")

    status.complete("postgres")
