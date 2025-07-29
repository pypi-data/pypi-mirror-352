import enum
from pathlib import Path
from typing import List

from loguru import logger
from pydantic import BaseModel, DirectoryPath


class ListOfPapersCategory(str, enum.Enum):
    """Enumeration for the categories of papers."""

    unconverted = "unconverted"
    converted = "converted"


class ListOfPapers(BaseModel):
    """Model to represent a list of papers."""

    category: ListOfPapersCategory
    papers: List[Path]


def unconverted_papers(data_path: DirectoryPath) -> ListOfPapers:
    """Find all unconverted papers in the specified directory."""
    unconverted_papers = ListOfPapers(
        category=ListOfPapersCategory.unconverted, papers=[]
    )

    # for each subdirectory in data_path
    for subdir in data_path.iterdir():
        if subdir.is_dir():
            # check if a PDF is present
            pdf_files = list(subdir.glob("*.pdf"))
            if pdf_files:
                # check if the is a coresponding Markdown file
                md_files = list(subdir.glob("*.md"))
                if not md_files:
                    unconverted_papers.papers.append(pdf_files[0])

    if unconverted_papers:
        logger.debug(f"Found {len(unconverted_papers.papers)} unconverted papers.")

    return unconverted_papers
