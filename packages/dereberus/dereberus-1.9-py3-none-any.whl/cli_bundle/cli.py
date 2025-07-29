from pathlib import Path
import click
from tabulate import tabulate
from cli_bundle.dereberus import DereberusApi, get_credentials
import json, os

@click.group()
def dereberus_commands():
  pass

def read_public_key(public_key_path):
  full_path = os.path.expanduser(public_key_path)
  with open(full_path, "r") as openfile:
    public_key = openfile.read()
  return public_key

def get_valid_resource(resource=None, service=None, client=None):
  try:
    while True:
      user_api_token = get_credentials("user_api_token")
      if not resource and not service:
        user_input = click.prompt("Enter Resource or Service (format: <service> or <client|service>)")
        if "|" in user_input:
          client, service = user_input.split("|", 1)
        else:
          resource = user_input
      if service and not client:
        client = click.prompt("Enter the Client name for the service")
      if client and not service:
        client = click.prompt("Enter the Service name for the client")
      if service and client:
        data = {"service_name": service, "client_name": client}
        endpoint = "/requests/validate_service"
      else:
        data = {"resource_name": resource}
        endpoint = "/requests/resources"
      valid_response = DereberusApi.post(user_api_token, endpoint, data=data)

      if valid_response.status_code == 200:
        if endpoint == "/requests/validate_service":
          resource = valid_response.json()["resource"]
        return resource
      click.echo("Invalid input. Please try again.")
      resource, service, client = None, None, None
  except Exception as e:
      click.echo(f"Error in job execution: {e}")
      return

@dereberus_commands.command()
def login():
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  user_data_response = DereberusApi.get(auth_token=user_api_token, endpoint="/auth/login")
  if user_data_response.status_code != 200:
    click.echo(user_data_response.json()["message"])
    return
  click.echo(user_data_response.json()["message"])
  user_data = user_data_response.json()["user_data"]
  if user_data_response.json()["user_exist"] == False:
    try:
      public_key_path = click.prompt("Enter the path to your public key file")
      public_key = read_public_key(public_key_path)
    except Exception as e:
      click.echo(f"Error: {e}")
      return
    response = DereberusApi.post(user_api_token, "/auth/user", data={"public_key": public_key, "user_data": user_data})
    if response.status_code != 200:
      click.echo(response.json().get("message"))
      return
    click.echo(response.json().get("message"))
    return
  click.echo("Public key is already set up.")
  click.echo("Do you want to change it? (y/n)")
  choice = input()
  if choice.lower() == "n":
    return
  try:
    public_key_path = click.prompt("Enter the path to your public key file")
    public_key = read_public_key(public_key_path)
  except Exception as e:
    click.echo(f"Error: {e}")
    return
  response = DereberusApi.post(user_api_token, "/auth/user", data={"public_key": public_key})
  if response.status_code != 200:
    click.echo(response.json().get("message"))
    return
  click.echo(response.json().get("message"))
  return

@dereberus_commands.command()
@click.option("--resource", "-r", required=False, help="Resource name to request")
@click.option("--service", "-s", required=False, help="service name to request")
@click.option("--client", "-c", required=False, help="Client name for the service")
@click.option("--reason", "-m", required=False, help="Reason for requesting access")
def access( resource, service, client, reason):
  if service and not client:
    click.echo("Error: If you specify a service, you must also provide a client using -c")
    return
  if not service and client:
    click.echo("Error: If you specify a client, you must also provide a service using -s")
    return
  resource = get_valid_resource(resource, service, client)
  if not resource and not service:
    click.echo("Invalid input. Please enter a valid resource or service|client.")
    return
  if not reason:
    reason = click.prompt("Enter the Reason")
  process_request(resource, reason)

def process_request(resource, reason):
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  resource_response = DereberusApi.post(user_api_token, "/requests/create", data={"resource_name": resource, "reason": reason})
  if resource_response.status_code != 200:
    click.echo(resource_response.json().get("message"))
    return
  click.echo(resource_response.json().get("message"))
  return
  
@dereberus_commands.command()
def resource():
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  list_response = DereberusApi.get(user_api_token, "/resources/list")
  if list_response.status_code != 200:
    click.echo(list_response.json().get("message"))
    return
  resources = list_response.json()
  headers = ["name", "ip"]
  rows = [[req.get(header, "") for header in headers] for req in resources]
  click.echo(tabulate(rows, headers=headers, tablefmt="psql"))

@dereberus_commands.command()
@click.option("--mode","-m", type=click.Choice(["pending", "approved", "all"], case_sensitive=False), default="pending", help="Filter requests by status.")
def list(mode):
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  list_response = DereberusApi.post(user_api_token, "/admin/list", data={"mode": mode})
  if list_response.status_code != 200:
    try:
      click.echo(list_response.json().get("message"))
    except Exception as e:
      click.echo(f"Error in job execution: {e}")
    return
  requests = list_response.json()
  headers = ["id", "mobile", "email", "resource", "ip", "reason", "status", "approver"]
  rows = [[req.get(header, "") for header in headers] for req in requests]
  click.echo(tabulate(rows, headers=headers, tablefmt="psql"))

@dereberus_commands.command()
@click.option("--request-id","-i", prompt="Enter request ID", help="ID of the request to approve")
def approve(request_id):
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  response = DereberusApi.post(user_api_token, "/admin/approve", data={"request_id": request_id})
  if response.status_code != 200:
    try:
      click.echo(response.json().get("message"))
    except Exception as e:
      click.echo(f"Error in job execution: {e}")
    return
  click.echo(response.json().get("message"))

@dereberus_commands.command()
@click.option("--request-id","-i", prompt="Enter request ID", help="ID of the request to reject")
def reject(request_id):
  user_api_token = get_credentials("user_api_token")
  if user_api_token is None:
    click.echo("API token not found")
    return
  response = DereberusApi.post(user_api_token, "/admin/reject", data={"request_id": request_id})
  if response.status_code != 200:
    try:
      click.echo(response.json().get("message"))
    except Exception as e:
      click.echo(f"Error in job execution: {e}")
    return
  click.echo(response.json().get("message"))

dereberus_commands.add_command(login)
dereberus_commands.add_command(access)
dereberus_commands.add_command(list)
dereberus_commands.add_command(approve)
dereberus_commands.add_command(reject)
dereberus_commands.add_command(resource)

if __name__ == "__main__":
    dereberus_commands()
