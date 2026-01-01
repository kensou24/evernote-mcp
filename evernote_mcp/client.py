"""Simplified Evernote API client for MCP server."""
import logging
from typing import Optional, List, Any

# Import from evernote-backup package (needs to be installed)
from evernote.edam.type.ttypes import Notebook, Note
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.error.ttypes import EDAMUserException, EDAMSystemException, EDAMNotFoundException

from evernote_backup.evernote_client import EvernoteClient as BaseEvernoteClient
from evernote_backup.evernote_client_util_ssl import get_cafile_path

logger = logging.getLogger(__name__)


class EvernoteMCPClient(BaseEvernoteClient):
    """Evernote client wrapper for MCP operations."""

    def __init__(self, auth_token: str, backend: str = "evernote",
                 network_retry_count: int = 5, use_system_ssl_ca: bool = False):
        """Initialize client with configuration.

        Args:
            auth_token: Evernote developer token
            backend: API backend (evernote, china, china:sandbox)
            network_retry_count: Number of network retries
            use_system_ssl_ca: Use system SSL CA certificates
        """
        cafile = None
        if use_system_ssl_ca:
            cafile = get_cafile_path(use_system_ssl_ca)

        super().__init__(
            backend=backend,
            token=auth_token,
            network_error_retry_count=network_retry_count,
            cafile=cafile,
        )

        # Verify connection on initialization
        try:
            self.verify_token()
            logger.info(f"Successfully authenticated as {self.user}")
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise

    # Notebook operations

    def list_notebooks(self) -> List[Notebook]:
        """List all notebooks."""
        return self.note_store.listNotebooks()

    def get_notebook(self, guid: str) -> Notebook:
        """Get notebook by GUID."""
        return self.note_store.getNotebook(guid)

    def create_notebook(self, name: str, stack: Optional[str] = None) -> Notebook:
        """Create a new notebook."""
        notebook = Notebook()
        notebook.name = name
        if stack:
            notebook.stack = stack

        return self.note_store.createNotebook(notebook)

    def update_notebook(self, notebook: Notebook) -> int:
        """Update existing notebook."""
        return self.note_store.updateNotebook(notebook)

    def expunge_notebook(self, guid: str) -> int:
        """Permanently delete notebook."""
        return self.note_store.expungeNotebook(guid)

    # Note operations

    def get_note(self, guid: str, with_content: bool = True) -> Note:
        """Get note by GUID."""
        return self.note_store.getNote(
            guid,
            withContent=with_content,
            withResourcesData=False,
            withResourcesRecognition=False,
            withResourcesAlternateData=False,
        )

    def create_note(self, title: str, content: str, notebook_guid: str,
                    tag_guids: Optional[List[str]] = None) -> Note:
        """Create a new note."""
        note = Note()
        note.title = title
        note.content = content
        note.notebookGuid = notebook_guid
        if tag_guids:
            note.tagGuids = tag_guids

        return self.note_store.createNote(note)

    def update_note(self, note: Note) -> Note:
        """Update existing note."""
        return self.note_store.updateNote(note)

    def delete_note(self, guid: str) -> Note:
        """Move note to trash (by setting active to False)."""
        note = self.get_note(guid, with_content=False)
        note.active = False
        return self.note_store.updateNote(note)

    def expunge_note(self, guid: str) -> int:
        """Permanently delete note."""
        return self.note_store.expungeNote(guid)

    def copy_note(self, guid: str, target_notebook_guid: str) -> Note:
        """Copy note to another notebook."""
        return self.note_store.copyNote(guid, target_notebook_guid)

    def find_notes(self, query: str, notebook_guid: Optional[str] = None,
                   limit: int = 100) -> Any:
        """Search notes using Evernote's search syntax."""
        note_filter = NoteFilter()
        note_filter.words = query
        if notebook_guid:
            note_filter.notebookGuid = notebook_guid

        result_spec = NotesMetadataResultSpec()
        result_spec.includeTitle = True
        result_spec.includeContent = True
        result_spec.includeUpdated = True
        result_spec.includeNotebookGuid = True

        return self.note_store.findNotesMetadata(
            filter=note_filter,
            offset=0,
            maxNotes=limit,
            resultSpec=result_spec,
        )

    def list_tags(self) -> List[Any]:
        """List all tags."""
        return self.note_store.listTags()
