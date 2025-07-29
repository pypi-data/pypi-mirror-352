"""Research command for stakeholder analysis and topic research."""

import asyncio
import json
from typing import Annotated

import cyclopts
import logfire

from ..research.service import ResearchService


def research_stakeholders(
    topic: Annotated[str, cyclopts.Parameter(help="Research topic to analyze")],
    max_meetings: Annotated[int, cyclopts.Parameter(help="Maximum meetings to analyze")] = 20,
    output_format: Annotated[str, cyclopts.Parameter(help="Output format: json or summary")] = "summary",
):
    """Analyze stakeholders for a specific research topic.

    This command finds meetings related to the topic and constructs a stakeholder map
    showing key persons, organizations, and their relationships.

    Args:
        topic: The research topic (e.g., "Radverkehr", "Klimaschutz", "Digitalisierung")
        max_meetings: Maximum number of meetings to analyze
        output_format: Output format - "json" for full JSON or "summary" for human-readable
    """
    logfire.info(f"Starting stakeholder analysis for topic: {topic}")
    
    async def _analyze():
        # Initialize research service
        research_service = ResearchService()
        
        # Analyze stakeholders
        stakeholder_analysis = await research_service.analyze_stakeholders_for_topic(
            topic, max_meetings
        )
        return stakeholder_analysis
    
    try:
        stakeholder_analysis = asyncio.run(_analyze())
        
        if output_format == "json":
            # Output full JSON
            print(json.dumps(stakeholder_analysis.model_dump(), indent=2, default=str))
        else:
            # Output human-readable summary
            print(f"\n🔍 Stakeholder Analysis for '{topic}'")
            print("=" * 50)
            
            print(f"\n👥 Key Persons ({len(stakeholder_analysis.key_persons)}):")
            for person in stakeholder_analysis.key_persons[:5]:  # Show top 5
                print(f"  • {person.person.name}")
                if person.person.role:
                    print(f"    Role: {person.person.role}")
                print(f"    Involvement: {person.involvement_level.value}")
                if person.contributions:
                    print(f"    Recent: {person.contributions[-1]}")
                print()
            
            print(f"\n🏢 Organizations ({len(stakeholder_analysis.organizations)}):")
            for org in stakeholder_analysis.organizations[:5]:  # Show top 5
                print(f"  • {org.organization.name}")
                if org.organization.type:
                    print(f"    Type: {org.organization.type}")
                print(f"    Level: {org.level.value}")
                if org.key_activities:
                    print(f"    Recent: {org.key_activities[-1]}")
                print()
            
            print(f"\n🤝 Decision Makers ({len(stakeholder_analysis.decision_makers)}):")
            for dm in stakeholder_analysis.decision_makers[:3]:  # Show top 3
                print(f"  • {dm.name} ({dm.role})")
            
            print(f"\n📢 Advocacy Groups ({len(stakeholder_analysis.advocacy_groups)}):")
            for group in stakeholder_analysis.advocacy_groups[:3]:  # Show top 3
                print(f"  • {group}")
            
            if stakeholder_analysis.influence_network:
                print("\n🌐 Influence Network:")
                for key, connections in list(stakeholder_analysis.influence_network.items())[:3]:
                    print(f"  • {key} → {', '.join(connections[:3])}")
            
            print(f"\n✅ Analysis completed - found stakeholders from {max_meetings} meetings")
        
    except Exception as e:
        logfire.error(f"Stakeholder analysis failed: {e}")
        print(f"❌ Error: {e}")
        raise


def research_topic(
    subject: Annotated[str, cyclopts.Parameter(help="Topic to research")],
    max_meetings: Annotated[int, cyclopts.Parameter(help="Maximum meetings to include")] = 20,
    include_stakeholders: Annotated[bool, cyclopts.Parameter(help="Include stakeholder analysis")] = True,
    output_format: Annotated[str, cyclopts.Parameter(help="Output format: json or summary")] = "summary",
):
    """Perform comprehensive research on a municipal topic.

    This command conducts a full analysis including document search, stakeholder mapping,
    and trend analysis for the specified topic.

    Args:
        subject: The topic to research
        max_meetings: Maximum meetings to analyze
        include_stakeholders: Whether to include stakeholder analysis
        output_format: Output format - "json" for full JSON or "summary" for human-readable
    """
    logfire.info(f"Starting comprehensive research for topic: {subject}")
    
    async def _research():
        # Initialize research service
        research_service = ResearchService()
        
        # Perform comprehensive research
        result = await research_service.research_topic_comprehensive(
            subject=subject,
            max_documents=50,
            include_meetings=True,
            include_stakeholders=include_stakeholders,
        )
        return result
    
    try:
        result = asyncio.run(_research())
        
        if output_format == "json":
            # Output full JSON
            print(json.dumps(result.model_dump(), indent=2, default=str))
        else:
            # Output human-readable summary
            print(f"\n📊 Comprehensive Research Report: '{subject}'")
            print("=" * 60)
            print(f"Generated: {result.research_timestamp}")
            print(f"Confidence: {result.confidence_score:.1%}")
            print(f"Data Completeness: {result.data_completeness:.1%}")
            
            print("\n📝 Executive Summary:")
            print(f"  {result.executive_summary}")
            
            print("\n📄 Document Analysis:")
            print(f"  • Total Documents: {result.document_analysis.total_documents}")
            for doc_type, count in result.document_analysis.document_types.items():
                if count > 0:
                    print(f"  • {doc_type.value}: {count}")
            
            if include_stakeholders and result.stakeholder_analysis.key_persons:
                print("\n👥 Key Stakeholders:")
                for person in result.stakeholder_analysis.key_persons[:3]:
                    print(f"  • {person.person.name} ({person.involvement_level.value})")
                
                if result.stakeholder_analysis.organizations:
                    print("\n🏢 Key Organizations:")
                    for org in result.stakeholder_analysis.organizations[:3]:
                        print(f"  • {org.organization.name} ({org.level.value})")
            
            print("\n📊 Data Sources:")
            print(f"  • OParl Documents: {result.source_summary.oparl_documents}")
            print(f"  • Vector DB Results: {result.source_summary.vector_db_results}")
            print(f"  • Quality Score: {result.source_summary.data_quality_score:.1%}")
            
            print("\n✅ Research completed successfully")
        
    except Exception as e:
        logfire.error(f"Topic research failed: {e}")
        print(f"❌ Error: {e}")
        raise