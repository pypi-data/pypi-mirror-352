## AuvikNetworksConnection Class 
The AuvikNetworksConnection class provides an interface to interact with the Auvik Networks API, allowing users to authenticate and retrieve data related to tenants and devices. The class includes error handling and retry logic for API requests to ensure reliability. This README provides an overview of the class's functionality, methods, and usage.

# Class Summary
AuvikNetworksConnection
Purpose: To authenticate and interact with the Auvik Networks API.

# Command-list
get_tenants: Retrieves tenant information.
get_tenant_details: Retrieves detailed information for a specific tenant.
get_device_info: Retrieves device information for a specific tenant.
get_auvik_devices_info: Retrieves detailed device information, with optional additional details.

# Methods:
__init__(username: str, password: str): Initializes the connection and authenticates the user.
get_tenants(json_output: bool = False): Retrieves tenant information.
get_tenant_details(domain_prefix: str, json_output: bool = False): Retrieves detailed information for a specific tenant.
get_auvik_devices_info(tenant_id: str = None, include_detail: bool = False, json_output: bool = False): Retrieves detailed device information with optional detail fields.

Ensure you have the necessary Python packages installed:
import requests
import json
import pandas as pd
import time

# Initialization
To use the AuvikNetworksConnection class, you need to provide your Auvik username and password (API token):
from auvik_networks_connection import AuvikNetworksConnection

username = "your_username"
password = "your_password"

auvik_conn = AuvikNetworksConnection(username, password)

# Retrieve Tenants
You can retrieve tenant information using the get_tenants method:
tenants = auvik_conn.get_tenants()
print(tenants)
To retrieve the output in JSON format, set json_output to True:
tenants_json = auvik_conn.get_tenants(json_output=True)
print(tenants_json)

# Retrieve Tenant Details
To get detailed information for a specific tenant:

domain_prefix = "tenant_prefix"
tenant_details = auvik_conn.get_tenant_details(domain_prefix)
print(tenant_details)

# Retrieve Detailed Device Information
To get detailed device information, including specific fields:

detailed_device_info = auvik_conn.get_auvik_devices_info(tenant_id, include_detail=True)
print(detailed_device_info)
Error Handling
The APIErrorHandler class is used internally to handle API errors. If the API returns an error status code, an exception will be raised with a relevant message.

Retry Logic
The get method includes retry logic with three attempts in case of a request failure. The system waits 10 seconds before retrying.

# Notes
Ensure that your credentials are stored securely and not hard-coded in your scripts.
The get_access_token method handles the base64 encoding of credentials and authenticates with the Auvik API.
Use the json_output parameter to retrieve data in JSON format if required.