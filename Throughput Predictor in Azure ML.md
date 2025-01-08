Throughput Predictor in Azure ML

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
    name="ML_Workspace2",
    location="eastus",
    resource_group="ML_ResourceGroup2",
    description="Workspace created using SDK v2",
)

ml_client.workspaces.begin_create_or_update(workspace)
print("Workspace created:", workspace.name)
```

#### Step 4: Save Configuration
Save the configuration for reuse:

```python
with open("config.json", "w") as f:
    f.write(workspace.serialize())
```
## Learnings

- Azure ML SDK v2 is the latest and most feature-rich SDK for managing ML resources in Azure.
- MLClient provides a clean, object-oriented way to interact with Azure ML workspaces.

## References
- Azure Machine Learning Python SDK v2 Documentation
