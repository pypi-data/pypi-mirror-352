import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel


class OParlPerson(BaseModel):
    id: str
    name: str
    familyName: Optional[str] = None
    givenName: Optional[str] = None
    formOfAdress: Optional[str] = None
    affix: Optional[str] = None
    gender: Optional[str] = None
    location: Optional["OParlLocation"] = (
        None  # see that quotes? https://docs.pydantic.dev/latest/concepts/forward_annotations/
    )
    status: Optional[List[str]] = None
    membership: Optional[List["OParlMembership"]] = None
    web: Optional[str] = None


class OParlFile(BaseModel):
    """Model for a file in the OParl API."""

    id: str
    name: str
    fileName: Optional[str] = None  # e.g. "document.pdf"
    mimeType: Optional[str] = None  # e.g. "application/pdf"
    date: Optional[datetime.datetime] = None  # Date of the file
    size: Optional[int] = None  # Size in bytes

    sha1Checksum: Optional[str] = None  # SHA1 checksum of the file
    sha512Checksum: Optional[str] = None  # SHA512 checksum of the file
    text: Optional[str] = None  # Text content of the file, if applicable

    accessUrl: str  # URL to access the file
    downloadUrl: Optional[str] = None  # URL to download the file

    fileLicense: Optional[str] = None  # License information for the file

    meeting: Optional[List[str]] = (
        None  # URL to the meeting this file is associated with
    )
    agendaItem: Optional[List[str]] = (
        None  # URL to the agenda item this file is associated with
    )
    paper: Optional[List[str]] = None  # URL to the paper this file is associated with

    license: Optional[str] = None  # License information for the file
    keyword: Optional[List[str]] = None  # Keywords associated with the file
    web: Optional[str] = None  # URL to open in a web browser for more information


class OParlLocation(BaseModel):
    """Dieser Objekttyp dient dazu, einen Ortsbezug formal abzubilden. Ortsangaben können sowohl aus Textinformationen
    bestehen (beispielsweise dem Namen einer Straße/eines Platzes oder eine genaue Adresse) als auch aus Geodaten.
    Ortsangaben sind auch nicht auf einzelne Positionen beschränkt, sondern können eine Vielzahl von Positionen,
    Flächen, Strecken etc. abdecken.

    see https://oparl.org/spezifikation/online-ansicht/#entity-location
    """

    id: str
    description: Optional[str] = None  # e.g. "Rathaus Bonn"
    streetAddress: Optional[str] = None  # e.g. "Markt 1"
    room: Optional[str] = None  # e.g. "Rathaus, Raum 101"
    postalCode: Optional[str] = None  # e.g. "53111"
    subLocality: Optional[str] = None  # e.g. "Altstadt"
    locality: Optional[str] = None  # e.g. "Bonn"
    bodies: Optional[List[str]] = (
        None  # List of body URLs this location is associated with
    )
    organizations: Optional[List[str]] = (
        None  # List of organization URLs this location is associated with
    )
    persons: Optional[List[str]] = (
        None  # List of person URLs this location is associated with
    )
    meetings: Optional[List[str]] = (
        None  # List of meeting URLs this location is associated with
    )
    papers: Optional[List[str]] = (
        None  # List of paper URLs this location is associated with
    )
    license: Optional[str] = None  # License information for the location
    keyword: Optional[List[str]] = None  # Keywords associated with the location
    web: Optional[str] = None  # URL to open in a web browser for more information
    geojson: Optional[dict] = None  # GeoJSON representation of the location


class OParlOrganizationType(str, Enum):
    """Enum for organization types in OParl.

    see https://oparl.org/spezifikation/online-ansicht/#entity-organization"""

    AMT = "Amt"
    EXTERNES_GREMIUM = "Externes Gremium"
    FRAKTION = "Fraktion"
    GREMIUM = "Gremium"
    HAUPTORGAN = "Hauptorgan"
    HILFSORGAN = "Hilfsorgan"
    INSTITUTION = "Institution"
    PARTEI = "Partei"
    VERWALTUNGSBEREICH = "Verwaltungsbereich"

    SONSTIGES = "Sonstiges"


class OParlOrganization(BaseModel):
    """Dieser Objekttyp dient dazu, eine Organisation formal abzubilden. Eine Organisation ist ein Zusammenschluss von
    Personen, die gemeinsam eine Aufgabe erfüllen. Dies kann beispielsweise ein Ausschuss, eine Fraktion oder eine
    Verwaltungseinheit sein. Organisationen können auch hierarchisch strukturiert sein, z.B. eine Fraktion kann
    mehrere Ausschüsse haben.

    see https://oparl.org/spezifikation/online-ansicht/#entity-organization
    """

    id: str  # e.g. "https://oparl.bonn.de/organization/id=123"
    name: str  # e.g. "Fraktion B"
    shortName: Optional[str] = None  # e.g. "FrB"
    organizationType: OParlOrganizationType  # Grobe Kategorisierung der Gruppierung.
    classification: str
    web: Optional[str] = None  # URL to open in a web browser for more information
    location: Optional[OParlLocation] = None
    meeting: Optional[str] = (
        None  # this is a URL to query for the meetings references by this organization
    )
    membership: Optional[List["OParlMembership"]] = None
    startDate: Optional[datetime.date] = None
    endDate: Optional[datetime.date] = None


class OParlAgendaItem(BaseModel):
    id: str  # Unique identifier for the agenda item
    meeting: Optional[str] = None  # The meeting this agenda item belongs to
    number: Optional[str]  # Gliederungsnummer
    order: int  # Order of the agenda item in the meeting
    name: Optional[str] = None  # Name of the agenda item
    public: Optional[bool] = True  # Indicates if the agenda item is public
    consultation: Optional[str] = (
        None  # URL to Consultation information for the agenda item
    )
    result: Optional[str] = None  # URL to Result information for the agenda item
    resolutionText: Optional[str] = None  # Text of the resolution for the agenda item
    resolutionFile: Optional[dict] = (
        None  # File containing the resolution for the agenda item
    )
    auxiliaryFile: Optional[List[dict]] = (
        None  # List of auxiliary files related to the agenda item
    )
    start: Optional[datetime.datetime] = None  # Start time of the agenda item
    end: Optional[datetime.datetime] = None  # End time of the agenda item
    license: Optional[str] = None  # License information for the agenda item
    keyword: Optional[List[str]] = None  # Keywords associated with the agenda item
    web: Optional[str] = None  # URL to open in a web browser for more information

    def get_all_files(self) -> List[OParlFile]:
        """Get all files associated with this agenda item."""
        files = []

        if self.resolutionFile:
            files.append(OParlFile(**self.resolutionFile))

        if self.auxiliaryFile:
            for file_dict in self.auxiliaryFile:
                files.append(OParlFile(**file_dict))

        return files

    def download_all_files(
        self, data_path: Optional[Path] = None
    ) -> List[tuple[OParlFile, bool]]:
        """Download all files associated with this agenda item.

        Args:
            data_path: Path to save downloaded files. Uses DEFAULT_DATA_PATH if None.

        Returns:
            List of tuples containing (OParlFile, success_status)
        """
        from .config import DEFAULT_DATA_PATH
        from .utils import download_file, sanitize_name

        if data_path is None:
            data_path = DEFAULT_DATA_PATH

        # Create agenda item directory
        agenda_dir_name = sanitize_name(
            f"agenda_item_{self.id.split('/')[-1] if '/' in self.id else self.id}"
        )
        if self.name:
            agenda_dir_name += f"_{sanitize_name(self.name)}"

        agenda_dir = data_path / agenda_dir_name
        agenda_dir.mkdir(parents=True, exist_ok=True)

        results = []
        files = self.get_all_files()

        for file_obj in files:
            if file_obj.accessUrl:
                # Create safe filename
                filename = file_obj.fileName or file_obj.name or "file"
                safe_filename = sanitize_name(filename)
                download_path = agenda_dir / safe_filename

                # Download the file
                success, _ = download_file(
                    file_obj.accessUrl,
                    download_path,
                    item_title=f"File '{file_obj.name}' from agenda item",
                    check_pdf=True,
                )
                results.append((file_obj, success))

        return results


class OParlMeeting(BaseModel):
    """Dieser Objekttyp dient der Abbildung von Sitzungen in der parlamentarischen Arbeit. Sitzungen sind formelle
    Zusammenkünfte von Gruppierungen zu einem bestimmten Zeitpunkt an einem bestimmten Ort. Sie können Tagesordnungspunkte
    enthalten, die wiederum Drucksachen (oparl:Paper) behandeln. Sitzungen können öffentlich oder nicht-öffentlich sein und
    können verschiedene Status haben, wie geplant, verschoben, abgesagt oder abgeschlossen.

    Siehe https://oparl.org/spezifikation/online-ansicht/#entity-meeting
    """

    id: str
    name: str
    meetingState: str  # e.g. "scheduled", "postponed", "cancelled", "finished"
    cancelled: Optional[bool] = False  # Indicates if the meeting was cancelled
    start: Optional[datetime.datetime] = None  # Start date of the meeting
    end: Optional[datetime.datetime] = None  # End date of the meeting
    location: Optional[OParlLocation] = None  # Location of the meeting
    organization: Optional[List[OParlOrganization]] = (
        None  # Organization hosting the meeting
    )
    participants: Optional[List[OParlPerson]] = (
        None  # List of participants in the meeting
    )
    invitation: Optional[OParlFile] = None  # The invitation document
    resultsProtocol: Optional[OParlFile] = None  # The results protocol document
    verbatimProtocol: Optional[OParlFile] = None  # The verbatim protocol document
    auxiliaryFile: Optional[List[OParlFile]] = (
        None  # List of auxiliary files related to the meeting
    )
    agendaItem: Optional[List[OParlAgendaItem]] = (
        None  # List of agenda items for the meeting
    )
    license: Optional[str] = None  # License information for the meeting
    keyword: Optional[List[str]] = None  # Keywords associated with the meeting
    web: Optional[str] = None  # URL to open in a web browser for more information


class OParlMembership(BaseModel):
    id: str
    person: Optional[OParlPerson] = None
    organization: Optional[OParlOrganization] = None
    role: str
    votingRight: bool
    startDate: datetime.date
    endDate: Optional[datetime.date] = None


class OParlPaper(BaseModel):
    """Dieser Objekttyp dient der Abbildung von Drucksachen in der parlamentarischen Arbeit, wie zum Beispiel
    Anfragen, Anträgen und Beschlussvorlagen. Drucksachen werden in Form einer Beratung (oparl:Consultation) im
    Rahmen eines Tagesordnungspunkts (oparl:AgendaItem) einer Sitzung (oparl:Meeting) behandelt.

    Drucksachen spielen in der schriftlichen wie mündlichen Kommunikation eine besondere Rolle, da in vielen Texten auf
    bestimmte Drucksachen Bezug genommen wird. Hierbei kommen in parlamentarischen Informationssystemen in der Regel
    unveränderliche Kennungen der Drucksachen zum Einsatz.

    see https://oparl.org/spezifikation/online-ansicht/#entity-paper
    """

    id: str
    body: Optional[str] = None  # Körperschaft, zu der die Drucksache gehört.
    name: Optional[str] = (
        None  # Name der Drucksache, z.B. "Antrag zur Förderung von Radwegen"
    )
    reference: str  # Eindeutige Kennung der Drucksache, z.B. "Drucksache 123/2023"
    date: datetime.date  # Datum der Einreichung der Drucksache, z.B. "2023-10-01"
    paperType: Optional[str] = (
        None  # Typ der Drucksache, z.B. "Antrag", "Anfrage", "Bericht"
    )
    relatedPaper: Optional[List["OParlPaper"]] = (
        None  # Referenzen zu verwandten Drucksachen, z.B. "Drucksache 456/2023"
    )
    superordinatedPaper: Optional[List["OParlPaper"]] = (
        None  # Referenz zu einer übergeordneten Drucksache, falls vorhanden
    )
    subordinatedPaper: Optional[List["OParlPaper"]] = (
        None  # Referenzen zu untergeordneten Drucksachen, falls vorhanden
    )
    mainFile: Optional[OParlFile] = (
        None  # Hauptdokument der Drucksache, z.B. "Drucksache 123/2023.pdf"
    )
    auxilaryFile: Optional[List[OParlFile]] = (
        None  # Zusätzliche Dateien zur Drucksache, z.B. "Drucksache 123/2023-Anhang.pdf"
    )
    location: Optional[List[OParlLocation]] = (
        None  # Ort, an dem die Drucksache eingereicht wurde, z.B. "Bonn"
    )
    originatorPerson: Optional[List[OParlPerson]] = (
        None  # Personen, die die Drucksache eingereicht haben, z.B. "Max Mustermann"
    )
    underDirectionOf: Optional[List[OParlOrganization]] = (
        None  # Organisationen, die die Drucksache betreuen, z.B. "Fraktion B"
    )
    originatorOrganization: Optional[List[OParlOrganization]] = (
        None  # Organisationen, die die Drucksache eingereicht haben, z.B. "Fraktion B"
    )
    consultation: Optional[List[str]] = None  # Beratungen der Drucksache.

    license: Optional[str] = None  # Lizenzinformationen zur Drucksache
    keyword: Optional[List[str]] = (
        None  # Schlagwörter zur Drucksache, z.B. "Radverkehr", "Förderung"
    )
    web: Optional[str] = (
        None  # URL zur Drucksache im Web, z.B. "https://www.bonn.de/drucksache/123/2023"
    )
