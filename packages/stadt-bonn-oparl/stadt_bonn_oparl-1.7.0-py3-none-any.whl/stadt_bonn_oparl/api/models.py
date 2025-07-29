import datetime
from typing import List, Optional

from pydantic import BaseModel

from stadt_bonn_oparl.models import (
    OParlAgendaItem,
    OParlFile,
    OParlLocation,
    OParlMeeting,
    OParlMembership,
    OParlOrganization,
    OParlPaper,
    OParlPerson,
)


class OParlResponse(BaseModel):
    """Base model for OParl API responses."""

    id: str

    created: Optional[datetime.datetime] = None
    modified: Optional[datetime.datetime] = None
    deleted: bool = False


class SystemResponse(OParlResponse):
    """Model for the system response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/System"
    oparlVersion: str = "https://schema.oparl.org/1.1/"
    otherOparlVersions: Optional[list[str]] = None
    license: Optional[str]
    body: str
    name: str
    contactEmail: Optional[str] = None
    contactName: Optional[str] = None
    website: Optional[str] = None
    vendor: str = "Mach! Den! Staat!"
    product: str = "Stadt Bonn OParl API Cache"


class PersonResponse(OParlResponse, OParlPerson):
    """Model for the person response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Person"

    membership_ref: Optional[List[str]] = None
    location_ref: Optional[str] = None


class PersonListResponse(BaseModel):
    """Model for a list of persons from the OParl API."""

    data: List[PersonResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class MembershipResponse(OParlResponse, OParlMembership):
    """Model for the membership response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Membership"

    person_ref: Optional[str] = None  # Internal use only, not part of the OParl schema

    organization_ref: Optional[str] = (
        None  # Internal use only, not part of the OParl schema
    )


class MembershipListResponse(BaseModel):
    """Model for a list of memberships from the OParl API."""

    data: List[MembershipResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class LocationResponse(OParlResponse, OParlLocation):
    """Model for the location response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Location"


class LocationListResponse(BaseModel):
    """Model for a list of locations from the OParl API."""

    data: List[LocationResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class OrganizationResponse(OParlResponse, OParlOrganization):
    """Model for the organization response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Organization"

    membership_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )
    location_ref: Optional[str] = (
        None  # Internal use only, not part of the OParl schema
    )
    meeting_ref: Optional[str] = None  # Internal use only, not part of the OParl schema


class OrganizationListResponse(BaseModel):
    """Model for a list of organizations from the OParl API."""

    data: List[OrganizationResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class MeetingResponse(OParlResponse, OParlMeeting):
    """Model for the meeting response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Meeting"

    location_ref: Optional[str] = (
        None  # Internal use only, not part of the OParl schema
    )
    organizations_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )


class MeetingListResponse(BaseModel):
    """Model for a list of meetings from the OParl API."""

    data: List[MeetingResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class AgendaItemResponse(OParlResponse, OParlAgendaItem):
    """Model for the agenda item response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/AgendaItem"


class AgendaItemListResponse(BaseModel):
    """Model for a list of agenda items from the OParl API."""

    data: List[AgendaItemResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class FileResponse(OParlResponse, OParlFile):
    """Model for the file response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/File"

    agendaItem_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )
    meeting_ref: Optional[str] = None  # Internal use only, not part of the OParl schema
    paper_ref: Optional[str] = None  # Internal use only, not part of the OParl schema


class FileListResponse(BaseModel):
    """Model for a list of files from the OParl API."""

    data: List[FileResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None


class PaperResponse(OParlResponse, OParlPaper):
    """Model for the paper response from the OParl API."""

    type: str = "https://schema.oparl.org/1.1/Paper"

    body_ref: Optional[str] = None  # Internal use only, not part of the OParl schema
    relatedPapers_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )
    superordinatedPaper_ref: Optional[str] = (
        None  # Internal use only, not part of the OParl schema
    )
    subordinatedPaper_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )
    mainFile_ref: Optional[str] = (
        None  # Internal use only, not part of the OParl schema
    )
    mainFileAccessUrl: Optional[str] = (
        None  # Internal use only, not part of the OParl schema
    )
    mainFileFilename: Optional[str] = (
        None  # Internal use only, not part of the OParl schema
    )
    auxilaryFiles_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )
    location_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )
    originatorPerson_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )
    underDirectionOfPerson_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )
    originatorOrganization_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )
    consultation_ref: Optional[List[str]] = (
        None  # Internal use only, not part of the OParl schema
    )


class PaperListResponse(BaseModel):
    """Model for a list of papers from the OParl API."""

    data: List[PaperResponse] = []

    pagination: Optional[dict] = None
    links: Optional[dict] = None
