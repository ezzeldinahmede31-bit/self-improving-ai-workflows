#!/usr/bin/env python3
"""Google Calendar OAuth Auto-Reconnect — permanent fix for expired tokens.

Monitors n8n Google Calendar node for OAuth expiry, automatically refreshes
tokens using stored refresh_token, and re-activates affected workflows.

Run as: cron every 5 min, or as systemd service.
"""
import json
import os
import subprocess
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Optional


class GoogleCalendarOAuthManager:
    """Manages Google Calendar OAuth tokens for n8n."""
    
    def __init__(self, project_root: Optional[str] = None):
        self.project_root = Path(project_root or "/home/ezzeldin/Documents/Default Project")
        self.env_file = self.project_root / ".env"
        self.n8n_url = "http://localhost:5677"
        self.token_file = self.project_root / "memory/.google_calendar_tokens.json"
        self.token_file.parent.mkdir(parents=True, exist_ok=True)
    
    def load_env(self) -> dict[str, str]:
        """Load environment variables from .env file."""
        env = {}
        if self.env_file.exists():
            for line in self.env_file.read_text().splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
        return env
    
    def save_env(self, updates: dict[str, str]) -> None:
        """Update .env file with new values."""
        env = self.load_env()
        env.update(updates)
        lines = [f"{k}={v}" for k, v in env.items()]
        self.env_file.write_text("\n".join(lines) + "\n")
    
    def get_n8n_api_key(self) -> Optional[str]:
        """Get n8n API key from environment."""
        env = self.load_env()
        return env.get("N8N_API_KEY")
    
    def load_tokens(self) -> dict[str, Any]:
        """Load stored OAuth tokens."""
        if self.token_file.exists():
            return json.loads(self.token_file.read_text())
        return {}
    
    def save_tokens(self, tokens: dict[str, Any]) -> None:
        """Save OAuth tokens to file."""
        self.token_file.write_text(json.dumps(tokens, indent=2))
    
    def refresh_access_token(self, refresh_token: str, client_id: str, client_secret: str) -> Optional[dict]:
        """Refresh Google OAuth access token using refresh token."""
        try:
            data = urllib.parse.urlencode({
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }).encode()
            
            req = urllib.request.Request(
                "https://oauth2.googleapis.com/token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode())
        except Exception as e:
            print(f"Token refresh failed: {e}")
            return None
    
    def test_calendar_access(self, access_token: str) -> bool:
        """Test if access token works with Calendar API."""
        try:
            req = urllib.request.Request(
                "https://www.googleapis.com/calendar/v3/users/me/calendarList",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status == 200
        except Exception:
            return False
    
    def get_n8n_credentials(self) -> list[dict]:
        """Get all n8n credentials via API."""
        api_key = self.get_n8n_api_key()
        if not api_key:
            return []
        
        try:
            req = urllib.request.Request(
                f"{self.n8n_url}/api/v1/credentials",
                headers={"X-N8N-API-KEY": api_key}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read().decode()).get("data", [])
        except Exception as e:
            print(f"Failed to get n8n credentials: {e}")
            return []
    
    def update_n8n_credential(self, cred_id: str, updates: dict) -> bool:
        """Update n8n credential via API."""
        api_key = self.get_n8n_api_key()
        if not api_key:
            return False
        
        try:
            data = json.dumps(updates).encode()
            req = urllib.request.Request(
                f"{self.n8n_url}/api/v1/credentials/{cred_id}",
                data=data,
                method="PATCH",
                headers={
                    "X-N8N-API-KEY": api_key,
                    "Content-Type": "application/json"
                }
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status == 200
        except Exception as e:
            print(f"Failed to update credential {cred_id}: {e}")
            return False
    
    def get_workflows_using_credential(self, cred_id: str) -> list[dict]:
        """Get workflows that use a specific credential."""
        api_key = self.get_n8n_api_key()
        if not api_key:
            return []
        
        try:
            req = urllib.request.Request(
                f"{self.n8n_url}/api/v1/workflows",
                headers={"X-N8N-API-KEY": api_key}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                workflows = json.loads(r.read().decode()).get("data", [])
            
            # Filter workflows using this credential
            using = []
            for wf in workflows:
                nodes = wf.get("nodes", [])
                for node in nodes:
                    creds = node.get("credentials", {})
                    for cred_type, cred_info in creds.items():
                        if isinstance(cred_info, dict) and cred_info.get("id") == cred_id:
                            using.append(wf)
                            break
            return using
        except Exception as e:
            print(f"Failed to get workflows: {e}")
            return []
    
    def reactivate_workflow(self, workflow_id: str) -> bool:
        """Reactivate a workflow via n8n API."""
        api_key = self.get_n8n_api_key()
        if not api_key:
            return False
        
        try:
            # Deactivate first
            req = urllib.request.Request(
                f"{self.n8n_url}/api/v1/workflows/{workflow_id}/deactivate",
                method="POST",
                headers={"X-N8N-API-KEY": api_key}
            )
            urllib.request.urlopen(req, timeout=10)
            
            # Then activate
            req = urllib.request.Request(
                f"{self.n8n_url}/api/v1/workflows/{workflow_id}/activate",
                method="POST",
                headers={"X-N8N-API-KEY": api_key}
            )
            with urllib.request.urlopen(req, timeout=10) as r:
                return r.status == 200
        except Exception as e:
            print(f"Failed to reactivate workflow {workflow_id}: {e}")
            return False
    
    def check_and_refresh(self) -> dict[str, Any]:
        """
        Main function: check all Google Calendar credentials, refresh if expired,
        and reactivate affected workflows.
        """
        result = {
            "checked": 0,
            "refreshed": 0,
            "reactivated": 0,
            "errors": []
        }
        
        # Load stored tokens
        stored = self.load_tokens()
        env = self.load_env()
        
        client_id = env.get("GOOGLE_CLIENT_ID") or stored.get("client_id")
        client_secret = env.get("GOOGLE_CLIENT_SECRET") or stored.get("client_secret")
        
        if not client_id or not client_secret:
            result["errors"].append("Missing GOOGLE_CLIENT_ID/SECRET in .env or token file")
            return result
        
        # Get all n8n credentials
        creds = self.get_n8n_credentials()
        google_cal_creds = [c for c in creds if c.get("type") == "googleCalendarOAuth2Api"]
        
        for cred in google_cal_creds:
            result["checked"] += 1
            cred_id = cred.get("id")
            cred_name = cred.get("name", "Unknown")
            
            # Get stored tokens for this credential
            cred_tokens = stored.get(cred_id, {})
            refresh_token = cred_tokens.get("refresh_token")
            access_token = cred_tokens.get("access_token")
            
            if not refresh_token:
                result["errors"].append(f"{cred_name}: no refresh_token stored")
                continue
            
            # Test current access token
            token_works = False
            if access_token:
                token_works = self.test_calendar_access(access_token)
            
            if not token_works:
                print(f"Token expired for {cred_name}, refreshing...")
                new_tokens = self.refresh_access_token(refresh_token, client_id, client_secret)
                
                if new_tokens and "access_token" in new_tokens:
                    # Update stored tokens
                    cred_tokens.update({
                        "access_token": new_tokens["access_token"],
                        "expires_at": time.time() + new_tokens.get("expires_in", 3600)
                    })
                    if "refresh_token" in new_tokens:
                        cred_tokens["refresh_token"] = new_tokens["refresh_token"]
                    
                    stored[cred_id] = cred_tokens
                    self.save_tokens(stored)
                    
                    # Update n8n credential
                    if self.update_n8n_credential(cred_id, {
                        "data": {
                            "accessToken": new_tokens["access_token"],
                            "refreshToken": cred_tokens.get("refresh_token", refresh_token),
                            "scope": cred_tokens.get("scope", "https://www.googleapis.com/auth/calendar"),
                            "tokenType": "Bearer",
                            "expiresAt": cred_tokens.get("expires_at", 0) * 1000
                        }
                    }):
                        result["refreshed"] += 1
                        print(f"  ✓ Refreshed {cred_name}")
                        
                        # Reactivate workflows using this credential
                        workflows = self.get_workflows_using_credential(cred_id)
                        for wf in workflows:
                            wf_id = wf.get("id")
                            if self.reactivate_workflow(wf_id):
                                result["reactivated"] += 1
                                print(f"  ✓ Reactivated workflow {wf.get('name', wf_id)}")
                            else:
                                result["errors"].append(f"Failed to reactivate {wf.get('name', wf_id)}")
                    else:
                        result["errors"].append(f"Failed to update n8n credential for {cred_name}")
                else:
                    result["errors"].append(f"Token refresh failed for {cred_name}")
            else:
                print(f"Token valid for {cred_name}")
        
        return result
    
    def run_daemon(self, interval: int = 300) -> None:
        """Run as daemon, checking every interval seconds."""
        print(f"Starting Google Calendar OAuth daemon (interval: {interval}s)")
        while True:
            try:
                result = self.check_and_refresh()
                print(f"Check complete: {result}")
            except Exception as e:
                print(f"Daemon error: {e}")
            time.sleep(interval)


def main():
    import sys
    manager = GoogleCalendarOAuthManager()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "check":
            result = manager.check_and_refresh()
            print(json.dumps(result, indent=2))
        elif cmd == "daemon":
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
            manager.run_daemon(interval)
        elif cmd == "test-token":
            tokens = manager.load_tokens()
            for cred_id, cred_tokens in tokens.items():
                if cred_id not in ("client_id", "client_secret"):
                    access = cred_tokens.get("access_token")
                    if access:
                        works = manager.test_calendar_access(access)
                        print(f"{cred_id}: {'VALID' if works else 'EXPIRED'}")
        else:
            print("Usage: google_calendar_oauth.py [check|daemon|test-token]")
    else:
        # Default: run once
        result = manager.check_and_refresh()
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()