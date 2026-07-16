"""Google Drive integration service."""
import logging
from typing import Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class GoogleDriveService:
    """Google Drive file operations."""

    def __init__(self):
        self.settings = get_settings()
        self._service = None

    def _get_service(self):
        if self._service:
            return self._service
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            # For service account auth (production)
            if self.settings.GOOGLE_DRIVE_CREDENTIALS_FILE:
                creds = service_account.Credentials.from_service_account_file(
                    self.settings.GOOGLE_DRIVE_CREDENTIALS_FILE,
                    scopes=["https://www.googleapis.com/auth/drive"],
                )
                self._service = build("drive", "v3", credentials=creds)
                return self._service

            # For OAuth2 auth (development) — tokens stored in DB
            logger.warning("Google Drive not configured. Set GOOGLE_DRIVE_CREDENTIALS_FILE.")
            return None
        except Exception as e:
            logger.error(f"Google Drive init failed: {e}")
            return None

    async def upload_file(self, file_bytes: bytes, filename: str, mime_type: str, folder_id: Optional[str] = None) -> Optional[dict]:
        """Upload a file to Google Drive."""
        service = self._get_service()
        if not service:
            logger.warning("Google Drive not available")
            return None

        try:
            import io
            from googleapiclient.http import MediaIoBaseUpload

            media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype=mime_type, resumable=True)
            file_metadata = {"name": filename}
            if folder_id:
                file_metadata["parents"] = [folder_id]

            file = service.files().create(
                body=file_metadata, media_body=media, fields="id, name, webViewLink, webContentLink"
            ).execute()

            return {
                "id": file.get("id"),
                "name": file.get("name"),
                "url": file.get("webViewLink"),
                "download_url": file.get("webContentLink"),
            }
        except Exception as e:
            logger.error(f"Drive upload failed: {e}")
            return None

    async def create_folder(self, name: str, parent_id: Optional[str] = None) -> Optional[dict]:
        """Create a folder in Google Drive."""
        service = self._get_service()
        if not service:
            return None

        try:
            file_metadata = {
                "name": name,
                "mimeType": "application/vnd.google-apps.folder",
            }
            if parent_id:
                file_metadata["parents"] = [parent_id]

            file = service.files().create(
                body=file_metadata, fields="id, name"
            ).execute()

            return {"id": file.get("id"), "name": file.get("name")}
        except Exception as e:
            logger.error(f"Drive folder creation failed: {e}")
            return None

    async def list_files(self, folder_id: Optional[str] = None, query: str = "", limit: int = 20) -> list[dict]:
        """List files in Google Drive."""
        service = self._get_service()
        if not service:
            return []

        try:
            q_parts = []
            if folder_id:
                q_parts.append(f"'{folder_id}' in parents")
            if query:
                q_parts.append(f"name contains '{query}'")
            q = " and ".join(q_parts) if q_parts else None

            results = service.files().list(
                q=q, pageSize=limit,
                fields="files(id, name, mimeType, size, createdTime, webViewLink)",
                orderBy="createdTime desc",
            ).execute()

            return results.get("files", [])
        except Exception as e:
            logger.error(f"Drive list failed: {e}")
            return []

    async def get_file_url(self, file_id: str) -> Optional[str]:
        """Get a shareable URL for a file."""
        service = self._get_service()
        if not service:
            return None

        try:
            file = service.files().get(
                fileId=file_id, fields="webViewLink"
            ).execute()
            return file.get("webViewLink")
        except Exception as e:
            logger.error(f"Drive URL failed: {e}")
            return None


# Singleton
drive_service = GoogleDriveService()
