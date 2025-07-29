"""Stakeholder tracker for person and organization analysis."""

from collections import defaultdict
from typing import Dict, List, Set, Any

import logfire

from stadt_bonn_oparl.oparl_fetcher import get_oparl_list_data, get_oparl_data
from ..models import (
    StakeholderAnalysis,
    PersonReference,
    OrganizationReference,
    PersonInvolvement,
    OrganizationInvolvement,
    ImpactLevel,
)


class StakeholderTracker:
    """Tracker for stakeholder analysis across meetings and documents."""

    def __init__(self):
        """Initialize the stakeholder tracker."""
        self.person_cache: Dict[str, Dict[str, Any]] = {}
        self.organization_cache: Dict[str, Dict[str, Any]] = {}
        self.stakeholder_connections: Dict[str, Set[str]] = defaultdict(set)

    async def find_meetings_by_topic(self, topic: str, max_meetings: int = 20) -> List[Dict[str, Any]]:
        """Find meetings that touch on a specific research topic.

        Args:
            topic: The research topic to search for
            max_meetings: Maximum number of meetings to return

        Returns:
            List of meetings related to the topic
        """
        logfire.info(f"Searching for meetings related to topic: {topic}")
        
        try:
            # Get all meetings and filter by topic
            meetings = await get_oparl_list_data("/meetings", params={"limit": max_meetings * 2})
            if not meetings:
                return []

            topic_meetings = []
            for meeting in meetings:
                # Check if topic appears in meeting name or agenda items
                if self._meeting_matches_topic(meeting, topic):
                    topic_meetings.append(meeting)
                    if len(topic_meetings) >= max_meetings:
                        break

            logfire.info(f"Found {len(topic_meetings)} meetings related to '{topic}'")
            return topic_meetings

        except Exception as e:
            logfire.error(f"Failed to find meetings for topic '{topic}': {e}")
            return []

    def _meeting_matches_topic(self, meeting: Dict[str, Any], topic: str) -> bool:
        """Check if a meeting is related to the research topic.

        Args:
            meeting: Meeting data from OParl API
            topic: Topic to search for

        Returns:
            True if meeting is related to topic
        """
        topic_lower = topic.lower()
        
        # Check meeting name
        if meeting.get("name") and topic_lower in meeting["name"].lower():
            return True
            
        # Check agenda items if available
        agenda_items = meeting.get("agendaItem", [])
        for item in agenda_items:
            if isinstance(item, dict):
                if item.get("name") and topic_lower in item["name"].lower():
                    return True
                if item.get("text") and topic_lower in item["text"].lower():
                    return True

        return False

    async def extract_stakeholders_from_meetings(
        self, 
        meetings: List[Dict[str, Any]]
    ) -> StakeholderAnalysis:
        """Extract and analyze stakeholders from meeting data.

        Args:
            meetings: List of meeting data

        Returns:
            StakeholderAnalysis with identified stakeholders and relationships
        """
        logfire.info(f"Extracting stakeholders from {len(meetings)} meetings")
        
        person_involvement: Dict[str, PersonInvolvement] = {}
        org_involvement: Dict[str, OrganizationInvolvement] = {}
        decision_makers: List[PersonReference] = []
        influence_network: Dict[str, List[str]] = defaultdict(list)

        # Process each meeting
        for meeting in meetings:
            await self._process_meeting_stakeholders(
                meeting, person_involvement, org_involvement, decision_makers, influence_network
            )

        # Convert to final format
        key_persons = list(person_involvement.values())
        organizations = list(org_involvement.values())

        # Identify advocacy groups from organizations
        advocacy_groups = [
            org.organization.name for org in organizations 
            if "verein" in org.organization.name.lower() or "initiative" in org.organization.name.lower()
        ]

        return StakeholderAnalysis(
            key_persons=key_persons,
            organizations=organizations,
            influence_network=dict(influence_network),
            decision_makers=decision_makers,
            advocacy_groups=advocacy_groups,
        )

    async def _process_meeting_stakeholders(
        self,
        meeting: Dict[str, Any],
        person_involvement: Dict[str, PersonInvolvement],
        org_involvement: Dict[str, OrganizationInvolvement],
        decision_makers: List[PersonReference],
        influence_network: Dict[str, List[str]],
    ):
        """Process stakeholders from a single meeting.

        Args:
            meeting: Meeting data
            person_involvement: Dictionary to track person involvement
            org_involvement: Dictionary to track organization involvement
            decision_makers: List of decision makers
            influence_network: Network of influences between stakeholders
        """
        try:
            # Get meeting participants
            participants = meeting.get("participant", [])
            if isinstance(participants, str):
                # If it's a URL, fetch the data
                participants_data = await get_oparl_data(participants)
                if participants_data:
                    participants = participants_data if isinstance(participants_data, list) else [participants_data]
                else:
                    participants = []

            # Process participants
            for participant in participants:
                if isinstance(participant, str):
                    # Fetch person data if it's a URL
                    person_data = await get_oparl_data(participant)
                    if person_data:
                        await self._add_person_involvement(person_data, person_involvement, meeting)
                elif isinstance(participant, dict):
                    await self._add_person_involvement(participant, person_involvement, meeting)

            # Get organization from meeting
            organization_url = meeting.get("organization")
            if organization_url:
                org_data = await get_oparl_data(organization_url)
                if org_data:
                    await self._add_organization_involvement(org_data, org_involvement, meeting)

        except Exception as e:
            logfire.warning(f"Failed to process stakeholders for meeting {meeting.get('id', 'unknown')}: {e}")

    async def _add_person_involvement(
        self,
        person_data: Dict[str, Any],
        person_involvement: Dict[str, PersonInvolvement],
        meeting: Dict[str, Any],
    ):
        """Add or update person involvement data.

        Args:
            person_data: Person data from API
            person_involvement: Dictionary tracking person involvement
            meeting: Meeting context
        """
        person_id = person_data.get("id", "")
        if not person_id:
            return

        # Create person reference
        person_ref = PersonReference(
            id=person_id,
            name=person_data.get("name", "Unknown"),
            role=person_data.get("title", ""),
        )

        # Update or create involvement
        if person_id not in person_involvement:
            person_involvement[person_id] = PersonInvolvement(
                person=person_ref,
                roles=[],
                contributions=[],
                involvement_level=ImpactLevel.LOW,
            )

        involvement = person_involvement[person_id]
        
        # Add meeting participation
        meeting_title = meeting.get("name", "Unknown Meeting")
        involvement.contributions.append(f"Participated in: {meeting_title}")
        
        # Add role if available
        if person_data.get("title"):
            role = person_data["title"]
            if role not in involvement.roles:
                involvement.roles.append(role)

        # Update involvement level based on participation frequency
        if len(involvement.contributions) >= 3:
            involvement.involvement_level = ImpactLevel.HIGH
        elif len(involvement.contributions) >= 2:
            involvement.involvement_level = ImpactLevel.MEDIUM

    async def _add_organization_involvement(
        self,
        org_data: Dict[str, Any],
        org_involvement: Dict[str, OrganizationInvolvement],
        meeting: Dict[str, Any],
    ):
        """Add or update organization involvement data.

        Args:
            org_data: Organization data from API
            org_involvement: Dictionary tracking organization involvement
            meeting: Meeting context
        """
        org_id = org_data.get("id", "")
        if not org_id:
            return

        # Create organization reference
        org_ref = OrganizationReference(
            id=org_id,
            name=org_data.get("name", "Unknown Organization"),
            type=org_data.get("organizationType", ""),
        )

        # Update or create involvement
        if org_id not in org_involvement:
            org_involvement[org_id] = OrganizationInvolvement(
                organization=org_ref,
                involvement_type="meeting_host",
                level=ImpactLevel.MEDIUM,
                key_activities=[],
            )

        involvement = org_involvement[org_id]
        
        # Add meeting hosting
        meeting_title = meeting.get("name", "Unknown Meeting")
        activity = f"Hosted meeting: {meeting_title}"
        if activity not in involvement.key_activities:
            involvement.key_activities.append(activity)

        # Update level based on activity count
        if len(involvement.key_activities) >= 5:
            involvement.level = ImpactLevel.HIGH

    async def create_stakeholder_map(self, topic: str, max_meetings: int = 20) -> StakeholderAnalysis:
        """Create a comprehensive stakeholder map for a research topic.

        Args:
            topic: The research topic
            max_meetings: Maximum number of meetings to analyze

        Returns:
            StakeholderAnalysis with complete stakeholder mapping
        """
        logfire.info(f"Creating stakeholder map for topic: {topic}")
        
        # Find relevant meetings
        meetings = await self.find_meetings_by_topic(topic, max_meetings)
        
        if not meetings:
            logfire.warning(f"No meetings found for topic: {topic}")
            return StakeholderAnalysis()

        # Extract stakeholders from meetings
        stakeholder_analysis = await self.extract_stakeholders_from_meetings(meetings)
        
        logfire.info(
            f"Stakeholder map created: {len(stakeholder_analysis.key_persons)} persons, "
            f"{len(stakeholder_analysis.organizations)} organizations"
        )
        
        return stakeholder_analysis

    async def track_stakeholders(self, documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Track stakeholders across documents (legacy method for compatibility).

        Args:
            documents: List of documents to analyze for stakeholders

        Returns:
            Stakeholder analysis results
        """
        # For now, return a summary
        return {
            "stakeholder_count": len(documents),
            "analysis": f"Analyzed {len(documents)} documents for stakeholder patterns"
        }
