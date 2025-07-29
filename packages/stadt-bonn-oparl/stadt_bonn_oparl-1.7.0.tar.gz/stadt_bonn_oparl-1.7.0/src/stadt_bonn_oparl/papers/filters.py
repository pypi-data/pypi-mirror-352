import csv
import json
from pathlib import Path

from loguru import logger


def filter_analysis_attributes(
    data_path: Path, save_path: Path, attributes: list[str], save_as_csv: bool = False
) -> int:
    analysis_files = list(data_path.glob("**/analysis.json"))

    if save_as_csv:
        _save_path = str(save_path.with_suffix(".csv"))
    else:
        _save_path = str(save_path)

    # remove 'title' and 'date' from attributes, as we include them anytime
    attributes = [attr for attr in attributes if attr not in ["title", "date"]]

    if not analysis_files:
        logger.info("No analysis files found.")
        return 0

    filtered_data = []
    for analysis_file in analysis_files:
        with open(analysis_file, "r", encoding="utf-8") as file:
            data = json.load(file)
            _title = ""

            # get the original title from the metadata file
            with open(
                analysis_file.parent / "metadata.json", "r", encoding="utf-8"
            ) as file:
                meta_data = json.load(file)
                _title = meta_data.get("name")
                _date = meta_data.get("date")

            _filtered_data = {
                "title": _title,
                "date": _date,
            }

            # include the specified attributes
            for attr in attributes:
                if attr in data:
                    _filtered_data[attr] = data[attr]

            filtered_data.append(_filtered_data)

    # write the filtered data to the specified file
    if save_as_csv:
        with open(_save_path, mode="w") as file:
            fieldnames = ["title", "date"] + attributes
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter="|")

            writer.writeheader()
            for row in filtered_data:
                writer.writerow(row)
    else:
        with open(_save_path, "w") as file:
            json.dump(filtered_data, file, ensure_ascii=False, indent=2)

    logger.debug(f"Filtered data saved to {_save_path}.")

    return len(filtered_data)
