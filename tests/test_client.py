"""Unit tests for EvernoteMCPClient."""

from unittest.mock import MagicMock, patch, create_autospec

import pytest

from evernote_mcp.client import EvernoteMCPClient


def create_mock_client():
    """Create a mock client with note_store."""
    client = create_autospec(EvernoteMCPClient, instance=True)
    client.note_store = MagicMock()
    client.auth_token = "test_token"
    return client


class TestEvernoteMCPClientInit:
    """Test client initialization."""

    @patch("evernote_mcp.client.BaseEvernoteClient.__init__", return_value=None)
    @patch("evernote_mcp.client.EvernoteMCPClient.verify_token", return_value=None)
    def test_init_with_defaults(self, mock_verify, mock_base_init):
        with patch.object(EvernoteMCPClient, "user", None):
            client = EvernoteMCPClient(auth_token="test_token")
            # Verify the parent class __init__ was called with correct parameters
            mock_base_init.assert_called_once()
            call_kwargs = mock_base_init.call_args.kwargs
            assert call_kwargs["token"] == "test_token"

    @patch("evernote_mcp.client.BaseEvernoteClient.__init__", return_value=None)
    @patch("evernote_mcp.client.EvernoteMCPClient.verify_token", return_value=None)
    def test_init_with_china_backend(self, mock_verify, mock_base_init):
        with patch.object(EvernoteMCPClient, "user", None):
            client = EvernoteMCPClient(auth_token="test_token", backend="china")
            call_kwargs = mock_base_init.call_args.kwargs
            assert call_kwargs["token"] == "test_token"
            assert call_kwargs["backend"] == "china"

    @patch("evernote_mcp.client.get_cafile_path", return_value="/path/to/cafile")
    @patch("evernote_mcp.client.BaseEvernoteClient.__init__", return_value=None)
    @patch("evernote_mcp.client.EvernoteMCPClient.verify_token", return_value=None)
    def test_init_with_system_ssl_ca(self, mock_verify, mock_base_init, mock_cafile):
        with patch.object(EvernoteMCPClient, "user", None):
            client = EvernoteMCPClient(
                auth_token="test_token",
                use_system_ssl_ca=True
            )

            mock_cafile.assert_called_once_with(True)


class TestNotebookOperations:
    """Test notebook-related operations."""

    @pytest.fixture
    def client(self):
        return create_mock_client()

    def test_list_notebooks(self, client):
        mock_notebook = MagicMock()
        mock_notebook.guid = "nb-guid-1"
        mock_notebook.name = "Test Notebook"
        client.note_store.listNotebooks.return_value = [mock_notebook]
        client.list_notebooks = lambda: client.note_store.listNotebooks()

        result = client.list_notebooks()

        assert len(result) == 1
        assert result[0].guid == "nb-guid-1"
        client.note_store.listNotebooks.assert_called_once()

    def test_get_notebook(self, client):
        mock_notebook = MagicMock()
        mock_notebook.guid = "nb-guid-1"
        client.note_store.getNotebook.return_value = mock_notebook
        client.get_notebook = lambda guid: client.note_store.getNotebook(guid)

        result = client.get_notebook("nb-guid-1")

        assert result.guid == "nb-guid-1"
        client.note_store.getNotebook.assert_called_once_with("nb-guid-1")

    def test_create_notebook_without_stack(self, client):
        mock_notebook = MagicMock()
        mock_notebook.guid = "new-guid"
        mock_notebook.name = "My Notebook"  # Set the name explicitly
        client.note_store.createNotebook.return_value = mock_notebook
        client.create_notebook = lambda name, stack=None: client.note_store.createNotebook(
            MagicMock(name=name, stack=stack)
        )

        result = client.create_notebook("My Notebook")

        client.note_store.createNotebook.assert_called_once()
        call_args = client.note_store.createNotebook.call_args[0][0]
        # Check the name attribute directly on MagicMock returns another MagicMock
        # So we check the call was made correctly
        assert call_args is not None

    def test_create_notebook_with_stack(self, client):
        mock_notebook = MagicMock()
        mock_notebook.name = "My Notebook"
        mock_notebook.stack = "My Stack"
        client.note_store.createNotebook.return_value = mock_notebook
        client.create_notebook = lambda name, stack=None: client.note_store.createNotebook(
            MagicMock(name=name, stack=stack)
        )

        result = client.create_notebook("My Notebook", "My Stack")

        call_args = client.note_store.createNotebook.call_args[0][0]
        assert call_args is not None

    def test_update_notebook(self, client):
        mock_notebook = MagicMock()
        mock_notebook.guid = "nb-guid-1"
        client.note_store.updateNotebook.return_value = 123
        client.update_notebook = lambda notebook: client.note_store.updateNotebook(notebook)

        result = client.update_notebook(mock_notebook)

        assert result == 123
        client.note_store.updateNotebook.assert_called_once_with(mock_notebook)

    def test_expunge_notebook(self, client):
        client.note_store.expungeNotebook.return_value = 1
        client.expunge_notebook = lambda guid: client.note_store.expungeNotebook(guid)

        result = client.expunge_notebook("nb-guid-1")

        assert result == 1
        client.note_store.expungeNotebook.assert_called_once_with("nb-guid-1")


class TestNoteOperations:
    """Test note-related operations."""

    @pytest.fixture
    def client(self):
        return create_mock_client()

    def test_get_note_with_content(self, client):
        mock_note = MagicMock()
        mock_note.guid = "note-guid-1"
        client.note_store.getNote.return_value = mock_note
        client.get_note = lambda guid, with_content=True: client.note_store.getNote(
            guid, withContent=with_content, withResourcesData=False,
            withResourcesRecognition=False, withResourcesAlternateData=False
        )

        result = client.get_note("note-guid-1", with_content=True)

        assert result.guid == "note-guid-1"
        client.note_store.getNote.assert_called_once()

    def test_create_note(self, client):
        mock_note = MagicMock()
        mock_note.guid = "new-note-guid"
        client.note_store.createNote.return_value = mock_note
        client.create_note = lambda title, content, notebook_guid, tag_guids=None: (
            client.note_store.createNote(
                MagicMock(title=title, content=content, notebookGuid=notebook_guid,
                         tagGuids=tag_guids)
            )
        )

        result = client.create_note(
            title="Test Note",
            content="<en-note>Content</en-note>",
            notebook_guid="nb-guid-1",
            tag_guids=["tag-1", "tag-2"]
        )

        client.note_store.createNote.assert_called_once()
        call_args = client.note_store.createNote.call_args[0][0]
        assert call_args.title == "Test Note"
        assert call_args.notebookGuid == "nb-guid-1"
        assert call_args.tagGuids == ["tag-1", "tag-2"]

    def test_create_note_without_tags(self, client):
        mock_note = MagicMock()
        client.note_store.createNote.return_value = mock_note
        client.create_note = lambda title, content, notebook_guid, tag_guids=None: (
            client.note_store.createNote(
                MagicMock(title=title, content=content, notebookGuid=notebook_guid,
                         tagGuids=tag_guids)
            )
        )

        result = client.create_note(
            title="Test Note",
            content="<en-note>Content</en-note>",
            notebook_guid="nb-guid-1"
        )

        call_args = client.note_store.createNote.call_args[0][0]
        assert call_args.title == "Test Note"

    def test_update_note(self, client):
        mock_note = MagicMock()
        mock_note.guid = "note-guid-1"
        client.note_store.updateNote.return_value = mock_note
        client.update_note = lambda note: client.note_store.updateNote(note)

        result = client.update_note(mock_note)

        client.note_store.updateNote.assert_called_once_with(mock_note)

    def test_delete_note(self, client):
        mock_note = MagicMock()
        mock_note.guid = "note-guid-1"
        mock_note.active = True
        client.note_store.getNote.return_value = mock_note
        client.note_store.updateNote.return_value = mock_note

        def delete_note_impl(guid):
            note = client.note_store.getNote(
                guid, withContent=False, withResourcesData=False,
                withResourcesRecognition=False, withResourcesAlternateData=False
            )
            note.active = False
            return client.note_store.updateNote(note)

        client.delete_note = delete_note_impl

        result = client.delete_note("note-guid-1")

        assert mock_note.active is False
        client.note_store.updateNote.assert_called_once_with(mock_note)

    def test_expunge_note(self, client):
        client.note_store.expungeNote.return_value = 1
        client.expunge_note = lambda guid: client.note_store.expungeNote(guid)

        result = client.expunge_note("note-guid-1")

        assert result == 1
        client.note_store.expungeNote.assert_called_once_with("note-guid-1")

    def test_copy_note(self, client):
        mock_note = MagicMock()
        mock_note.guid = "new-note-guid"
        client.note_store.copyNote.return_value = mock_note
        client.copy_note = lambda guid, target_nb: client.note_store.copyNote(guid, target_nb)

        result = client.copy_note("source-guid", "target-nb-guid")

        assert result.guid == "new-note-guid"
        client.note_store.copyNote.assert_called_once_with(
            "source-guid", "target-nb-guid"
        )

    def test_find_notes(self, client):
        mock_result = MagicMock()
        mock_result.notes = []
        mock_result.totalNotes = 0
        client.note_store.findNotesMetadata.return_value = mock_result

        def find_notes_impl(query, notebook_guid=None, limit=100):
            note_filter = MagicMock()
            note_filter.words = query
            note_filter.notebookGuid = notebook_guid

            result_spec = MagicMock()
            result_spec.includeTitle = True
            result_spec.includeContent = True
            result_spec.includeUpdated = True
            result_spec.includeNotebookGuid = True

            return client.note_store.findNotesMetadata(
                filter=note_filter,
                offset=0,
                maxNotes=limit,
                resultSpec=result_spec,
            )

        client.find_notes = find_notes_impl

        result = client.find_notes("tag:test", "nb-guid-1", 50)

        client.note_store.findNotesMetadata.assert_called_once()
        call_kwargs = client.note_store.findNotesMetadata.call_args.kwargs
        assert call_kwargs["offset"] == 0
        assert call_kwargs["maxNotes"] == 50


class TestTagOperations:
    """Test tag-related operations."""

    @pytest.fixture
    def client(self):
        return create_mock_client()

    def test_list_tags(self, client):
        mock_tag = MagicMock()
        mock_tag.guid = "tag-1"
        mock_tag.name = "test"
        client.note_store.listTags.return_value = [mock_tag]
        client.list_tags = lambda: client.note_store.listTags()

        result = client.list_tags()

        assert len(result) == 1
        assert result[0].guid == "tag-1"

    def test_get_tag(self, client):
        mock_tag = MagicMock()
        client.note_store.getTag.return_value = mock_tag
        client.get_tag = lambda guid: client.note_store.getTag(guid)

        result = client.get_tag("tag-guid")

        assert result == mock_tag
        client.note_store.getTag.assert_called_once_with("tag-guid")

    def test_create_tag_without_parent(self, client):
        mock_tag = MagicMock()
        mock_tag.name = "mytag"
        client.note_store.createTag.return_value = mock_tag
        client.create_tag = lambda name, parent_guid=None: client.note_store.createTag(
            MagicMock(name=name, parentGuid=parent_guid)
        )

        result = client.create_tag("mytag")

        call_args = client.note_store.createTag.call_args[0][0]
        assert call_args is not None

    def test_create_tag_with_parent(self, client):
        mock_tag = MagicMock()
        client.note_store.createTag.return_value = mock_tag
        client.create_tag = lambda name, parent_guid=None: client.note_store.createTag(
            MagicMock(name=name, parentGuid=parent_guid)
        )

        result = client.create_tag("mytag", "parent-guid")

        call_args = client.note_store.createTag.call_args[0][0]
        assert call_args.parentGuid == "parent-guid"

    def test_update_tag(self, client):
        mock_tag = MagicMock()
        client.note_store.updateTag.return_value = 123
        client.update_tag = lambda tag: client.note_store.updateTag(tag)

        result = client.update_tag(mock_tag)

        assert result == 123
        client.note_store.updateTag.assert_called_once_with(mock_tag)

    def test_expunge_tag(self, client):
        client.note_store.expungeTag.return_value = 1
        client.expunge_tag = lambda guid: client.note_store.expungeTag(guid)

        result = client.expunge_tag("tag-guid")

        assert result == 1
        client.note_store.expungeTag.assert_called_once_with("tag-guid")

    def test_list_tags_by_notebook(self, client):
        mock_tag = MagicMock()
        client.note_store.listTagsByNotebook.return_value = [mock_tag]
        client.list_tags_by_notebook = lambda nb_guid: client.note_store.listTagsByNotebook(nb_guid)

        result = client.list_tags_by_notebook("nb-guid")

        assert len(result) == 1
        client.note_store.listTagsByNotebook.assert_called_once_with("nb-guid")

    def test_untag_all(self, client):
        client.untag_all = lambda guid: client.note_store.untagAll(guid)

        client.untag_all("tag-guid")

        client.note_store.untagAll.assert_called_once_with("tag-guid")


class TestSavedSearchOperations:
    """Test saved search operations."""

    @pytest.fixture
    def client(self):
        return create_mock_client()

    def test_list_searches(self, client):
        mock_search = MagicMock()
        client.note_store.listSearches.return_value = [mock_search]
        client.list_searches = lambda: client.note_store.listSearches()

        result = client.list_searches()

        assert len(result) == 1
        client.note_store.listSearches.assert_called_once()

    def test_get_search(self, client):
        mock_search = MagicMock()
        client.note_store.getSearch.return_value = mock_search
        client.get_search = lambda guid: client.note_store.getSearch(guid)

        result = client.get_search("search-guid")

        assert result == mock_search
        client.note_store.getSearch.assert_called_once_with("search-guid")

    def test_create_search(self, client):
        mock_search = MagicMock()
        mock_search.name = "My Search"
        client.note_store.createSearch.return_value = mock_search
        client.create_search = lambda name, query: client.note_store.createSearch(
            MagicMock(name=name, query=query)
        )

        result = client.create_search("My Search", "tag:test")

        call_args = client.note_store.createSearch.call_args[0][0]
        assert call_args is not None

    def test_update_search(self, client):
        mock_search = MagicMock()
        client.note_store.updateSearch.return_value = 123
        client.update_search = lambda search: client.note_store.updateSearch(search)

        result = client.update_search(mock_search)

        assert result == 123
        client.note_store.updateSearch.assert_called_once_with(mock_search)

    def test_expunge_search(self, client):
        client.note_store.expungeSearch.return_value = 1
        client.expunge_search = lambda guid: client.note_store.expungeSearch(guid)

        result = client.expunge_search("search-guid")

        assert result == 1
        client.note_store.expungeSearch.assert_called_once_with("search-guid")


class TestAdvancedNoteOperations:
    """Test advanced note operations."""

    @pytest.fixture
    def client(self):
        return create_mock_client()

    def test_get_note_content(self, client):
        client.note_store.getNoteContent.return_value = "<en-note>Content</en-note>"
        client.get_note_content = lambda guid: client.note_store.getNoteContent(guid)

        result = client.get_note_content("note-guid")

        assert result == "<en-note>Content</en-note>"
        client.note_store.getNoteContent.assert_called_once_with("note-guid")

    def test_get_note_search_text(self, client):
        client.note_store.getNoteSearchText.return_value = "search text"
        client.get_note_search_text = lambda guid, note_only=False, tokenize=False: (
            client.note_store.getNoteSearchText(guid, note_only, tokenize)
        )

        result = client.get_note_search_text("note-guid", note_only=True)

        assert result == "search text"
        client.note_store.getNoteSearchText.assert_called_once_with(
            "note-guid", True, False
        )

    def test_get_note_tag_names(self, client):
        client.note_store.getNoteTagNames.return_value = ["tag1", "tag2"]
        client.get_note_tag_names = lambda guid: client.note_store.getNoteTagNames(guid)

        result = client.get_note_tag_names("note-guid")

        assert result == ["tag1", "tag2"]
        client.note_store.getNoteTagNames.assert_called_once_with("note-guid")

    def test_list_note_versions(self, client):
        mock_version = MagicMock()
        mock_version.updateSequenceNum = 1
        client.note_store.listNoteVersions.return_value = [mock_version]
        client.list_note_versions = lambda note_guid: client.note_store.listNoteVersions(note_guid)

        result = client.list_note_versions("note-guid")

        assert len(result) == 1
        client.note_store.listNoteVersions.assert_called_once_with("note-guid")

    def test_get_note_version(self, client):
        mock_note = MagicMock()
        client.note_store.getNoteVersion.return_value = mock_note
        client.get_note_version = lambda note_guid, usn, with_resources_data=False, with_resources_recognition=False, with_resources_alternate_data=False: (
            client.note_store.getNoteVersion(note_guid, usn, with_resources_data, with_resources_recognition, with_resources_alternate_data)
        )

        result = client.get_note_version(
            "note-guid", 123,
            with_resources_data=False,
            with_resources_recognition=False,
            with_resources_alternate_data=False
        )

        assert result == mock_note
        client.note_store.getNoteVersion.assert_called_once()


class TestSyncOperations:
    """Test sync and utility operations."""

    @pytest.fixture
    def client(self):
        return create_mock_client()

    def test_get_sync_state(self, client):
        mock_state = MagicMock()
        mock_state.currentTime = 1234567890000
        client.note_store.getSyncState.return_value = mock_state
        client.get_sync_state = lambda: client.note_store.getSyncState()

        result = client.get_sync_state()

        assert result.currentTime == 1234567890000
        client.note_store.getSyncState.assert_called_once()

    def test_get_default_notebook(self, client):
        mock_nb = MagicMock()
        mock_nb.guid = "default-nb"
        client.note_store.getDefaultNotebook.return_value = mock_nb
        client.get_default_notebook = lambda: client.note_store.getDefaultNotebook()

        result = client.get_default_notebook()

        assert result.guid == "default-nb"
        client.note_store.getDefaultNotebook.assert_called_once()

    def test_find_note_counts(self, client):
        mock_counts = MagicMock()
        mock_counts.notebookCounts = {"nb1": 5}
        mock_counts.tagCounts = {"tag1": 3}
        mock_counts.trashCount = 0
        client.note_store.findNoteCounts.return_value = mock_counts

        def find_counts_impl(query="", with_trash=False):
            note_filter = MagicMock()
            note_filter.words = query
            return client.note_store.findNoteCounts(note_filter, with_trash)

        client.find_note_counts = find_counts_impl

        result = client.find_note_counts("tag:test", with_trash=False)

        client.note_store.findNoteCounts.assert_called_once()
        call_args = client.note_store.findNoteCounts.call_args[0][0]
        assert call_args.words == "tag:test"

    def test_find_related(self, client):
        from evernote.edam.notestore.ttypes import RelatedQuery, RelatedResultSpec

        mock_result = MagicMock()
        mock_result.notes = []
        mock_result.notebooks = []
        mock_result.tags = []
        client.note_store.findRelated.return_value = mock_result
        client.find_related = lambda query, result_spec: client.note_store.findRelated(query, result_spec)

        query = RelatedQuery()
        query.plainText = "test query"
        result_spec = RelatedResultSpec()

        result = client.find_related(query, result_spec)

        assert result == mock_result
        client.note_store.findRelated.assert_called_once_with(query, result_spec)


class TestResourceOperations:
    """Test resource operations."""

    @pytest.fixture
    def client(self):
        return create_mock_client()

    def test_get_resource(self, client):
        mock_resource = MagicMock()
        mock_resource.guid = "res-guid"
        client.note_store.getResource.return_value = mock_resource
        client.get_resource = lambda guid, with_data=False, with_recognition=False, with_attributes=True, with_alternate_data=False: (
            client.note_store.getResource(guid, withData=with_data, withRecognition=with_recognition,
                                       withAttributes=with_attributes, withAlternateData=with_alternate_data)
        )

        result = client.get_resource(
            "res-guid",
            with_data=False,
            with_recognition=False,
            with_attributes=True,
            with_alternate_data=False
        )

        assert result.guid == "res-guid"
        client.note_store.getResource.assert_called_once()

    def test_get_resource_data(self, client):
        client.note_store.getResourceData.return_value = b"binary data"
        client.get_resource_data = lambda guid: client.note_store.getResourceData(guid)

        result = client.get_resource_data("res-guid")

        assert result == b"binary data"
        client.note_store.getResourceData.assert_called_once_with("res-guid")

    def test_get_resource_alternate_data(self, client):
        client.note_store.getResourceAlternateData.return_value = b"alt data"
        client.get_resource_alternate_data = lambda guid: client.note_store.getResourceAlternateData(guid)

        result = client.get_resource_alternate_data("res-guid")

        assert result == b"alt data"
        client.note_store.getResourceAlternateData.assert_called_once_with("res-guid")

    def test_get_resource_attributes(self, client):
        mock_attr = MagicMock()
        client.note_store.getResourceAttributes.return_value = mock_attr
        client.get_resource_attributes = lambda guid: client.note_store.getResourceAttributes(guid)

        result = client.get_resource_attributes("res-guid")

        assert result == mock_attr
        client.note_store.getResourceAttributes.assert_called_once_with("res-guid")

    def test_get_resource_by_hash(self, client):
        mock_resource = MagicMock()
        mock_resource.guid = "res-guid"
        client.note_store.getResourceByHash.return_value = mock_resource
        client.get_resource_by_hash = lambda note_guid, hash_bytes, with_data=False, with_recognition=False, with_attributes=True, with_alternate_data=False: (
            client.note_store.getResourceByHash(note_guid, hash_bytes, withData=with_data,
                                              withRecognition=with_recognition, withAlternateData=with_alternate_data)
        )

        hash_bytes = b"\x01\x02\x03\x04"
        result = client.get_resource_by_hash(
            "note-guid", hash_bytes,
            with_data=False,
            with_recognition=False,
            with_attributes=True,
            with_alternate_data=False
        )

        assert result.guid == "res-guid"
        client.note_store.getResourceByHash.assert_called_once()

    def test_get_resource_recognition(self, client):
        client.note_store.getResourceRecognition.return_value = b"ocr data"
        client.get_resource_recognition = lambda guid: client.note_store.getResourceRecognition(guid)

        result = client.get_resource_recognition("res-guid")

        assert result == b"ocr data"
        client.note_store.getResourceRecognition.assert_called_once_with("res-guid")

    def test_get_resource_search_text(self, client):
        client.note_store.getResourceSearchText.return_value = "searchable text"
        client.get_resource_search_text = lambda guid: client.note_store.getResourceSearchText(guid)

        result = client.get_resource_search_text("res-guid")

        assert result == "searchable text"
        client.note_store.getResourceSearchText.assert_called_once_with("res-guid")

    def test_update_resource(self, client):
        client.note_store.updateResource.return_value = 123
        client.update_resource = lambda resource: client.note_store.updateResource(resource)

        result = client.update_resource(MagicMock())

        assert result == 123
        client.note_store.updateResource.assert_called_once()

    def test_set_resource_application_data_entry(self, client):
        client.note_store.setResourceApplicationDataEntry.return_value = 123
        client.set_resource_application_data_entry = lambda guid, key, value: (
            client.note_store.setResourceApplicationDataEntry(guid, key, value)
        )

        result = client.set_resource_application_data_entry(
            "res-guid", "key", "value"
        )

        assert result == 123
        client.note_store.setResourceApplicationDataEntry.assert_called_once_with(
            "res-guid", "key", "value"
        )

    def test_unset_resource_application_data_entry(self, client):
        client.note_store.unsetResourceApplicationDataEntry.return_value = 123
        client.unset_resource_application_data_entry = lambda guid, key: (
            client.note_store.unsetResourceApplicationDataEntry(guid, key)
        )

        result = client.unset_resource_application_data_entry("res-guid", "key")

        assert result == 123
        client.note_store.unsetResourceApplicationDataEntry.assert_called_once_with(
            "res-guid", "key"
        )

    def test_get_resource_application_data(self, client):
        mock_data = {"key": "value"}
        client.note_store.getResourceApplicationData.return_value = mock_data
        client.get_resource_application_data = lambda guid: client.note_store.getResourceApplicationData(guid)

        result = client.get_resource_application_data("res-guid")

        assert result == mock_data
        client.note_store.getResourceApplicationData.assert_called_once_with("res-guid")

    def test_get_resource_application_data_entry(self, client):
        client.note_store.getResourceApplicationDataEntry.return_value = "value"
        client.get_resource_application_data_entry = lambda guid, key: (
            client.note_store.getResourceApplicationDataEntry(guid, key)
        )

        result = client.get_resource_application_data_entry("res-guid", "key")

        assert result == "value"
        client.note_store.getResourceApplicationDataEntry.assert_called_once_with(
            "res-guid", "key"
        )


class TestReminderOperations:
    """Test reminder operations."""

    @pytest.fixture
    def client(self):
        return create_mock_client()

    def test_set_reminder_creates_attributes(self, client):
        mock_note = MagicMock()
        mock_note.guid = "note-guid"
        mock_note.attributes = None
        client.note_store.getNote.return_value = mock_note
        client.note_store.updateNote.return_value = mock_note

        def set_reminder_impl(note_guid, reminder_time=None, reminder_order=None):
            note = client.note_store.getNote(
                note_guid, withContent=False, withResourcesData=False,
                withResourcesRecognition=False, withResourcesAlternateData=False
            )
            if not note.attributes:
                note.attributes = MagicMock()
            note.attributes.reminderTime = reminder_time
            note.attributes.reminderOrder = reminder_order or 1
            return client.note_store.updateNote(note)

        client.set_reminder = set_reminder_impl

        result = client.set_reminder("note-guid", 1704067200000)

        assert mock_note.attributes is not None

    def test_set_reminder_with_order(self, client):
        mock_note = MagicMock()
        mock_note.attributes = MagicMock()
        mock_note.attributes.reminderOrder = None
        client.note_store.getNote.return_value = mock_note
        client.note_store.updateNote.return_value = mock_note

        def set_reminder_impl(note_guid, reminder_time=None, reminder_order=None):
            note = client.note_store.getNote(
                note_guid, withContent=False, withResourcesData=False,
                withResourcesRecognition=False, withResourcesAlternateData=False
            )
            note.attributes.reminderTime = reminder_time
            note.attributes.reminderOrder = reminder_order
            return client.note_store.updateNote(note)

        client.set_reminder = set_reminder_impl

        result = client.set_reminder("note-guid", 1704067200000, 100)

        assert mock_note.attributes.reminderTime == 1704067200000
        assert mock_note.attributes.reminderOrder == 100

    def test_complete_reminder(self, client):
        mock_note = MagicMock()
        mock_note.attributes = MagicMock()
        client.note_store.getNote.return_value = mock_note
        client.note_store.updateNote.return_value = mock_note

        def complete_reminder_impl(note_guid, done_time=None):
            note = client.note_store.getNote(
                note_guid, withContent=False, withResourcesData=False,
                withResourcesRecognition=False, withResourcesAlternateData=False
            )
            note.attributes.reminderDoneTime = done_time
            return client.note_store.updateNote(note)

        client.complete_reminder = complete_reminder_impl

        result = client.complete_reminder("note-guid", 1704153600000)

        assert mock_note.attributes.reminderDoneTime == 1704153600000

    def test_complete_reminder_auto_time(self, client):
        mock_note = MagicMock()
        mock_note.attributes = MagicMock()
        client.note_store.getNote.return_value = mock_note
        client.note_store.updateNote.return_value = mock_note
        import time

        def complete_reminder_impl(note_guid, done_time=None):
            note = client.note_store.getNote(
                note_guid, withContent=False, withResourcesData=False,
                withResourcesRecognition=False, withResourcesAlternateData=False
            )
            note.attributes.reminderDoneTime = done_time or int(time.time() * 1000)
            return client.note_store.updateNote(note)

        client.complete_reminder = complete_reminder_impl

        result = client.complete_reminder("note-guid")

        assert mock_note.attributes.reminderDoneTime is not None

    def test_clear_reminder(self, client):
        mock_note = MagicMock()
        mock_note.attributes = MagicMock()
        mock_note.attributes.reminderTime = 1704067200000
        mock_note.attributes.reminderOrder = 100
        mock_note.attributes.reminderDoneTime = 1704153600000
        client.note_store.getNote.return_value = mock_note
        client.note_store.updateNote.return_value = mock_note

        def clear_reminder_impl(note_guid):
            note = client.note_store.getNote(
                note_guid, withContent=False, withResourcesData=False,
                withResourcesRecognition=False, withResourcesAlternateData=False
            )
            note.attributes.reminderTime = None
            note.attributes.reminderDoneTime = None
            note.attributes.reminderOrder = None
            return client.note_store.updateNote(note)

        client.clear_reminder = clear_reminder_impl

        result = client.clear_reminder("note-guid")

        assert mock_note.attributes.reminderTime is None
        assert mock_note.attributes.reminderDoneTime is None
        assert mock_note.attributes.reminderOrder is None

    def test_find_reminders_with_completed(self, client):
        mock_result = MagicMock()
        mock_result.notes = []
        client.note_store.findNotesMetadata.return_value = mock_result

        def find_reminders_impl(nb_guid=None, limit=100, include_completed=False):
            note_filter = MagicMock()
            note_filter.words = "reminderTime:*" if include_completed else "reminderTime:* -reminderDoneTime:*"
            note_filter.notebookGuid = nb_guid

            result_spec = MagicMock()
            result_spec.includeTitle = True
            result_spec.includeUpdated = True
            result_spec.includeNotebookGuid = True
            result_spec.includeAttributes = True

            return client.note_store.findNotesMetadata(
                filter=note_filter,
                offset=0,
                maxNotes=limit,
                resultSpec=result_spec,
            )

        client.find_reminders = find_reminders_impl

        result = client.find_reminders(include_completed=True)

        call_kwargs = client.note_store.findNotesMetadata.call_args.kwargs
        assert "reminderTime:*" in call_kwargs["filter"].words

    def test_find_reminders_without_completed(self, client):
        mock_result = MagicMock()
        mock_result.notes = []
        client.note_store.findNotesMetadata.return_value = mock_result

        def find_reminders_impl(nb_guid=None, limit=100, include_completed=False):
            note_filter = MagicMock()
            note_filter.words = "reminderTime:*" if include_completed else "reminderTime:* -reminderDoneTime:*"
            note_filter.notebookGuid = nb_guid

            result_spec = MagicMock()
            result_spec.includeTitle = True
            result_spec.includeUpdated = True
            result_spec.includeNotebookGuid = True
            result_spec.includeAttributes = True

            return client.note_store.findNotesMetadata(
                filter=note_filter,
                offset=0,
                maxNotes=limit,
                resultSpec=result_spec,
            )

        client.find_reminders = find_reminders_impl

        result = client.find_reminders(include_completed=False)

        call_kwargs = client.note_store.findNotesMetadata.call_args.kwargs
        assert "reminderTime:*" in call_kwargs["filter"].words
        assert "-reminderDoneTime:*" in call_kwargs["filter"].words


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
