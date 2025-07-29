from pathlib import Path
from typing import Annotated

from cyclopts import App, Parameter
from pydantic import DirectoryPath, NewPath

from stadt_bonn_oparl.papers.filters import filter_analysis_attributes

filter = App("filter", help="Filter some of the fields available in OParl Papers.")


@filter.command(
    name="analysis", help="Filter some attributes out of the analysis files."
)
def analysis(
    data_path: DirectoryPath,
    save_path: NewPath = Path("filtered.json"),
    attributes: Annotated[
        list[str], Parameter(help="Input filename(s)", consume_multiple=True)
    ] = ["title", "date"],
    save_as_csv: bool = False,
):
    """
    Filter some attributes out of the analysis files in data-path.

    Parameters
    ----------
    data_path: DirectoryPath
        The path to the directory to search for failed downloads.
    save_path: FilePath
        The path to the file where the filtered data shall be saved to.
    save_as_csv: bool
        Save the filtered data as CSV, if no not set, it will be saved as JSON
    """

    filter_analysis_attributes(data_path, save_path, attributes, save_as_csv)
