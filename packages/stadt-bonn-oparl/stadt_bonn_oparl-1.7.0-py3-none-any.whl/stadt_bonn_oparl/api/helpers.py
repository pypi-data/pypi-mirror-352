from typing import Optional

import httpx
from fastapi import HTTPException
import logfire

from stadt_bonn_oparl.api.config import SELF_API_URL, UPSTREAM_API_URL
from stadt_bonn_oparl.api.models import (
    FileResponse,
    MeetingListResponse,
    MeetingResponse,
    MembershipListResponse,
    MembershipResponse,
    OrganizationListResponse,
    OrganizationResponse,
    PaperListResponse,
    PaperResponse,
    PersonResponse,
)


async def _get_membership(
    http_client: httpx.Client, membership_id: str
) -> MembershipResponse:
    """Helper function to get a membership by ID from the OParl API."""
    _url = "https://www.bonn.sitzung-online.de/public/oparl/memberships"

    response = http_client.get(_url + f"?id={membership_id}")
    if response.status_code == 200:
        _json = response.json()

        _json["person_ref"] = _json.get("person", None)
        if _json["person_ref"]:
            _json["person_ref"] = _json["person_ref"].replace(
                UPSTREAM_API_URL, SELF_API_URL
            )
        _json["person"] = None
        _json["organization_ref"] = _json.get("organization", None)
        if _json["organization_ref"]:
            _json["organization_ref"] = _json["organization_ref"].replace(
                UPSTREAM_API_URL, SELF_API_URL
            )
        _json["organization"] = None

        return MembershipResponse(**_json)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch membership {membership_id} information from OParl API",
        )


async def _get_person(
    http_client: httpx.Client, person_id: str | int
) -> PersonResponse:
    """Helper function to get a person by ID from the OParl API."""
    _url = "https://www.bonn.sitzung-online.de/public/oparl/persons"

    if not isinstance(person_id, str):
        person_id = str(person_id)

    response = http_client.get(_url + f"?id={person_id}")
    if response.status_code == 200:
        _json = response.json()

        # check if the person is deleted
        if _json.get("deleted", False):
            raise HTTPException(
                status_code=404,
                detail=f"Person with ID {person_id} not found in OParl API",
            )

        # _json['membership_ref'] shall be all the IDs from the memberships
        if "membership" in _json:
            _json["membership_ref"] = [
                membership["id"] for membership in _json["membership"]
            ]
            # rewrite each membership URL
            _json["membership_ref"] = [
                membership.replace(UPSTREAM_API_URL, SELF_API_URL)
                for membership in _json["membership_ref"]
            ]
        else:
            _json["membership_ref"] = None

        _json["membership"] = None
        _json["location_ref"] = _json["location"] if "location" in _json else None
        if _json["location_ref"]:
            _json["location_ref"] = _json["location_ref"].replace(
                UPSTREAM_API_URL, SELF_API_URL
            )
        _json["location"] = None

        return PersonResponse(**_json)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch person {person_id} information from OParl API",
        )


def _process_organization(org: dict) -> None:
    """Helper function to process organization data by converting URLs."""
    if "membership" in org and org["membership"] is not None:
        # rewrite each membership URL
        org["membership_ref"] = [
            membership.replace(UPSTREAM_API_URL, SELF_API_URL)
            for membership in org["membership"]
        ]
    else:
        org["membership_ref"] = None
    org["membership"] = None

    if "location" in org and org["location"] is not None:
        org["location_ref"] = org["location"]["id"].replace(
            UPSTREAM_API_URL, SELF_API_URL
        )
    else:
        org["location_ref"] = None
    org["location"] = None

    if "meeting" in org and org["meeting"] is not None:
        org["meeting_ref"] = org["meeting"].replace(UPSTREAM_API_URL, SELF_API_URL)
    else:
        org["meeting_ref"] = None
    org["meeting"] = None


async def _get_organization_all(
    http_client: httpx.Client,
) -> OrganizationListResponse:
    """Helper function to get all organizations from the OParl API."""
    _url = "https://www.bonn.sitzung-online.de/public/oparl/organizations"

    all_organizations = []
    current_url: Optional[str] = _url

    while current_url:
        response = http_client.get(current_url, timeout=10.0)
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Failed to fetch organizations from OParl API",
            )

        _json = response.json()

        # Process each organization in this page
        for org in _json["data"]:
            _process_organization(org)
            logfire.info(f"Processing organization: {org}")
            all_organizations.append(OrganizationResponse(**org))

        # Check for next page
        current_url = None
        if "links" in _json and "next" in _json["links"]:
            current_url = _json["links"]["next"]

    # Return all organizations with updated pagination info
    return OrganizationListResponse(
        data=all_organizations, pagination={"total": len(all_organizations)}, links={}
    )


async def _get_organization_by_id(
    http_client: httpx.Client, organization_id: str | int
) -> OrganizationResponse:
    """Helper function to get a organization by ID from the OParl API."""
    _url = "https://www.bonn.sitzung-online.de/public/oparl/organizations"

    if not isinstance(organization_id, str):
        organization_id = str(organization_id)

    response = http_client.get(_url + f"?typ=gr&id={organization_id}")
    if response.status_code == 200:
        _json = response.json()

        # check if the organization is deleted
        if _json.get("deleted", False):
            raise HTTPException(
                status_code=404,
                detail=f"Organization with ID {organization_id} not found in OParl API",
            )

        _process_organization(_json)
        return OrganizationResponse(**_json)
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch organization {organization_id} information from OParl API",
        )


async def _get_organization_by_body_id(
    http_client: httpx.Client, body_id: str | int
) -> OrganizationListResponse:
    """Helper function to get organizations by body ID from the OParl API."""
    _url = "https://www.bonn.sitzung-online.de/public/oparl/organizations"

    if not isinstance(body_id, str):
        body_id = str(body_id)

    all_organizations = []
    current_url: Optional[str] = _url + f"?typ=gr&body={body_id}"

    while current_url:
        response = http_client.get(current_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch organization with body ID {body_id} from OParl API",
            )

        _json = response.json()

        # Process each organization in this page
        for org in _json["data"]:
            _process_organization(org)
            all_organizations.append(OrganizationResponse(**org))

        # Check for next page
        current_url = None
        if "links" in _json and "next" in _json["links"]:
            current_url = _json["links"]["next"]

    # Return all organizations with updated pagination info
    return OrganizationListResponse(
        data=all_organizations, pagination={"total": len(all_organizations)}, links={}
    )


async def _get_memberships_by_body_id(
    http_client: httpx.Client, body_id: str | int
) -> MembershipListResponse:
    """Helper function to get memberships by body ID from the OParl API."""
    _url = "https://www.bonn.sitzung-online.de/public/oparl/memberships"

    if not isinstance(body_id, str):
        body_id = str(body_id)

    response = http_client.get(_url + f"?body={body_id}")
    if response.status_code == 200:
        _json = response.json()

        # check if the object has deleted = True aka not found
        for membership in _json["data"]:
            membership["person_ref"] = (
                membership["person"] if "person" in membership else None
            )
            membership["person_ref"] = membership["person_ref"].replace(
                UPSTREAM_API_URL, SELF_API_URL
            )
            membership["person"] = None
            membership["organization_ref"] = (
                membership["organization"] if "organization" in membership else None
            )
            membership["organization_ref"] = membership["organization_ref"].replace(
                UPSTREAM_API_URL, SELF_API_URL
            )
            membership["organization"] = None

        return MembershipListResponse(**_json)

    raise HTTPException(
        status_code=500,
        detail=f"Failed to fetch memberships with body ID {body_id} from OParl API",
    )


async def _get_meeting_by_id(
    http_client: httpx.Client, meeting_id: str | int
) -> MeetingResponse:
    """Helper function to get a meeting by ID from the OParl API."""
    _url = UPSTREAM_API_URL + f"/meetings?id={meeting_id}"

    response = http_client.get(_url, timeout=10.0)
    if response.status_code == 200:
        _json = response.json()

        # check if the object has deleted = True aka not found
        if _json.get("deleted", False):
            raise HTTPException(
                status_code=404,
                detail=f"Meeting with ID {meeting_id} not found in OParl API",
            )

        # rewrite the organization URLs
        if "organization" in _json:
            _json["organizations_ref"] = _json["organization"]
            _json["organizations_ref"] = [
                org_url.replace(UPSTREAM_API_URL, SELF_API_URL)
                for org_url in _json["organizations_ref"]
            ]
        else:
            _json["organizations_ref"] = None
        _json["organization"] = None

        return MeetingResponse(**_json)

    raise HTTPException(
        status_code=500,
        detail=f"Failed to fetch meeting with ID {meeting_id} from OParl API",
    )


async def _get_meetings_by_organization_id(
    http_client: httpx.Client, organization_id: str | int
) -> MeetingListResponse:
    """Helper function to get meetings by organization ID from the OParl API."""
    _url = UPSTREAM_API_URL + "/meetings"

    if not isinstance(organization_id, str):
        organization_id = str(organization_id)

    response = http_client.get(_url + f"?organization={organization_id}", timeout=35.0)
    if response.status_code == 200:
        _json = response.json()

        for meeting in _json["data"]:
            meeting["organizations_ref"] = [
                org_url.replace(UPSTREAM_API_URL, SELF_API_URL)
                for org_url in meeting["organization"]
            ]
            meeting["organization"] = None

            location_ref = (
                meeting["location"].replace(UPSTREAM_API_URL, SELF_API_URL)
                if "location" in meeting
                else None
            )
            meeting["location_ref"] = location_ref
            meeting["location"] = None

        return MeetingListResponse(**_json)

    elif response.status_code == 404:
        raise HTTPException(
            status_code=404,
            detail=f"No meetings found for organization ID {organization_id}",
        )
    raise HTTPException(
        status_code=500,
        detail=f"Failed to fetch meetings with organization ID {organization_id} from OParl API",
    )


async def _get_paper_by_id(
    http_client: httpx.Client, paper_id: str | int
) -> PaperResponse:
    """Helper function to get a paper by ID from the OParl API."""
    _url = UPSTREAM_API_URL + f"/papers?id={paper_id}"

    response = http_client.get(_url, timeout=10.0)
    if response.status_code == 200:
        _json = response.json()

        # check if the object has deleted = True aka not found
        if _json.get("deleted", False):
            raise HTTPException(
                status_code=404,
                detail=f"Paper with ID {paper_id} not found in OParl API",
            )

        _process_paper(_json)
        return PaperResponse(**_json)

    raise HTTPException(
        status_code=500,
        detail=f"Failed to fetch paper with ID {paper_id} from OParl API",
    )


def _process_paper(paper: dict) -> None:
    """Helper function to process paper data by converting URLs."""
    # Process reference fields to convert URLs from upstream to self API
    paper["body_ref"] = paper.get("body", None)
    if paper["body_ref"]:
        paper["body_ref"] = paper["body_ref"].replace(UPSTREAM_API_URL, SELF_API_URL)
    paper["body"] = None

    # Process relatedPapers
    if "relatedPaper" in paper and paper["relatedPaper"]:
        paper["relatedPapers_ref"] = [
            url.replace(UPSTREAM_API_URL, SELF_API_URL) for url in paper["relatedPaper"]
        ]
    else:
        paper["relatedPapers_ref"] = None
    paper["relatedPaper"] = None

    # Process superordinatedPaper
    paper["superordinatedPaper_ref"] = paper.get("superordinatedPaper", None)
    if paper["superordinatedPaper_ref"]:
        paper["superordinatedPaper_ref"] = paper["superordinatedPaper_ref"].replace(
            UPSTREAM_API_URL, SELF_API_URL
        )
    paper["superordinatedPaper"] = None

    # Process subordinatedPaper
    if "subordinatedPaper" in paper and paper["subordinatedPaper"]:
        paper["subordinatedPaper_ref"] = [
            url.replace(UPSTREAM_API_URL, SELF_API_URL)
            for url in paper["subordinatedPaper"]
        ]
    else:
        paper["subordinatedPaper_ref"] = None
    paper["subordinatedPaper"] = None

    # Process mainFile - could be an object with id field or a string
    if "mainFile" in paper and paper["mainFile"]:
        if isinstance(paper["mainFile"], dict) and "id" in paper["mainFile"]:
            paper["mainFile_ref"] = paper["mainFile"]["id"].replace(
                UPSTREAM_API_URL, SELF_API_URL
            )
            paper["mainFileAccessUrl"] = paper["mainFile"].get("accessUrl", None)
            paper["mainFileFilename"] = paper["mainFile"].get("fileName", None)
        elif isinstance(paper["mainFile"], str):
            paper["mainFile_ref"] = paper["mainFile"].replace(
                UPSTREAM_API_URL, SELF_API_URL
            )
        else:
            paper["mainFile_ref"] = None
    else:
        paper["mainFile_ref"] = None
    paper["mainFile"] = None

    # Process auxilaryFile
    if "auxilaryFile" in paper and paper["auxilaryFile"]:
        paper["auxilaryFiles_ref"] = [
            url.replace(UPSTREAM_API_URL, SELF_API_URL) for url in paper["auxilaryFile"]
        ]
    else:
        paper["auxilaryFiles_ref"] = None
    paper["auxilaryFile"] = None

    # Process location - convert list to list of refs
    if "location" in paper and paper["location"]:
        if isinstance(paper["location"], list):
            paper["location_ref"] = [
                url.replace("https://www.bonn.sitzung-online.de/public", SELF_API_URL)
                for url in paper["location"]
            ]
        elif isinstance(paper["location"], str):
            paper["location_ref"] = [
                paper["location"].replace(
                    "https://www.bonn.sitzung-online.de/public", SELF_API_URL
                )
            ]
        else:
            paper["location_ref"] = None
    else:
        paper["location_ref"] = None
    paper["location"] = None

    # Process originatorPerson - convert list to list of refs
    if "originatorPerson" in paper and paper["originatorPerson"]:
        if isinstance(paper["originatorPerson"], list):
            paper["originatorPerson_ref"] = [
                url.replace(UPSTREAM_API_URL, SELF_API_URL)
                for url in paper["originatorPerson"]
            ]
        elif isinstance(paper["originatorPerson"], str):
            paper["originatorPerson_ref"] = [
                paper["originatorPerson"].replace(UPSTREAM_API_URL, SELF_API_URL)
            ]
        else:
            paper["originatorPerson_ref"] = None
    else:
        paper["originatorPerson_ref"] = None
    paper["originatorPerson"] = None

    # Process underDirectionOf - convert list to list of refs
    if "underDirectionOf" in paper and paper["underDirectionOf"]:
        if isinstance(paper["underDirectionOf"], list):
            paper["underDirectionOfPerson_ref"] = [
                url.replace(UPSTREAM_API_URL, SELF_API_URL)
                for url in paper["underDirectionOf"]
            ]
        elif isinstance(paper["underDirectionOf"], str):
            paper["underDirectionOfPerson_ref"] = [
                paper["underDirectionOf"].replace(UPSTREAM_API_URL, SELF_API_URL)
            ]
        else:
            paper["underDirectionOfPerson_ref"] = None
    else:
        paper["underDirectionOfPerson_ref"] = None
    paper["underDirectionOf"] = None

    # Process originatorOrganization - convert to list of refs
    if "originatorOrganization" in paper and paper["originatorOrganization"]:
        if isinstance(paper["originatorOrganization"], list):
            paper["originatorOrganization_ref"] = [
                url.replace(UPSTREAM_API_URL, SELF_API_URL)
                for url in paper["originatorOrganization"]
            ]
        elif isinstance(paper["originatorOrganization"], str):
            paper["originatorOrganization_ref"] = [
                paper["originatorOrganization"].replace(UPSTREAM_API_URL, SELF_API_URL)
            ]
        else:
            paper["originatorOrganization_ref"] = None
    else:
        paper["originatorOrganization_ref"] = None
    paper["originatorOrganization"] = None

    # Process consultation - list of objects with id fields
    if "consultation" in paper and paper["consultation"]:
        paper["consultation_ref"] = []
        for consultation in paper["consultation"]:
            if isinstance(consultation, dict) and "id" in consultation:
                paper["consultation_ref"].append(
                    consultation["id"].replace(UPSTREAM_API_URL, SELF_API_URL)
                )
            elif isinstance(consultation, str):
                paper["consultation_ref"].append(
                    consultation.replace(UPSTREAM_API_URL, SELF_API_URL)
                )
    else:
        paper["consultation_ref"] = None
    paper["consultation"] = None


async def _get_papers_all(
    http_client: httpx.Client,
    page: int = 1,
    page_size: int = 10,
) -> PaperListResponse:
    """Helper function to get papers from the OParl API with pagination support."""
    _url = "https://www.bonn.sitzung-online.de/public/oparl/papers"

    # Build query parameters for pagination
    params = f"?page={page}&pageSize={page_size}"
    request_url = _url + params

    response = http_client.get(request_url, timeout=10.0)
    if response.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch papers from OParl API",
        )

    _json = response.json()

    # Process each paper in this page
    for paper in _json["data"]:
        _process_paper(paper)

    # Convert pagination links to use localhost URLs if they exist
    links = _json.get("links", {})
    converted_links = {}

    for link_name, link_url in links.items():
        if link_url:
            # Replace the upstream domain with localhost but keep the path and query params
            converted_links[link_name] = link_url.replace(
                "https://www.bonn.sitzung-online.de/public/oparl/papers",
                f"{SELF_API_URL}/papers",
            )
        else:
            converted_links[link_name] = link_url

    return PaperListResponse(
        data=[PaperResponse(**paper) for paper in _json["data"]],
        pagination=_json.get("pagination", {}),
        links=converted_links,
    )


async def _get_file_by_id(
    http_client: httpx.Client, file_id: str | int
) -> FileResponse:
    """Helper function to get a file by ID from the OParl API."""
    _url = UPSTREAM_API_URL + f"/files?id={file_id}&dtyp=130"

    response = http_client.get(_url, timeout=10.0)
    if response.status_code == 200:
        _json = response.json()

        # check if the object has deleted = True aka not found
        if _json.get("deleted", False):
            raise HTTPException(
                status_code=404,
                detail=f"File with ID {file_id} not found in OParl API",
            )

        # Process reference fields to convert URLs from upstream to self API
        # Process agendaItem references
        if "agendaItem" in _json and _json["agendaItem"]:
            _json["agendaItem_ref"] = [
                url.replace(UPSTREAM_API_URL, SELF_API_URL)
                for url in _json["agendaItem"]
            ]
        else:
            _json["agendaItem_ref"] = None
        _json["agendaItem"] = None

        # Process meeting reference
        _json["meeting_ref"] = _json.get("meeting", None)
        if _json["meeting_ref"]:
            _json["meeting_ref"] = _json["meeting_ref"].replace(
                UPSTREAM_API_URL, SELF_API_URL
            )
        _json["meeting"] = None

        # Process paper reference
        _json["paper_ref"] = _json.get("paper", None)
        if _json["paper_ref"]:
            _json["paper_ref"] = _json["paper_ref"].replace(
                UPSTREAM_API_URL, SELF_API_URL
            )
        _json["paper"] = None

        return FileResponse(**_json)

    raise HTTPException(
        status_code=500,
        detail=f"Failed to fetch file with ID {file_id} from OParl API",
    )
