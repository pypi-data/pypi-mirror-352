from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging
from seabirdfilehandler import DataFile
from seabirdfilehandler.parameter import Parameters
from seabirdfilehandler.validation_modules import CnvValidationList

logger = logging.getLogger(__name__)


class CnvFile(DataFile):
    """
    A representation of a cnv-file as used by SeaBird.

    This class intends to fully extract and organize the different types of
    data and metadata present inside of such a file. Downstream libraries shall
    be able to use this representation for all applications concerning cnv
    files, like data processing, transformation or visualization.

    To achieve that, the metadata header is organized by the parent-class,
    DataFile, while the data table is extracted by this class. The data
    representation can be a numpy array or pandas dataframe. The handling of
    the data is mostly done inside parameters, a representation of the
    individual measurement parameter data and metadata.

    This class is also able to parse the edited data and metadata back to the
    original .cnv file format, allowing for custom data processing using this
    representation, while still being able to use Sea-Birds original software
    on that output. It also allows to stay comparable with other parsers or
    methods in general.

    Parameters
    ----------
    path_to_file: Path | str:
        the path to the file
    only_header: bool :
        Whether to stop reading the file after the metadata header.
    create_dataframe: bool :
        Whether to create a pandas DataFrame from the data table.
    absolute_time_calculation: bool:
        whether to use a real timestamp instead of the second count
    event_log_column: bool:
        whether to add a station and device event column from DSHIP
    coordinate_columns: bool:
        whether to add longitude and latitude from the extra metadata header

    """

    def __init__(
        self,
        path_to_file: Path | str,
        only_header: bool = False,
        create_dataframe: bool = False,
        absolute_time_calculation: bool = False,
        event_log_column: bool = False,
        coordinate_columns: bool = False,
    ):
        super().__init__(path_to_file, only_header)
        self.validation_modules = self.obtaining_validation_modules()
        self.start_time = self.reading_start_time()
        self.parameters = Parameters(self.data, self.data_table_description)
        if create_dataframe:
            self.df = self.parameters.get_pandas_dataframe()
        if absolute_time_calculation:
            self.absolute_time_calculation()
        if event_log_column:
            self.add_station_and_event_column()
        if coordinate_columns:
            self.add_position_columns()

    def reading_start_time(
        self,
        time_source: str = "System UTC",
    ) -> datetime | None:
        """
        Extracts the Cast start time from the metadata header.
        """
        for line in self.sbe9_data:
            if line.startswith(time_source):
                start_time = line.split("=")[1]
                start_time = datetime.strptime(
                    start_time, " %b %d %Y %H:%M:%S "
                )
                return start_time
        return None

    def absolute_time_calculation(self) -> bool:
        """
        Replaces the basic cnv time representation of counting relative to the
        casts start point, by real UTC timestamps.
        This operation will act directly on the dataframe.

        """
        time_parameter = None
        for parameter in self.df.columns:
            if parameter.lower().startswith("time"):
                time_parameter = parameter
        if time_parameter and self.start_time:
            self.parameters.create_parameter(
                name="datetime",
                data=np.array(
                    [
                        timedelta(days=float(time)) + self.start_time
                        if time_parameter == "timeJ"
                        else timedelta(seconds=float(time)) + self.start_time
                        for time in self.df[time_parameter]
                    ]
                ),
            )
            return True
        return False

    def add_start_time(self) -> bool:
        """
        Adds the Cast start time to the dataframe.
        Necessary for joins on the time.
        """
        if self.start_time:
            self.parameters.create_parameter(
                name="start_time",
                data=str(self.start_time),
            )
            return True
        return False

    def obtaining_validation_modules(self) -> CnvValidationList:
        """
        Collects the individual validation modules and their respective
        information, usually present in key-value pairs.
        """
        validation_modules = self.processing_info
        return CnvValidationList(validation_modules)

    def df2cnv(self, df: pd.DataFrame | None = None) -> list:
        """
        Parses a pandas dataframe into a list that represents the lines inside
        of a cnv data table.

        Parameters
        ----------
        df: DataFrame to export, default is self.df

        Returns
        -------
        a list of lines in the cnv data table format

        """
        df = df if isinstance(df, pd.DataFrame) else self.df
        cnv_out = []
        for _, row in df.iterrows():
            cnv_like_row = "".join(
                (lambda column: f"{str(column):>11}")(value) for value in row
            )
            cnv_out.append(cnv_like_row + "\n")
        return cnv_out

    def array2cnv(self) -> list:
        result = []
        for row in self.parameters.full_data_array:
            formatted_row = "".join(f"{elem:11}" for elem in row)
            result.append(formatted_row + "\n")
        return result

    def to_cnv(
        self,
        file_name: Path | str | None = None,
        use_dataframe: bool = True,
    ):
        """
        Writes the values inside of this instance as a new cnv file to disc.

        Parameters
        ----------
        file_name: Path:
            the new file name to use for writing
        use_current_df: bool:
            whether to use the current dataframe as data table
        use_current_validation_header: bool:
            whether to use the current processing module list
        header_list: list:
            the data columns to use for the export

        """
        file_name = self.path_to_file if file_name is None else file_name
        # content construction
        if use_dataframe:
            data = self.df2cnv()
        else:
            data = self.array2cnv()
        self._update_header()
        self.file_data = [*self.header, *data]
        # writing content out
        try:
            with open(file_name, "w", encoding="latin-1") as file:
                for line in self.file_data:
                    file.write(line)

        except IOError as error:
            logger.error(f"Could not write cnv file: {error}")

    def _update_header(self):
        """Re-creates the cnv header."""
        self.data_table_description = self.parameters._form_data_table_info()
        self.header = [
            *[f"* {data}" for data in self.sbe9_data[:-1]],
            *[f"** {data}" for data in self.metadata_list],
            f"* {self.sbe9_data[-1]}",
            *[f"# {data}" for data in self.data_table_description],
            *[f"# {data}" for data in self.sensor_data],
            *[f"# {data}" for data in self.processing_info],
            "*END*\n",
        ]

    def add_processing_metadata(self, addition: str | list):
        """
        Adds new processing lines to the list of processing module information

        Parameters
        ----------
        addition: str:
            the new information line

        """
        # TODO: use CnvprocessingList here
        if isinstance(addition, str):
            addition = [addition]
        for line in addition:
            self.file_data.append(line)
            # add the new info line *before* the 'file_type = ascii' line
            self.processing_info.insert(-1, line)

    def add_station_and_event_column(self) -> bool:
        """
        Adds a column with the DSHIP station and device event numbers to the
        dataframe. These must be present inside the extra metadata header.

        """
        if "Station" in self.metadata:
            self.parameters.create_parameter(
                data=self.metadata["Station"],
                name="Event",
            )
            return True
        return False

    def add_position_columns(self) -> bool:
        """
        Adds a column with the longitude and latitude to the dataframe.
        These must be present inside the extra metadata header.

        """
        if ("latitude" or "longitude") in [
            k.lower() for k in self.parameters.keys()
        ]:
            return True
        if ("GPS_Lat" and "GPS_Lon") in self.metadata:
            self.parameters.create_parameter(
                data=self.metadata["GPS_Lat"],
                name="Latitude",
            )
            self.parameters.create_parameter(
                data=self.metadata["GPS_Lon"],
                name="Longitude",
            )
            return True
        else:
            return False

    def add_cast_number(self, number: int | None = None) -> bool:
        """
        Adds a column with the cast number to the dataframe.

        Parameters
        ----------
        number: int:
            the cast number of this files cast

        """
        if ("Cast" in self.metadata.keys()) and (not number):
            number = int(self.metadata["Cast"])
        if number:
            self.parameters.create_parameter(
                data=number,
                name="Cast",
            )
            return True
        return False
