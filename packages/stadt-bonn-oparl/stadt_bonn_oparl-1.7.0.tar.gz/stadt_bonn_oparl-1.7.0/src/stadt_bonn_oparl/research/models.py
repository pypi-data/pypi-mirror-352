"""Pydantic models for research results."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field



class EventType(str, Enum):
    """Types of events in the timeline."""

    PAPER_SUBMITTED = "paper_submitted"
    MEETING_DISCUSSED = "meeting_discussed"
    DECISION_MADE = "decision_made"
    CONSULTATION_OPENED = "consultation_opened"
    AMENDMENT_PROPOSED = "amendment_proposed"
    IMPLEMENTATION_STARTED = "implementation_started"
    OUTCOME_REPORTED = "outcome_reported"


class ImpactLevel(str, Enum):
    """Impact level of events."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DocumentType(str, Enum):
    """Types of documents in the system."""

    PAPER = "paper"
    MEETING_PROTOCOL = "meeting_protocol"
    AGENDA_ITEM = "agenda_item"
    CONSULTATION = "consultation"
    AMENDMENT = "amendment"


class PersonReference(BaseModel):
    """Reference to a person."""

    id: str
    name: str
    role: Optional[str] = None


class OrganizationReference(BaseModel):
    """Reference to an organization."""

    id: str
    name: str
    type: Optional[str] = None


class DateRange(BaseModel):
    """Date range for time-based queries."""

    start_date: datetime
    end_date: datetime


class ResearchScope(BaseModel):
    """Scope parameters for research queries."""

    time_period: Optional[DateRange] = None
    document_types: List[DocumentType] = Field(default_factory=list)
    include_meetings: bool = True
    include_stakeholders: bool = True
    max_documents: int = 50


class KeyFinding(BaseModel):
    """A key finding from the research."""

    title: str
    description: str
    significance: ImpactLevel
    evidence: List[str] = Field(default_factory=list)
    confidence_score: float = Field(ge=0.0, le=1.0)


class TimelineEvent(BaseModel):
    """Represents a significant event in topic development."""

    date: datetime
    event_type: EventType
    document_id: str
    title: str
    description: str
    outcome: Optional[str] = None
    participants: List[PersonReference] = Field(default_factory=list)
    impact_level: ImpactLevel


class PersonInvolvement(BaseModel):
    """A person's involvement in a topic."""

    person: PersonReference
    roles: List[str] = Field(default_factory=list)
    contributions: List[str] = Field(default_factory=list)
    involvement_level: ImpactLevel


class OrganizationInvolvement(BaseModel):
    """An organization's involvement in a topic."""

    organization: OrganizationReference
    involvement_type: str
    level: ImpactLevel
    key_activities: List[str] = Field(default_factory=list)


class StakeholderAnalysis(BaseModel):
    """Analysis of people and organizations involved in topic."""

    key_persons: List[PersonInvolvement] = Field(default_factory=list)
    organizations: List[OrganizationInvolvement] = Field(default_factory=list)
    influence_network: Dict[str, List[str]] = Field(default_factory=dict)
    decision_makers: List[PersonReference] = Field(default_factory=list)
    advocacy_groups: List[str] = Field(default_factory=list)


class DocumentAnalysis(BaseModel):
    """Analysis of documents related to a topic."""

    total_documents: int
    document_types: Dict[DocumentType, int] = Field(default_factory=dict)
    key_documents: List[Dict[str, Any]] = Field(default_factory=list)
    trends: List[str] = Field(default_factory=list)


class SourceSummary(BaseModel):
    """Summary of data sources used."""

    total_sources: int
    oparl_documents: int
    vector_db_results: int
    external_sources: int = 0
    data_quality_score: float = Field(ge=0.0, le=1.0)


class ComprehensiveResearchResult(BaseModel):
    """Main result object for comprehensive topic research."""

    subject: str
    research_timestamp: datetime
    research_scope: ResearchScope

    # Analysis Results
    executive_summary: str
    key_findings: List[KeyFinding] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    stakeholder_analysis: StakeholderAnalysis
    document_analysis: DocumentAnalysis

    # Meta Information
    confidence_score: float = Field(ge=0.0, le=1.0)
    data_completeness: float = Field(ge=0.0, le=1.0)
    limitations: List[str] = Field(default_factory=list)
    source_summary: SourceSummary


class MeetingMetadata(BaseModel):
    """Metadata about a meeting."""

    id: str
    date: datetime
    title: str
    organization: OrganizationReference
    participants: List[PersonReference] = Field(default_factory=list)


class AgendaItemAnalysis(BaseModel):
    """Analysis of a single agenda item."""

    id: str
    title: str
    discussion_summary: str
    outcome: Optional[str] = None
    related_papers: List[str] = Field(default_factory=list)
    key_speakers: List[PersonReference] = Field(default_factory=list)


class Decision(BaseModel):
    """A decision made in a meeting."""

    agenda_item_id: str
    decision_type: str
    outcome: str
    voting_result: Optional[Dict[str, Any]] = None
    implementation_notes: Optional[str] = None


class VotingAnalysis(BaseModel):
    """Analysis of voting patterns."""

    total_votes: int
    voting_breakdown: Dict[str, int] = Field(default_factory=dict)
    controversial_items: List[str] = Field(default_factory=list)
    consensus_items: List[str] = Field(default_factory=list)


class ActionItem(BaseModel):
    """A follow-up action from a meeting."""

    description: str
    responsible_party: Optional[PersonReference] = None
    deadline: Optional[datetime] = None
    status: str


class MeetingAnalysisResult(BaseModel):
    """Result of meeting-specific analysis."""

    meeting_metadata: MeetingMetadata
    agenda_analysis: List[AgendaItemAnalysis] = Field(default_factory=list)
    decisions_made: List[Decision] = Field(default_factory=list)
    discussion_summary: str
    voting_patterns: Optional[VotingAnalysis] = None
    follow_up_actions: List[ActionItem] = Field(default_factory=list)


class EvolutionPhase(BaseModel):
    """A phase in topic evolution."""

    period: DateRange
    phase_name: str
    description: str
    key_events: List[TimelineEvent] = Field(default_factory=list)
    activity_level: ImpactLevel


class TrendAnalysis(BaseModel):
    """Analysis of trends over time."""

    trend_direction: str  # "increasing", "decreasing", "stable", "cyclical"
    trend_strength: float = Field(ge=0.0, le=1.0)
    peak_periods: List[DateRange] = Field(default_factory=list)
    low_periods: List[DateRange] = Field(default_factory=list)
    notable_changes: List[str] = Field(default_factory=list)


class Pattern(BaseModel):
    """A pattern identified in the data."""

    pattern_type: str
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[str] = Field(default_factory=list)


class Prediction(BaseModel):
    """A prediction about future developments."""

    prediction: str
    confidence: float = Field(ge=0.0, le=1.0)
    timeframe: str
    basis: List[str] = Field(default_factory=list)


class TopicEvolutionResult(BaseModel):
    """Result of temporal topic analysis."""

    topic: str
    analysis_period: DateRange
    evolution_timeline: List[EvolutionPhase] = Field(default_factory=list)
    trend_analysis: TrendAnalysis
    pattern_recognition: List[Pattern] = Field(default_factory=list)
    future_predictions: List[Prediction] = Field(default_factory=list)
