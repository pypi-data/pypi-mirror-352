import json
from pathlib import Path

import logfire
from loguru import logger
from pydantic import DirectoryPath, FilePath

from .api.client import OParlAPIClient
from .utils import download_file, sanitize_name

logfire.instrument_requests()


def download_oparl_pdfs(
    client: OParlAPIClient,
    data_path: Path,
    start_page: int = 1,
    max_pages: int = 5,
):
    """
    Download PDFs from the OParl API via local API server.

    Note: Many document servers require authentication. This function will
    detect if the downloaded files are actual PDFs or HTML login pages.

    Args:
        client: The OParl API client instance
        data_path: Path to save downloaded files
        start_page: Starting page number
        max_pages: Maximum number of pages to fetch
        state_file: Optional path to a state file

    Returns:
        tuple: (Number of files downloaded, Number of actual PDF files, Number of HTML files)
    """
    logger.info(f"Starting OParl PDF download via API server: {client.base_url}")

    total_downloaded = 0
    actual_pdfs = 0
    html_pages = 0
    authentication_warnings_shown = False
    more_pages = True

    # if start_page is not 1, calculate the page number
    page = start_page
    _max_pages = max_pages + start_page

    if data_path is None:
        logger.error("No data path provided.")
        return total_downloaded, actual_pdfs, html_pages

    while more_pages and page <= _max_pages:
        with logfire.span(f"Fetching OParl data from page {page}"):
            # Fetch papers for current page
            papers_data = client.get_papers(page=page)
            if not papers_data:
                logger.error(f"Failed to fetch papers data from page {page}")
                break

            papers = papers_data.get("data", [])
            if not papers:
                logger.info(f"No papers found on page {page}")
                break

            # Process each paper
            for paper in papers:
                paper.get("id", "").split("/")[-1] if paper.get("id") else None
                paper_name = paper.get("name", "Unknown")
                paper_date = paper.get("date", paper.get("publishedDate", ""))
                paper_reference = paper.get("reference", "")

                # Create a sanitized name for the file
                file_prefix = ""
                if paper_date:
                    file_prefix += f"{paper_date} "
                if paper_reference:
                    file_prefix += f"{paper_reference} "

                paper_dir_name = sanitize_name(f"{file_prefix}{paper_name}")
                paper_dir = data_path / paper_dir_name
                paper_dir.mkdir(parents=True, exist_ok=True)

                # Save metadata
                try:
                    metadata_path = paper_dir / "metadata.json"
                    with open(metadata_path, "w", encoding="utf-8") as f:
                        json.dump(paper, f, ensure_ascii=False, indent=2)
                    logger.debug(f"Saved metadata for {paper_name} to {metadata_path}")
                except Exception as e:
                    logger.error(f"Failed to save metadata for {paper_name}: {e}")

                # Download main file (PDF)
                if paper.get("mainFileAccessUrl"):
                    pdf_url = paper.get("mainFileAccessUrl")
                    file_name = paper.get("mainFileFilename", "document.pdf")
                    download_path = paper_dir / sanitize_name(file_name)

                    # Check if the file already exists
                    if download_path.exists():
                        logger.info(f"File already exists: {download_path}")
                        continue

                    success, content_type = download_file(
                        pdf_url,
                        download_path,
                        item_title=f"PDF for '{paper_name}'",
                        check_pdf=True,
                    )

                    if success:
                        total_downloaded += 1
                        if content_type == "pdf":
                            actual_pdfs += 1
                        elif content_type == "html":
                            html_pages += 1
                            if not authentication_warnings_shown:
                                logger.warning(
                                    "Some documents require authentication. Downloaded files may be login pages instead of PDFs."
                                )
                                authentication_warnings_shown = True

                # Download auxiliary files if present
                aux_files = paper.get("auxiliaryFile", [])
                if isinstance(aux_files, list) and aux_files:
                    aux_dir = paper_dir / "attachments"
                    aux_dir.mkdir(parents=True, exist_ok=True)

                    for aux_file in aux_files:
                        if isinstance(aux_file, dict) and aux_file.get("accessUrl"):
                            aux_url = aux_file["accessUrl"]
                            aux_name = aux_file.get("fileName", "attachment.pdf")
                            aux_path = aux_dir / sanitize_name(aux_name)

                            success, content_type = download_file(
                                aux_url,
                                aux_path,
                                item_title=f"Attachment for '{paper_name}'",
                                check_pdf=True,
                            )

                            if success:
                                total_downloaded += 1
                                if content_type == "pdf":
                                    actual_pdfs += 1
                                elif content_type == "html":
                                    html_pages += 1

        # Check if there are more pages
        links = papers_data.get("links", {})
        if links and links.get("next"):
            page += 1
        else:
            more_pages = False

    logger.info(
        f"Finished downloading {total_downloaded} files from OParl API: "
        f"{actual_pdfs} actual PDFs, {html_pages} HTML pages, "
        f"{total_downloaded - actual_pdfs - html_pages} other files"
    )

    if html_pages > 0:
        logger.warning(
            "Most downloaded files are HTML instead of PDFs. The documents are likely "
            "behind an authentication wall. Check a sample file to confirm."
        )

    return total_downloaded, actual_pdfs, html_pages


def convert_oparl_pdf(file_path: FilePath, data_path: DirectoryPath) -> bool:
    """
    Convert a PDF file to Docling format.

    Args:
        file_path (FilePath): Path to the PDF file

    Returns:
        bool: True if conversion is successful, False otherwise
    """
    output_dir = data_path
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{file_path.stem}.md"
    docling_path = output_dir / f"{file_path.stem}.docling"
    json_path = output_dir / f"{file_path.stem}.json"

    # check if all of the files already exist, if so: return
    if output_path.exists() and docling_path.exists() and json_path.exists():
        logger.debug(
            f"All converted files for {file_path} already exist. Skipping conversion."
        )
        return True

    with logfire.span(f"converting OParl PDF {file_path}"):
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import (
            AcceleratorDevice,
            AcceleratorOptions,
            PdfPipelineOptions,
        )
        from docling.document_converter import DocumentConverter, PdfFormatOption

        logger.info(f"Converting file: {file_path}")
        if not file_path.suffix == ".pdf":
            logger.error(f"{file_path} is not a PDF. Skipping conversion.")
            return False

        with logfire.suppress_instrumentation():
            pipeline_options = PdfPipelineOptions()
            pipeline_options.do_ocr = False
            pipeline_options.accelerator_options = AcceleratorOptions(
                num_threads=12, device=AcceleratorDevice.AUTO
            )

            converter = DocumentConverter(
                format_options={
                    InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
                }
            )

            doc = converter.convert(file_path).document

        # TODO maybe we should check if the file already exist?!
        try:
            with logfire.suppress_instrumentation():
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(doc.export_to_markdown())

                doc.save_as_doctags(docling_path)
                doc.save_as_json(json_path)
        except Exception as e:
            logger.error(f"Failed to save converted document: {e}")
            return False

    return True
