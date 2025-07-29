<h1 align="center">MindBridge API Python Client</h1>
<p align="center">
    <img alt="Logo of MindBridge" src="https://www.mindbridge.ai/wp-content/uploads/2021/07/MindBridge_Logo_Primary_RGB.png" />
</p>

Interact with the MindBridge API using this Python SDK. Please see [The MindBridge API](https://www.mindbridge.ai/support/api/) for more information about the MindBridge API. You can also [Access MindBridge Customer Support](https://support.mindbridge.ai/hc/en-us/articles/360054147834-Access-MindBridge-Customer-Support) or [Contact us](https://www.mindbridge.ai/contact/).

## Installation
mindbridge-api-python-client can be installed with [pip](https://pip.pypa.io):

```sh
python -m pip install mindbridge-api-python-client
```

## Usage
Replace `subdomain.mindbridge.ai` with your MindBridge tenant URL.
```py
import getpass
import mindbridgeapi as mbapi

url = "subdomain.mindbridge.ai"
token = getpass.getpass(f"Token for {url}: ")

server = mbapi.Server(url=url, token=token)

organization = mbapi.OrganizationItem(name="My Organization name")
organization = server.organizations.create(organization)

# Create engagements, analyses and run them, etc.
```
