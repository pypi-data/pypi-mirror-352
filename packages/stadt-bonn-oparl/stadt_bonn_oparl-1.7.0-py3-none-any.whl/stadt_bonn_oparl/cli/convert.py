from cyclopts import App
from loguru import logger
from pydantic import DirectoryPath, FilePath

from stadt_bonn_oparl.processors import convert_oparl_pdf


convert = App(
    name="convert", help="Convert OPARL Papers PDF to Markdown and Docling format"
)


@convert.command(name=["paper", "papers"])
def convert_paper(
    data_path: DirectoryPath | FilePath,
    from_file: FilePath | None = None,
    all: bool = False,
) -> bool:
    """
    Convert an OPARL Papers PDF to Markdown and Docling format.
    This function processes a single PDF file or all PDFs in the specified directory.

    If `from_file` is provided, it reads the list of PDFs to be converted from that file,
    otherwise, it processes the PDF provided as a single file at `data_path` or all PDFs
    in the specified directory will be converted.

    Parameters
    ----------
    data_path: DirectoryPath | FilePath
        Path to the directory containing OPARL Papers in PDF file
    from_file: FilePath
        Path to the file from which the list of PDFs to be converted will be read.
    all: bool
        If True, convert all PDFs in the directory

    Returns
    -------
        bool: True if conversion is successful, False otherwise
    """
    logger.debug("Starting OParl data conversion...")

    papers = None

    if from_file:
        # read the file into ListOfPapers
        from stadt_bonn_oparl.papers.find import ListOfPapers

        with open(from_file, "r", encoding="utf-8") as file:
            try:
                papers = ListOfPapers.model_validate_json(file.read()).papers
            except Exception as e:
                logger.error(f"Failed to read from file {from_file}: {e}")
                return False

    if all:
        # Assuming convert_oparl_pdf saves to CONVERTED_DATA_DIRECTORY
        papers = data_path.glob("**/*.pdf")
    else:
        if not data_path.is_file() or not data_path.suffix == ".pdf":
            logger.error("The provided path is not a PDF file.")
            return False

        papers = [data_path]

    if papers:
        for pdf_file in papers:
            if not pdf_file.is_file() or pdf_file.suffix != ".pdf":
                logger.error(f"Skipping non-PDF file: {pdf_file}")
                continue

            logger.debug(f"Converting PDF file: {pdf_file}")
            convert_oparl_pdf(pdf_file, data_path=pdf_file.parent)

    logger.debug("OParl data conversion completed.")

    return True
