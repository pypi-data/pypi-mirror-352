import logfire
from cyclopts import App
from loguru import logger
from pydantic import DirectoryPath

from stadt_bonn_oparl.api.client import OParlAPIClient
from stadt_bonn_oparl.processors import download_oparl_pdfs

download = App(name="download", help="Download OPARL artifacts")


@download.command(name="paper")
def download_paper(
    data_path: DirectoryPath,
    start_page: int = 1,
    max_pages: int = 2,
    api_base_url: str = "http://localhost:8000",
) -> bool:
    """
    Process OParl data and download PDFs via API server.

    Parameters
    ----------
    data_path: DirectoryPath
        Path to the directory where OParl data will be saved.
    start_page: int
        The page number to start downloading from.
    max_pages: int
        The maximum number of pages to download.
    api_base_url: str
        Base URL of the local API server.
    """
    logger.info("Starting OParl data processing via API server...")

    logger.debug(
        f"Downloading OParl data via API server {api_base_url}, starting at page {start_page} and ending after {max_pages} pages at {start_page+max_pages}..."
    )

    with OParlAPIClient(api_base_url) as client:
        # Check if API server is accessible
        if not client.health_check():
            logger.error(
                f"API server at {api_base_url} is not accessible. Please ensure the server is running."
            )
            return False

        with logfire.span(f"downloading OParl data via API server {api_base_url}"):
            total_downloads, actual_pdfs, html_pages = download_oparl_pdfs(
                client,
                start_page=start_page,
                max_pages=max_pages,
                data_path=data_path,
            )

    logger.info(
        f"OParl processing finished. Downloaded {total_downloads} files: "
        f"{actual_pdfs} actual PDFs, {html_pages} HTML pages"
    )

    if html_pages > 0 and actual_pdfs == 0:
        logger.warning(
            "No actual PDFs were downloaded. The documents appear to be behind an authentication wall. "
            "You may need to obtain access credentials to download the actual PDFs."
        )

    return True
