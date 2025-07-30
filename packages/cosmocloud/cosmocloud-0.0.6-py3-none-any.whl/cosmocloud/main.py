import json
import os
import sys

import click
import requests

# Constants
API_BASE_URL = "https://groot-production.cosmocloud.io"
TOKEN_FILE = os.path.expanduser("~/.cosmocloud_token")


# Save tokens to a file
def save_tokens(tokens):
    """
    Save tokens to a file.
    """

    with open(TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(tokens, f)


# Load tokens from a file
def load_tokens():
    """
    Load tokens from a file.
    """

    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# Call API with token
def call_api(
    endpoint: str,
    method: str,
    data: dict,
    server_url: str,
    public: bool = False,
):
    """
    Call Cosmocloud API with token.
    """

    headers = {}
    if not public:
        tokens = load_tokens()
        if not tokens:
            click.echo("Please log in first.")
            sys.exit(1)
        headers = {"Authorization": f"Bearer {tokens['IdToken']}"}

    response = requests.request(
        method, f"{server_url}{endpoint}", headers=headers, json=data, timeout=5
    )

    if response.status_code == 401:
        click.echo(
            "Session expired or invalid credentials. Please try logging in again."
        )
        sys.exit(1)

    if int(response.status_code / 100) != 2:
        click.echo("Couldn't connect to Cosmocloud Deploy. Please try again later.")
        sys.exit(1)

    return response.json()


# CLI commands
@click.group()
def cli():
    """
    Cosmocloud CLI
    """


@click.command()
@click.option("--username", prompt=True, help="Your Cosmocloud username")
@click.option(
    "--password", prompt=True, hide_input=True, help="Your Cosmocloud password"
)
@click.option(
    "-s",
    "--server-url",
    prompt=True,
    help="Your Cosmocloud server URL",
    prompt_required=False,
    default=API_BASE_URL,
)
def login(username, password, server_url):
    """
    Log in with your user.

    Example:
    $ cosmocloud login --username myuser --password mypassword
    """

    tokens = call_api(
        server_url=server_url,
        endpoint="/auth",
        method="POST",
        data={"username": username, "password": password},
        public=True,
    )

    save_tokens(tokens)
    click.echo("Login successful!")


def get_entity(entity_list, entity_name):
    """
    Get entity ID from entity list.
    """

    org_id = ""
    for org in entity_list:
        if org["name"].lower() == entity_name.lower():
            org_id = org["id"]
            break

    if not org_id:
        click.echo(f"{entity_name} not found.")
        sys.exit(1)

    return org_id


@click.command()
@click.option(
    "-s",
    "--server-url",
    prompt=True,
    help="Your Cosmocloud server URL",
    prompt_required=False,
    default=API_BASE_URL,
)
def list_organisations(server_url):
    """
    List all organisations.
    """

    response = call_api("/orgs?limit=1000", "GET", data={}, server_url=server_url)

    for org in response["data"]:
        click.echo(f"{org['name']}: {org['status']}")


@click.command()
@click.option("-o", "--organisation", prompt=True, help="Your organisation name")
@click.option(
    "-s",
    "--server-url",
    prompt=True,
    help="Your Cosmocloud server URL",
    prompt_required=False,
    default=API_BASE_URL,
)
def list_app_services(organisation, server_url):
    """
    List all app services.
    """

    response = call_api("/orgs?limit=1000", "GET", data={}, server_url=server_url)
    org_id = get_entity(response["data"], organisation)

    response = call_api(
        f"/orgs/{org_id}/app-services", "GET", data={}, server_url=server_url
    )
    for app_service in response["data"]:
        click.echo(f"{app_service['name']}: {app_service['status']}")


@click.command()
@click.option("-o", "--organisation", prompt=True, help="Your organisation name")
@click.option("-a", "--app-service", prompt=True, help="Your app service name")
@click.option(
    "-s",
    "--server-url",
    prompt=True,
    help="Your Cosmocloud server URL",
    prompt_required=False,
    default=API_BASE_URL,
)
def list_releases(organisation, app_service, server_url):
    """
    List all releases.
    """

    response = call_api("/orgs?limit=1000", "GET", data={}, server_url=server_url)
    org_id = get_entity(response["data"], organisation)

    response = call_api(
        f"/orgs/{org_id}/app-services", "GET", data={}, server_url=server_url
    )
    app_service_id = get_entity(response["data"], app_service)

    response = call_api(
        f"/orgs/{org_id}/app-services/{app_service_id}/releases?limit=1000",
        "GET",
        data={},
        server_url=server_url,
    )

    for release_obj in response["data"]:
        deployed_on = ", ".join(env["name"] for env in release_obj["environments"])
        if not deployed_on:
            deployed_on = "Not deployed"
        click.echo(f"{release_obj['version']}: {deployed_on}")


@click.command()
@click.option("-o", "--organisation", prompt=True, help="Your organisation name")
@click.option(
    "-s",
    "--server-url",
    prompt=True,
    help="Your Cosmocloud server URL",
    prompt_required=False,
    default=API_BASE_URL,
)
@click.option(
    "-a",
    "--app-service",
    prompt=True,
    help="Your app service to release new version for",
)
@click.option("-v", "--version", prompt=True, help="Version to release")
@click.option("-e", "--environment", prompt=True, help="Your environment name")
def release(organisation, app_service, version, environment, server_url):
    """
    Release a new version for your app service.
    """

    response = call_api("/orgs?limit=1000", "GET", data={}, server_url=server_url)
    org_id = get_entity(response["data"], organisation)

    response = call_api(
        f"/orgs/{org_id}/app-services", "GET", data={}, server_url=server_url
    )
    app_service_id = get_entity(response["data"], app_service)

    response = call_api(
        f"/orgs/{org_id}/envs?limit=1000", "GET", data={}, server_url=server_url
    )
    env_id = get_entity(response["data"], environment)

    response = call_api(
        f"/orgs/{org_id}/app-services/{app_service_id}/releases",
        "POST",
        data={"environment_id": env_id, "version": version},
        server_url=server_url,
    )
    click.echo(response["message"])


@click.command()
@click.option("-o", "--organisation", prompt=True, help="Your organisation name")
@click.option(
    "-a",
    "--app-service",
    prompt=True,
    help="Your app service to release new version for",
)
@click.option("-v", "--version", prompt=True, help="Version to release")
@click.option("-e", "--environment", prompt=True, help="Your environment name")
@click.option(
    "-s",
    "--server-url",
    prompt=True,
    help="Your Cosmocloud server URL",
    prompt_required=False,
    default=API_BASE_URL,
)
def promote(organisation, app_service, version, environment, server_url):
    """
    Promote an existing version for your app service.
    """

    response = call_api("/orgs?limit=1000", "GET", data={}, server_url=server_url)
    org_id = get_entity(response["data"], organisation)

    response = call_api(
        f"/orgs/{org_id}/app-services", "GET", data={}, server_url=server_url
    )
    app_service_id = get_entity(response["data"], app_service)

    response = call_api(
        f"/orgs/{org_id}/envs?limit=1000", "GET", data={}, server_url=server_url
    )
    env_id = get_entity(response["data"], environment)

    response = call_api(
        f"/orgs/{org_id}/app-services/{app_service_id}/releases/promote",
        "POST",
        data={"environment_id": env_id, "version": version},
        server_url=server_url,
    )
    click.echo(response["message"])


# Add commands to CLI
cli.add_command(login)
cli.add_command(list_organisations)
cli.add_command(list_app_services)
cli.add_command(list_releases)
cli.add_command(release)
cli.add_command(promote)
