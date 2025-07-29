# Dell AI CLI - Getting Started

This guide demonstrates the major functionality of the Dell AI CLI, including:
- Authentication
- Model listing and details
- Model access validation for gated repositories
- Platform listing and details
- Deployment snippet generation for models
- App catalog exploration and deployment

## Prerequisites

- Dell AI CLI installed
- Hugging Face account (for authentication)

## 1. Authentication

### Login
```bash
dell-ai login
# You'll be prompted to enter your Hugging Face token
# or use --token flag to provide it directly
dell-ai login --token <your_token>
```

### Check Authentication Status
```bash
dell-ai whoami
```

### Logout
```bash
dell-ai logout
```

## 2. Models

### List Available Models
```bash
dell-ai models list
```

### Get Model Details
```bash
dell-ai models show <model_id>
# Example: dell-ai models show meta-llama/Llama-4-Maverick-17B-128E-Instruct
```

### Check Access to a Model
```bash
dell-ai models check-access <model_id>
# Example: dell-ai models check-access meta-llama/Llama-4-Maverick-17B-128E-Instruct
```

This command checks if you have access to a specific model repository, which is particularly useful for gated models that require permission. If you don't have access to a gated model, you'll need to request access on the Hugging Face Hub before you can use it for deployment.

### Generate Model Deployment Snippet
```bash
dell-ai models get-snippet --model-id <model_id> --platform-id <platform_id> --engine <engine> --gpus <num_gpus> --replicas <num_replicas>

# Example
dell-ai models get-snippet --model-id meta-llama/Llama-4-Maverick-17B-128E-Instruct --platform-id xe9680-nvidia-h200 --engine docker --gpus 8 --replicas 1

# Example with short flags
dell-ai models get-snippet -m meta-llama/Llama-4-Maverick-17B-128E-Instruct -p xe9680-nvidia-h200 -e kubernetes -g 8 -r 1
```

**Note:** When generating deployment snippets, the CLI automatically checks if you have access to the specified model. If the model is gated and you don't have permission, you'll need to request access on the Hugging Face Hub before proceeding.

## 3. Platforms

### List Available Platforms
```bash
dell-ai platforms list
```

### Get Platform Details
```bash
dell-ai platforms show <platform_id>
# Example: dell-ai platforms show xe9680-nvidia-h200
```

## 4. Model-Platform Compatibility

### Check Platform Support for a Model
```bash
# Using the models show command to view compatibility information
dell-ai models show <model_id> | grep -A 20 "configs_deploy"
# Example: dell-ai models show meta-llama/Llama-4-Maverick-17B-128E-Instruct | grep -A 20 "configs_deploy"

# For a more focused view, use jq if available
dell-ai models show <model_id> --json | jq '.configs_deploy'
```

The output will show which platforms support the model and the available configurations for each platform, including:
- Required GPU count
- Maximum input tokens
- Maximum total tokens
- Maximum batch prefill tokens

## 5. Application Catalog

The Dell AI CLI provides access to the Application Catalog, which contains ready-to-deploy applications optimized for AI workloads.

### List Available Applications
```bash
dell-ai apps list
```

### Get Application Details
```bash
dell-ai apps show <app_id>
# Example: dell-ai apps show openwebui
```

This displays comprehensive information about the application, including:
- Basic metadata (name, license, etc)
- Description and features
- Recommended models
- Components and their configuration options
- Available configuration parameters

### Generate Application Deployment Snippet
```bash
dell-ai apps get-snippet <app_id> --config '<config_json>'
# Example: dell-ai apps get-snippet openwebui --config '{"config":[{"helmPath":"main.config.storageClassName","type":"string","value":"gp2"}]}'
```

The `--config` parameter accepts a JSON string containing configuration parameters for the application. The JSON should have a `config` array containing objects with the following properties:
- `helmPath`: The Helm path for the parameter (found in the app details)
- `type`: The parameter type (string, boolean, number, or json)
- `value`: The desired value for the parameter

Example configuration for OpenWebUI with custom storage class and enabled OpenAI API:
```json
{
  "config": [
    {
      "helmPath": "main.config.storageClassName",
      "type": "string",
      "value": "gp2"
    },
    {
      "helmPath": "main.config.enableOpenAI",
      "type": "boolean",
      "value": true
    }
  ]
}
```
The command returns a Helm command that can be used to deploy the application with the specified configuration.

## Common Options

### Show Version
```bash
dell-ai --version
# or
dell-ai -v
```
