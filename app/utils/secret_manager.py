# Author: Mangesh Wagh
# Email: mangeshwagh2722@gmail.com


"""
Google Cloud Secret Manager integration.
Retrieves sensitive credentials from GCP Secret Manager instead of
environment variables, providing audit trails and automatic rotation.
"""

import logging
from typing import Optional
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=20)
def get_secret(secret_id: str, project_id: str, version: str = "latest") -> Optional[str]:
    """
    Retrieve a secret value from Google Cloud Secret Manager.
    Results are cached in-process to minimise API calls.

    Args:
        secret_id:  The secret name in Secret Manager
        project_id: Your GCP project ID
        version:    Secret version (default: "latest")

    Returns:
        Secret value as string, or None if retrieval fails
    """
    try:
        from google.cloud import secretmanager
        client = secretmanager.SecretManagerServiceClient()
        name = f"projects/{project_id}/secrets/{secret_id}/versions/{version}"
        response = client.access_secret_version(request={"name": name})
        secret_value = response.payload.data.decode("UTF-8")
        logger.info(f"Secret '{secret_id}' retrieved from Secret Manager")
        return secret_value
    except ImportError:
        logger.debug("google-cloud-secret-manager not installed — using env vars")
        return None
    except Exception as e:
        logger.warning(f"Secret Manager unavailable for '{secret_id}': {e}")
        return None


def get_firebase_credentials(project_id: str = "771554077981") -> Optional[dict]:
    """
    Attempt to load Firebase service account from Secret Manager.
    Falls back to FIREBASE_SERVICE_ACCOUNT_PATH env var if unavailable.
    """
    import json
    secret = get_secret("firebase-service-account", project_id)
    if secret:
        try:
            return json.loads(secret)
        except json.JSONDecodeError:
            logger.error("Firebase credentials from Secret Manager are malformed JSON")
    return None


def load_secrets_to_env(project_id: str = "771554077981") -> bool:
    """
    Fetch 'stadium-code-secrets' from GCP Secret Manager and load into os.environ.
    Handles both JSON and raw .env file formats.
    """
    import os
    import json
    
    secret_data = get_secret("stadium-code-secrets", project_id)
    if not secret_data:
        return False
        
    # Attempt 1: Try parsing as JSON
    try:
        secrets = json.loads(secret_data)
        if isinstance(secrets, dict):
            for key, value in secrets.items():
                if value:
                    os.environ[key] = str(value)
            logger.info("✅ Successfully loaded JSON secrets from GCP Secret Manager")
            return True
    except (json.JSONDecodeError, TypeError):
        pass

    # Attempt 2: Try parsing as .env format (KEY=VALUE)
    try:
        lines = secret_data.splitlines()
        loaded_count = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                # Remove quotes if present
                value = value.strip().strip("'").strip('"')
                os.environ[key.strip()] = value
                loaded_count += 1
        
        if loaded_count > 0:
            logger.info(f"✅ Successfully loaded {loaded_count} secrets from .env format in Secret Manager")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to parse .env formatted secrets: {e}")
    
    return False
