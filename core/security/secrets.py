"""
Secret Management - Zero-Knowledge Architecture
Fetches secrets from Google Secret Manager (Production) or .env (Local Dev)
"""

import os
import logging
from typing import Optional
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file for local development
load_dotenv()


class SecretManager:
    """
    Secret Manager for secure API key and credential handling.
    
    Priority:
    1. Google Secret Manager (Production)
    2. Environment variables / .env file (Local Dev)
    
    CRITICAL: Never prints secrets to console/logs.
    """
    
    def __init__(self):
        self._gcp_secret_manager_available = False
        self._initialize_gcp()
    
    def _initialize_gcp(self) -> None:
        """Initialize Google Cloud Secret Manager client if available"""
        try:
            from google.cloud import secretmanager
            self._secret_client = secretmanager.SecretManagerServiceClient()
            self._gcp_secret_manager_available = True
            logger.info("Google Secret Manager initialized (Production mode)")
        except ImportError:
            logger.debug("google-cloud-secret-manager not installed, using .env fallback")
        except Exception as e:
            logger.warning(f"Google Secret Manager unavailable: {e}, falling back to .env")
    
    def get_secret(self, key: str, project_id: Optional[str] = None) -> Optional[str]:
        """
        Get secret value from Google Secret Manager or environment variable.
        
        Args:
            key: Secret key name
            project_id: GCP Project ID (required for Secret Manager)
            
        Returns:
            Secret value or None if not found
            
        Raises:
            ValueError: If secret is required but not found
        """
        # Try Google Secret Manager first (Production)
        if self._gcp_secret_manager_available and project_id:
            try:
                secret_name = f"projects/{project_id}/secrets/{key}/versions/latest"
                response = self._secret_client.access_secret_version(request={"name": secret_name})
                secret_value = response.payload.data.decode("UTF-8")
                logger.debug(f"Secret '{key}' retrieved from Google Secret Manager")
                return secret_value
            except Exception as e:
                logger.warning(f"Failed to fetch '{key}' from Secret Manager: {e}")
                # Fall through to environment variable
        
        # Fallback to environment variable / .env file (Local Dev)
        secret_value = os.getenv(key)
        if secret_value:
            logger.debug(f"Secret '{key}' retrieved from environment variable")
            return secret_value
        
        logger.warning(f"Secret '{key}' not found in Secret Manager or environment")
        return None
    
    def get_secret_or_raise(self, key: str, project_id: Optional[str] = None) -> str:
        """
        Get secret value, raising ValueError if not found.
        
        Args:
            key: Secret key name
            project_id: GCP Project ID
            
        Returns:
            Secret value
            
        Raises:
            ValueError: If secret is not found
        """
        secret_value = self.get_secret(key, project_id)
        if secret_value is None:
            raise ValueError(
                f"Required secret '{key}' not found. "
                f"Set {key} in Google Secret Manager or .env file"
            )
        return secret_value


# Global instance
_secret_manager_instance: Optional[SecretManager] = None


def get_secret_manager() -> SecretManager:
    """Get global SecretManager instance (singleton)"""
    global _secret_manager_instance
    if _secret_manager_instance is None:
        _secret_manager_instance = SecretManager()
    return _secret_manager_instance

