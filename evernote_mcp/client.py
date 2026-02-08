"""Simplified Evernote API client for MCP server."""
import logging
from typing import Optional, List, Any

# Import from evernote-backup package (needs to be installed)
from evernote.edam.type.ttypes import Notebook, Note, Tag, SavedSearch
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec, RelatedQuery, RelatedResultSpec
from evernote.edam.error.ttypes import EDAMUserException, EDAMSystemException, EDAMNotFoundException
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

    def get_tag(self, guid: str) -> Tag:
        """Get tag by GUID."""
        return self.note_store.getTag(guid)

    def create_tag(self, name: str, parent_guid: Optional[str] = None) -> Tag:
        """Create a new tag."""
        tag = Tag()
        tag.name = name
        if parent_guid:
            tag.parentGuid = parent_guid
        return self.note_store.createTag(tag)

    def update_tag(self, tag: Tag) -> int:
        """Update existing tag."""
        return self.note_store.updateTag(tag)

    def expunge_tag(self, guid: str) -> int:
        """Permanently delete tag."""
        return self.note_store.expungeTag(guid)

    def list_tags_by_notebook(self, notebook_guid: str) -> List[Tag]:
        """List all tags used in a specific notebook."""
        return self.note_store.listTagsByNotebook(notebook_guid)

    def untag_all(self, guid: str) -> None:
        """Remove a tag from all notes."""
        self.note_store.untagAll(guid)

    # Saved search operations

    def list_searches(self) -> List[SavedSearch]:
        """List all saved searches."""
        return self.note_store.listSearches()

    def get_search(self, guid: str) -> SavedSearch:
        """Get saved search by GUID."""
        return self.note_store.getSearch(guid)

    def create_search(self, name: str, query: str) -> SavedSearch:
        """Create a new saved search."""
        search = SavedSearch()
        search.name = name
        search.query = query
        return self.note_store.createSearch(search)

    def update_search(self, search: SavedSearch) -> int:
        """Update existing saved search."""
        return self.note_store.updateSearch(search)

    def expunge_search(self, guid: str) -> int:
        """Permanently delete saved search."""
        return self.note_store.expungeSearch(guid)

    # Advanced note operations

    def get_note_content(self, guid: str) -> str:
        """Get just the ENML content of a note."""
        return self.note_store.getNoteContent(guid)

    def get_note_search_text(self, guid: str, note_only: bool = False,
                            tokenize_for_indexing: bool = False) -> str:
        """Get extracted plain text for indexing."""
        return self.note_store.getNoteSearchText(guid, note_only, tokenize_for_indexing)

    def get_note_tag_names(self, guid: str) -> List[str]:
        """Get tag names for a note."""
        return self.note_store.getNoteTagNames(guid)

    def list_note_versions(self, note_guid: str) -> List[Any]:
        """List previous versions of a note (Premium only)."""
        return self.note_store.listNoteVersions(note_guid)

    def get_note_version(self, note_guid: str, update_sequence_num: int,
                        with_resources_data: bool = False,
                        with_resources_recognition: bool = False,
                        with_resources_alternate_data: bool = False) -> Note:
        """Get a specific version of a note (Premium only)."""
        return self.note_store.getNoteVersion(
            note_guid, update_sequence_num,
            with_resources_data, with_resources_recognition, with_resources_alternate_data
        )

    # Sync and utility functions

    def get_sync_state(self) -> Any:
        """Get sync state information."""
        return self.note_store.getSyncState()

    def get_default_notebook(self) -> Notebook:
        """Get the default notebook."""
        return self.note_store.getDefaultNotebook()

    def find_note_counts(self, query: str = "", with_trash: bool = False) -> Any:
        """Get note counts for each notebook and tag."""
        note_filter = NoteFilter()
        note_filter.words = query
        return self.note_store.findNoteCounts(note_filter, with_trash)

    def find_related(self, query: RelatedQuery, result_spec: RelatedResultSpec) -> Any:
        """Find related entities (notes, notebooks, tags)."""
        return self.note_store.findRelated(query, result_spec)
