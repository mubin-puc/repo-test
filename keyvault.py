# %%
# Fetch connection string and container name dynamically (from Key Vault or config.json)
try:
    # Authenticate using Azure CLI credentials
    credential = AzureCliCredential()

    # Get Key Vault name from environment variable
    key_vault_name = os.getenv("KEY_VAULT_NAME")
    if not key_vault_name:
        raise ValueError("Environment variable 'KEY_VAULT_NAME' is not set.")

    # Form the Key Vault URL
    vault_url = f"https://{key_vault_name}.vault.azure.net"

    # Create a SecretClient to access Key Vault
    client = SecretClient(credential=credential, vault_url=vault_url)

    # Retrieve secrets from Key Vault
    storage_account_name = client.get_secret("STORAGE-ACCOUNT-NAME").value

    print("Secrets successfully retrieved from Key Vault.")
except Exception as e:
    print(f"Failed to retrieve secrets from Key Vault: {e}")