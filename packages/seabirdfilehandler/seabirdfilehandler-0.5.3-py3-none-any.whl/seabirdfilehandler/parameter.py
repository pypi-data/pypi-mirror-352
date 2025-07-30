from __future__ import annotations
from typing import Tuple
import re
from collections import UserDict
import numpy as np
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class Parameters(UserDict):
    """
    A collection of all the parameters in a CnvFile.

    Allows for a much cleaner handling of parameter data and their metadata.
    Will be heavily expanded.

    Parameters
    ----------
    data: list
        The raw data as extraced by DataFile
    metadata: list
        The raw metadata as extraced by DataFile

    Returns
    -------

    """

    def __init__(
        self,
        data: list,
        metadata: list,
    ):
        self.raw_input_data = data
        self.raw_metadata = metadata
        self.full_data_array = self.create_full_ndarray()
        self.differentiate_table_description()
        self.metadata, self.duplicate_columns = self.reading_data_header(
            metadata
        )
        self.data = self.create_parameter_instances()

    def get_parameter_names(self) -> list[str]:
        return [parameter["name"] for parameter in self.metadata.values()]

    def get_parameter_list(self) -> list[Parameter]:
        """ """
        return list(self.data.values())

    def create_full_ndarray(self, data_table: list = []) -> np.ndarray:
        """
        Builds a numpy array representing the data table in a cnv file.

        Parameters
        ----------
        data_table: list :
            The data to work with
             (Default value = [])

        Returns
        -------
        A numpy array of the same shape as the cnv files data table

        """
        data_table = (
            self.raw_input_data if len(data_table) == 0 else data_table
        )
        n = 11
        row_list = []
        for line in data_table:
            row_list.append(
                [
                    line[i : i + n].split()[0]
                    for i in range(0, len(line) - n, n)
                ]
            )
        return np.array(row_list, dtype=float)

    def create_parameter_instances(
        self,
        metadata: dict[str, dict] = {},
    ) -> dict[str, Parameter]:
        """
        Differentiates the individual parameter columns into separate parameter
        instances.

        Parameters
        ----------
        metadata: dict[str, dict] :
            The structured metadata dictionary
             (Default value = {})

        Returns
        -------
        A dictionary of parameter instances

        """
        metadata = (
            self.metadata if len(list(metadata.keys())) == 0 else metadata
        )
        parameter_dict = {}
        list_of_metadata_shortnames = list(metadata.keys())
        if self.full_data_array.shape[1] != len(list_of_metadata_shortnames):
            raise AssertionError(
                f"Array column width {
                    self.full_data_array.shape[1]
                } does not fit metadata length {len(metadata)}"
            )
        for i in range(self.full_data_array.shape[1]):
            column_data = self.full_data_array[:, i]
            key = list_of_metadata_shortnames[i]
            parameter_dict[key] = Parameter(
                data=column_data, metadata=metadata[key]
            )
        return parameter_dict

    def _form_data_table_info(self) -> list:
        """Recreates the data table descriptions, like column names and spans
        from the structured dictionaries these values were stored in."""
        new_table_info = []
        for key, value in self.data_table_stats.items():
            new_table_info.append(f"{key} = {value}\n")
        for index, (name, _) in enumerate(self.data_table_names_and_spans):
            new_table_info.append(f"name {index} = {name}\n")
        for index, (_, span) in enumerate(self.data_table_names_and_spans):
            new_table_info.append(f"span {index} = {span}\n")
        for key, value in self.data_table_misc.items():
            new_table_info.append(f"{key} = {value}\n")
        return new_table_info

    def differentiate_table_description(self):
        """
        The original method that structures data table metadata.

        Needs heavy refactoring.
        """
        past_spans = False
        pre = []
        column_names = []
        column_value_spans = []
        post = []
        for line in self.raw_metadata:
            if line.startswith("name"):
                column_names.append(line.split("=")[1].strip())
            elif line.startswith("span"):
                past_spans = True
                column_value_spans.append(line.split("=")[1].strip())
            else:
                if not past_spans:
                    pre.append(line)
                else:
                    post.append(line)
        assert len(column_names) == len(column_value_spans)
        self.data_table_stats = {
            line.split("=")[0].strip(): line.split("=")[1].strip()
            for line in pre
        }
        self.data_table_names_and_spans = [
            (name, span)
            for name, span in zip(column_names, column_value_spans)
        ]
        self.data_table_misc = {
            line.split("=")[0].strip(): line.split("=")[1].strip()
            for line in post
        }

    def add_parameter(self, parameter: Parameter):
        """
        Adds one parameter instance to the collection.

        Parameters
        ----------
        parameter: Parameter :
            The new parameter

        """
        self.data[parameter.name] = parameter

    def create_parameter(
        self,
        data: np.ndarray | int | float | str,
        metadata: dict = {},
        name: str = "",
    ) -> Parameter:
        """
        Creates a new parameter instance with the given data and metadata.

        The input data is either a numpy array or a single value. The single
        value will be broadcasted to the shape of the data table. A use-case
        would be the addition of an 'event' or 'cast' column.

        Parameters
        ----------
        data: np.ndarray | int | float | str :
            Data to use or expand

        metadata: dict :
            Metadata for the new parameter
             (Default value = {})
        name: str :
            Name to use for missing metadata values
             (Default value = "")

        Returns
        -------
        The new parameter instance

        """
        if len(metadata) < 5:
            if len(name) > 0:
                metadata = self.add_default_metadata(
                    name=name, metadata=metadata
                )
            else:
                raise ValueError(
                    "Please specify either a name or sufficient metadata"
                )
        if not isinstance(data, np.ndarray):
            data = np.full(
                fill_value=data,
                shape=self.full_data_array.shape[0],
            )
        parameter = Parameter(data=data, metadata=metadata)
        self.add_parameter(parameter)
        return parameter

    def add_default_metadata(
        self,
        name: str,
        metadata: dict = {},
        list_of_keys: list = [
            "shortname",
            "longinfo",
            "name",
            "metainfo",
            "unit",
        ],
    ) -> dict:
        """
        Fills up missing metadata points with a default value.

        Parameters
        ----------
        name: str :
            The value to use as default
        metadata: dict :
            The present metadata
             (Default value = {})
        list_of_keys: list :
             The expected metadata keys

        Returns
        -------
        The full metadata dictionary

        """
        default = {}
        for key in list_of_keys:
            if key not in list(metadata.keys()):
                if key in ["metainfo", "unit"]:
                    default[key] = ""
                default[key] = name
        return {**metadata, **default}

    def update_spans(self):
        """Updates all spans of the parameters."""
        for parameter in self.get_parameter_list():
            parameter.update_span()

    def get_spans(self) -> list[tuple[int, int]]:
        """Returns all span tuples of the parameters."""
        # update spans first
        self.update_spans()
        return [parameter.span for parameter in self.get_parameter_list()]

    def get_pandas_dataframe(self) -> pd.DataFrame:
        """Returns a pandas DataFrame of the current parameter data."""
        data = np.array(
            [parameter.data for parameter in self.get_parameter_list()]
        ).T
        columns = [parameter.name for parameter in self.get_parameter_list()]
        assert data.shape[1] == len(columns)
        df = pd.DataFrame(data=data, columns=columns)
        for column in df.columns:
            if column.lower() not in [
                "latitude",
                "longitude",
                "event",
                "cast",
                "flag",
            ]:
                df[column].astype("float64")
        return df

    def with_name_type(self, name_type: str = "shortname"):
        """
        Uses the given name_type as column descriptors.

        Parameters
        ----------
        name_type: str :
            The metadata name to use
             (Default value = "shortname")

        """
        for parameter in self.get_parameter_list():
            parameter.use_name(name_type)

    def reading_data_header(
        self, header_info: list = []
    ) -> Tuple[dict[str, dict], list[int]]:
        """Reads the tables header data from the header.

        Parameters
        ----------
        header_info : list:
            the header values from the file
        header_info: list :
             (Default value = [])

        Returns
        -------


        """
        if len(header_info) == 0:
            header_info = self.raw_metadata
        table_header = {}
        duplicate_columns = []
        for line in header_info:
            if line.startswith("name"):
                header_meta_info = {}
                # get basic shortname and the full, non-differentiated info
                shortname = longinfo = line_info = line.split("=")[1].strip()
                try:
                    shortname, longinfo = line_info.split(":")
                except IndexError:
                    pass
                finally:
                    shortname = shortname.strip()
                    if shortname in list(table_header.keys()):
                        try:
                            duplicate_columns.append(
                                int(line.split("=")[0].strip().split()[1])
                            )
                        except IndexError as error:
                            logger.error(
                                f"Could not resolve duplicate column: {
                                    shortname
                                }, {error}"
                            )
                    else:
                        header_meta_info["shortname"] = shortname
                        header_meta_info["longinfo"] = longinfo.strip()
                        metainfo = self._extract_data_header_meta_info(
                            longinfo.strip()
                        )
                        header_meta_info = {**header_meta_info, **metainfo}
                        table_header[shortname.strip()] = header_meta_info
        return table_header, duplicate_columns

    def _extract_data_header_meta_info(self, line: str) -> dict:
        """Extracts the individual information bits inside of the header lines

        Parameters
        ----------
        line : str:
            one header line, trimmed by the 'name =' prefix and the shortname
        line: str :


        Returns
        -------


        """
        regex_string = r"(?:(?P<name0>.+),\s(?P<metainfo0>.+)\s\[(?P<unit0>.+)\]|(?P<name2>.+)\s\[(?P<unit2>.+)\]|(?P<name3>.+),\s(?P<metainfo2>.[^\s]+)|(?P<name4>.+))"
        regex_check = re.search(regex_string, line, flags=re.IGNORECASE)
        if regex_check:
            regex_info = dict(regex_check.groupdict())
            regex_info = {
                key[:-1]: value
                for key, value in regex_info.items()
                if value is not None
            }
            if len(regex_info) > 2:
                # check for second sensors and adjust their names
                if regex_info["metainfo"][-1] == "2":
                    regex_info["name"] = regex_info["name"] + " 2"
                    regex_info["metainfo"] = regex_info["metainfo"][:-1]
                    if len(regex_info["metainfo"]) == 0:
                        regex_info.pop("metainfo")
            if regex_info["name"] == "flag":
                regex_info["metainfo"] = regex_info["name"]
                regex_info["unit"] = regex_info["name"]
            return regex_info
        return {}


class Parameter:
    """A representation of one parameter in a cnv file.

    Consists of the values of the parameter as well as the metadata.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(
        self,
        data: np.ndarray,
        metadata: dict,
    ) -> None:
        self.data = data
        self.metadata = metadata
        self.name = metadata["shortname"]
        self.update_span()

    def __str__(self) -> str:
        return str(self.metadata["longinfo"])

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other) -> bool:
        return self.data == other.data

    def get_pandas_series(self) -> pd.Series:
        """Returns a pandas Series of the current parameter data."""
        return pd.Series(data=self.data, name=self.name)

    def use_name(self, name_type: str = "shortname"):
        """
        Uses the given name as parameter descriptor.

        Parameters
        ----------
        name_type: str :
            The metadata name to use
             (Default value = "shortname")

        """
        try:
            self.name = self.metadata[name_type]
        except KeyError:
            return

    def update_span(self):
        """
        Updates the data span.

        Uses the first value if dtype is not numeric.
        """
        if self.data.dtype in ["float64", "int"]:
            self.span = (self.data.min(), self.data.max())
        else:
            self.span = (self.data[0], self.data[0])
