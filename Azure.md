# Setting Up Azure ML Workspace with SDK v2

## Objective
Learn how to create and connect to an Azure ML workspace using Python SDK v2.

## Steps

### Step 1: Install Azure Python SDK v2
Install the required packages:
```bash
pip install azure-ai-ml azure-identity
```
### Step 2: Authenticate & connect to Azure ML workspace

Authenticate using DefaultAzureCredential

```python
# Set up credentials and connect to Azure ML workspace
credential = DefaultAzureCredential()
ml_client = MLClient(credential, subscription_id="hiddenforsafety", resource_group_name="ML_ResourceGroup", workspace_name="ML_Workspace")
print("Connected to workspace:", ml_client.workspace_name)
```

### Step 3: Create a Workspace 
If a workspace doesn’t exist, create it:
```python
from azure.ai.ml.entities import Workspace

workspace = Workspace(
    name="MyNewWorkspace",
    location="eastus",
    resource_group="MyResourceGroup",
    description="Workspace created using SDK v2",
)

ml_client.workspaces.begin_create_or_update(workspace)
print("Workspace created:", workspace.name)
```
