import base64
import os
import subprocess
import tempfile
from typing import List

import typer
from intctl.config import load_config, save_config, apply_env
from .setup_resources.service_account import create_service_account
from .setup_resources.postgres import create_postgres
from .status import StatusManager
from .setup_resources.kubernetes import create_kubernetes_cluster
from .setup_resources.registry import setup_artifact_registry
from .setup_resources.bucket import setup_gcs_bucket
from .setup_resources.setup_cloud_endpoints import setup_cloud_endpoints
from .setup_resources.deploy import transfer_and_deploy
from .setup_resources.finalise_database import finalise_database
import re
import uuid
import json




app = typer.Typer(help="intctl: CLI for provisioning cloud resources.")


def run(cmd: str) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def slugify_project_name(name: str) -> str:
    base = re.sub(r"[^a-z0-9-]", "-", name.lower())
    base = re.sub(r"-+", "-", base).strip("-")
    suffix = uuid.uuid4().hex[:6]
    return f"{base[:20]}-{suffix}"


def choose_billing_account() -> str:
    result = run("gcloud beta billing accounts list --format=json")
    if result.returncode != 0:
        print("❌ Failed to list billing accounts.")
        print(result.stderr)
        raise typer.Exit(1)

    accounts = json.loads(result.stdout)
    open_accounts = [a for a in accounts if a.get("open")]

    if not open_accounts:
        print("❌ No open billing accounts found. Please open one in the GCP console.")
        raise typer.Exit(1)

    print("\nAvailable billing accounts:")
    for i, acc in enumerate(open_accounts, 1):
        acc_id = acc["name"].split("/")[-1]
        print(f"  {i}. {acc['displayName']} (#{acc_id})")

    while True:
        choice = input("Pick a billing account number: ").strip()
        try:
            idx = int(choice)
            if 1 <= idx <= len(open_accounts):
                return open_accounts[idx - 1]["name"].split("/")[-1]
            else:
                print("Invalid number.")
        except ValueError:
            print("Enter a number.")


def choose_cloud(cfg: dict) -> None:
    current = cfg.get("cloud", "gcp")
    val = input(f"Choose cloud [gcp/azure/aws] ({current}): ") or current
    cfg["cloud"] = val


def configure_command() -> None:
    cfg = load_config()
    choose_cloud(cfg)
    cfg["user_uuid"] = input("user_uuid: ") or cfg.get("user_uuid")
    cfg["organization_uuid"] = input("organization_uuid: ") or cfg.get("organization_uuid")
    cfg["workspace_uuid"] = input("workspace_uuid: ") or cfg.get("workspace_uuid")
    cfg["region"] = input("region: ") or cfg.get("region", "us-central1")

    if cfg["cloud"] == "gcp":
        res = run('gcloud projects list --format="value(projectId,name,projectNumber)"')
        if res.returncode != 0:
            print("❌ Failed to list GCP projects.")
            print(res.stderr)
            raise typer.Exit(1)

        project_lines = [line for line in res.stdout.strip().splitlines()]
        projects = []

        print("\nAvailable GCP projects:")
        for idx, line in enumerate(project_lines, 1):
            parts = line.split()
            project_id = parts[0] if len(parts) > 0 else "(unknown)"
            name = parts[1] if len(parts) > 1 else ""
            project_number = parts[2] if len(parts) > 2 else ""
            projects.append(project_id)
            print(f"  {idx}. {project_id} - {name or '(no name)'} (#{project_number})")

        while True:
            choice = input("\nPick a project number or 'n' to create a new project: ").strip().lower()
            if choice == "n":
                new_name = input("Enter a name for the new project: ").strip()
                project_id = slugify_project_name(new_name)
                billing_account = choose_billing_account()

                print(f"🚧 Creating project '{new_name}' with ID '{project_id}'...")
                result = run(f"gcloud projects create {project_id} --name='{new_name}'")
                if result.returncode != 0:
                    print("❌ Failed to create project.")
                    print(result.stderr)
                    continue

                print(f"✅ Project '{new_name}' created with ID: {project_id}")

                billing_result = run(
                    f"gcloud beta billing projects link {project_id} --billing-account {billing_account}"
                )
                if billing_result.returncode != 0:
                    print("❌ Failed to link billing account.")
                    print(billing_result.stderr)
                    continue

                print(f"🔗 Linked billing account {billing_account} to project {project_id}")
                cfg["project_id"] = project_id
                break
            else:
                try:
                    idx = int(choice)
                    if 1 <= idx <= len(projects):
                        cfg["project_id"] = projects[idx - 1]
                        print(f"✅ Selected project: {cfg['project_id']}")
                        break
                    else:
                        print("Invalid project number.")
                except ValueError:
                    print("Invalid input.")

    save_config(cfg)
    apply_env(cfg)
    print("Configuration saved.")




def setup_command() -> None:
    cfg = load_config()
    apply_env(cfg)
    status = StatusManager()
    create_service_account(cfg, status)
    create_postgres(cfg, status)
    create_kubernetes_cluster(cfg, status)
    setup_artifact_registry(cfg, status)
    setup_gcs_bucket(cfg, status)
    setup_cloud_endpoints(cfg, status)
    transfer_and_deploy(cfg, status)
    finalise_database(cfg, status)
    status.summary()


def cloud_command(provider: str) -> None:
    cfg = load_config()
    cfg["cloud"] = provider
    save_config(cfg)
    print(f"Cloud set to {provider}")


def update_command() -> None:
    print("Checking for updates (not implemented)")


@app.command()
def configure():
    """Run configuration setup."""
    configure_command()


@app.command()
def setup():
    """Create service account and resources."""
    setup_command()


@app.command()
def update():
    """Check for updates (stub)."""
    update_command()


@app.command()
def cloud(provider: str = typer.Argument(..., help="Cloud provider: gcp, aws, or azure")):
    """Set cloud provider."""
    if provider not in ["gcp", "aws", "azure"]:
        typer.echo("Provider must be one of: gcp, aws, azure")
        raise typer.Exit(code=1)
    cloud_command(provider)    


if __name__ == "__main__":
    app()
