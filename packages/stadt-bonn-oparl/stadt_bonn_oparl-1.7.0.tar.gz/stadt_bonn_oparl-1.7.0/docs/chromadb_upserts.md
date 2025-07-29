# ChromaDB Upsert Operations Documentation

This document describes which models get upserted into ChromaDB through the API routers, including the specific metadata fields stored for each model type.

## Overview

The API implements ChromaDB upsert operations across 7 out of 10 router files. Each upsert operation stores the full model data as JSON documents along with specific metadata fields for efficient querying.

## Models with ChromaDB Upserts

### 1. AgendaItems Router (`src/stadt_bonn_oparl/api/routers/agendaitems.py`)

**Model**: `AgendaItemResponse` (from `src/stadt_bonn_oparl/api/models.py`, inherits from `OParlAgendaItem`)  
**Collection**: Retrieved via `chromadb_agendaitems_collection` dependency  
**Function**: `chromadb_upsert_agenda_item()`

**Upsert Data Structure**:
- **Document**: Full model JSON (`data.model_dump_json()`)
- **Metadata**:
  - `id`: Agenda item ID
  - `name`: Agenda item name
  - `number`: Agenda item number
  - `order`: Display order
  - `public`: Public visibility flag
  - `meeting`: Associated meeting reference
- **ID**: Uses the agenda item's ID as ChromaDB document ID

### 2. Files Router (`src/stadt_bonn_oparl/api/routers/files.py`)

**Model**: `FileResponse` (from `src/stadt_bonn_oparl/api/models.py`, inherits from `OParlFile`)  
**Collection**: Retrieved via `chromadb_files_collection` dependency  
**Function**: `chromadb_upsert_file()`

**Upsert Data Structure**:
- **Document**: Full model JSON (`file.model_dump_json()`)
- **Metadata**:
  - `id`: File ID
  - `type`: File type
  - `name`: File name
  - `fileName`: Original filename
  - `date`: File date (ISO format if present)
  - `mimeType`: MIME type
  - `agendaItem_ref`: Reference to agenda items
  - `meeting_ref`: Reference to meetings
  - `paper_ref`: Reference to papers
- **ID**: Uses the file's ID as ChromaDB document ID

### 3. Meetings Router (`src/stadt_bonn_oparl/api/routers/meetings.py`)

**Model**: `MeetingResponse` (from `src/stadt_bonn_oparl/api/models.py`, inherits from `OParlMeeting`)  
**Collection**: Retrieved via `chromadb_meetings_collection` dependency  
**Function**: `chromadb_upsert_meeting()`

**Upsert Data Structure**:
- **Document**: Full model JSON (`data.model_dump_json()`)
- **Metadata**:
  - `id`: Meeting ID
  - `name`: Meeting name
  - `start`: Meeting start time (ISO format if present)
  - `end`: Meeting end time (ISO format if present)
  - `meetingState`: Current state of the meeting
- **ID**: Uses the meeting's ID as ChromaDB document ID

**Note**: Supports batch upserts for `MeetingListResponse` objects.

### 4. Memberships Router (`src/stadt_bonn_oparl/api/routers/memberships.py`)

**Model**: `MembershipResponse` (from `src/stadt_bonn_oparl/api/models.py`, inherits from `OParlMembership`)  
**Collection**: Retrieved via `chromadb_memberships_collection` dependency  
**Function**: `chromadb_upsert_membership()`

**Upsert Data Structure**:
- **Document**: Full model JSON (`membership.model_dump_json()`)
- **Metadata**:
  - `id`: Membership ID
  - `type`: Membership type
- **ID**: Uses the membership's ID as ChromaDB document ID

**Note**: Supports batch upserts for `MembershipListResponse` objects.

### 5. Organizations Router (`src/stadt_bonn_oparl/api/routers/organizations.py`)

**Model**: `OrganizationResponse` (from `src/stadt_bonn_oparl/api/models.py`, inherits from `OParlOrganization`)  
**Collection**: Retrieved via `chromadb_organizations_collection` dependency  
**Function**: `chromadb_upsert_organization()`

**Upsert Data Structure**:
- **Document**: Full model JSON (`org.model_dump_json()`)
- **Metadata**:
  - `id`: Organization ID
  - `type`: Organization type
  - `name`: Organization name
  - `short_name`: Organization short name (`org.shortName`)
- **ID**: Uses the organization's ID as ChromaDB document ID

**Note**: Supports batch upserts for `OrganizationListResponse` objects.

### 6. Papers Router (`src/stadt_bonn_oparl/api/routers/papers.py`)

**Model**: `PaperResponse` (from `src/stadt_bonn_oparl/api/models.py`, inherits from `OParlPaper`)  
**Collection**: Retrieved via `chromadb_papers_collection` dependency  
**Function**: `chromadb_upsert_paper()`

**Upsert Data Structure**:
- **Document**: Full model JSON (`data.model_dump_json()`)
- **Metadata**:
  - `id`: Paper ID
  - `type`: Paper type
  - `name`: Paper name
  - `reference`: Paper reference number
  - `date`: Paper date (ISO format if present)
  - `paperType`: Type of paper document
  - `body_ref`: Reference to associated body
  - `mainFile_ref`: Reference to main file
- **ID**: Uses the paper's ID as ChromaDB document ID

**Note**: Supports batch upserts for `PaperListResponse` objects.

### 7. Persons Router (`src/stadt_bonn_oparl/api/routers/persons.py`)

**Model**: `PersonResponse` (from `src/stadt_bonn_oparl/api/models.py`, inherits from `OParlPerson`)  
**Collection**: Retrieved via `chromadb_persons_collection` dependency  
**Function**: `chromadb_upsert_person()`

**Upsert Data Structure**:
- **Document**: Full model JSON (`data.model_dump_json()`)
- **Metadata**:
  - `id`: Person ID
  - `type`: Person type
  - `affix`: Person's affix/title
  - `given_name`: Person's given name (`data.givenName`)
  - `family_name`: Person's family name (`data.familyName`)
  - `name`: Full person name
  - `gender`: Person's gender
  - `status`: Person's status (converted to string)
- **ID**: Uses the person's ID as ChromaDB document ID

## Routers WITHOUT ChromaDB Upserts

### 1. Bodies Router (`src/stadt_bonn_oparl/api/routers/bodies.py`)
- **No ChromaDB operations** - Only serves as a simple proxy to the upstream API

### 2. Locations Router (`src/stadt_bonn_oparl/api/routers/locations.py`)
- **No ChromaDB operations** - Only validates and returns location data from upstream API

### 3. Status Router (`src/stadt_bonn_oparl/api/routers/status.py`)
- **No upserts** - Only reads from ChromaDB collections to count documents for status reporting
- **Read Operations**: Counts documents from persons, organizations, memberships, and meetings collections

## Key Implementation Patterns

1. **Background Processing**: All upserts use FastAPI's `BackgroundTasks` for non-blocking operations
2. **Observability**: All operations are wrapped with Logfire spans for monitoring
3. **Batch Support**: List responses trigger multiple upserts for each item
4. **Full Document Storage**: Complete model JSON is stored as the document content
5. **Structured Metadata**: Key fields are extracted for efficient querying and filtering
6. **Consistent ID Strategy**: All use the OParl entity ID as the ChromaDB document ID

## Collection Names

The collections are managed through dependency injection, but based on the dependency names:
- `chromadb_agendaitems_collection`
- `chromadb_files_collection`
- `chromadb_meetings_collection`
- `chromadb_memberships_collection`
- `chromadb_organizations_collection`
- `chromadb_papers_collection`
- `chromadb_persons_collection`

## Architecture Benefits

This architecture provides a comprehensive caching layer that enables:
- **Full-text search** across all major OParl entities
- **Metadata-based querying** for efficient filtering
- **Complete data preservation** for detailed analysis
- **Non-blocking operations** for better API performance
- **Observability** through integrated monitoring