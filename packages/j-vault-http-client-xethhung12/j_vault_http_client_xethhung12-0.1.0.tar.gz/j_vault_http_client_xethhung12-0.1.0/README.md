# JVaultHttpClient

A python version of connector to JVault Http Server for retrieving application configuration during app initialization stage.

# Installation
```bash
pip install -U j_vault_http_client_xethhung12
```

# Usage

```python
from j_vault_http_client_xethhung12 import jvault_http_client

if __name__ == '__main__':
    jvault_http_client.load_to_env()
```