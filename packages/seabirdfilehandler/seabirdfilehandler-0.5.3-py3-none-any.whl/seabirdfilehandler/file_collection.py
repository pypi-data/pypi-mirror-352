from pathlib import Path
import logging
from collections import UserList
from typing import Callable, Type
import pandas as pd
import numpy as np
from seabirdfilehandler import (
    CnvFile,
    BottleFile,
    BottleLogFile,
)
from seabirdfilehandler import DataFile
from seabirdfilehandler.utils import get_unique_sensor_data

logger = logging.getLogger(__name__)


class FileCollection(UserList):
    """A representation of multiple files of the same kind. These files share
    the same suffix and are otherwise closely connected to each other. A common
    use case would be the collection of CNVs to allow for easier processing or
    integration of field calibration measurements.

    Parameters
    ----------

    Returns
    -------

    """

    def __init__(
        self,
        path_to_files: str | Path,
        file_suffix: str,
        only_metadata: bool = False,
        sorting_key: Callable | None = None,
    ):
        super().__init__()
        self.path_to_files = Path(path_to_files)
        self.file_suffix = file_suffix.strip(".")
        self.file_type: Type[DataFile]
        self.extract_file_type()
        self.individual_file_paths = []
        self.collect_files(sorting_key=sorting_key)
        self.load_files(only_metadata)
        if not only_metadata:
            if self.file_type == DataFile:
                self.df_list = self.get_dataframes()
                self.df = self.get_collection_dataframe(self.df_list)
            if self.file_type == CnvFile:
                self.data_meta_info = self.get_data_table_meta_info()
            self.sensor_data = get_unique_sensor_data(
                [file.sensors for file in self.data]
            )

    def __str__(self):
        return "/n".join(self.data)

    def extract_file_type(self):
        """ """
        mapping_suffix_to_type = {
            "cnv": CnvFile,
            "btl": BottleFile,
            "bl": BottleLogFile,
        }
        for key, value in mapping_suffix_to_type.items():
            if key == self.file_suffix:
                self.file_type = value
                break
            else:
                self.file_type = DataFile

    def collect_files(
        self,
        sorting_key: Callable | None = lambda file: int(
            file.stem.split("_")[3]
        ),
    ):
        """ """
        self.individual_file_paths = sorted(
            self.path_to_files.rglob(f"*{self.file_suffix}"),
            key=sorting_key,
        )

    def load_files(self, only_metadata: bool = False):
        """ """
        for file in self.individual_file_paths:
            try:
                self.data.append(self.file_type(file))
            except TypeError:
                logger.error(
                    f"Could not open file {file} with the type "
                    f"{self.file_type}."
                )
                continue

    def get_dataframes(
        self,
        event_log: bool = False,
        coordinates: bool = False,
        time_correction: bool = False,
        cast_identifier: bool = False,
        long_header_names: bool = False,
        full_data_header: bool = True,
    ) -> list[pd.DataFrame]:
        """

        Parameters
        ----------
        event_log: bool :
             (Default value = False)
        coordinates: bool :
             (Default value = False)
        time_correction: bool :
             (Default value = False)
        cast_identifier: bool :
             (Default value = False)
        long_header_names: bool :
             (Default value = False)
        full_data_header: bool :
             (Default value = True)

        Returns
        -------

        """
        for index, file in enumerate(self.data):
            if full_data_header:
                file.rename_dataframe_header(header_detail_level="longinfo")
            elif long_header_names:
                file.rename_dataframe_header(header_detail_level="name")
            if event_log:
                file.add_station_and_event_column()
            if coordinates:
                file.add_position_columns()
            if time_correction:
                file.absolute_time_calculation()
                file.add_start_time()
            if cast_identifier:
                file.add_cast_number(index + 1)
        return [file.df for file in self.data]

    def get_collection_dataframe(
        self, list_of_dfs: list[pd.DataFrame] | None = None
    ) -> pd.DataFrame:
        """

        Parameters
        ----------
        list_of_dfs: list[pd.DataFrame] | None :
             (Default value = None)

        Returns
        -------

        """
        if not list_of_dfs:
            list_of_dfs = self.get_dataframes()
        df = pd.concat(list_of_dfs, ignore_index=True)
        # df.meta.metadata = list_of_dfs[0].meta.metadata
        return df

    def tidy_collection_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """

        Parameters
        ----------
        df: pd.DataFrame :


        Returns
        -------

        """
        df = self.use_bad_flag_for_nan(df)
        df = self.set_dtype_to_float(df)
        return self.select_real_scan_data(df)

    def use_bad_flag_for_nan(self, df: pd.DataFrame) -> pd.DataFrame:
        """

        Parameters
        ----------
        df: pd.DataFrame :


        Returns
        -------

        """
        bad_flags = set()
        for file in self.data:
            for line in file.data_table_description:
                if line.startswith("bad_flag"):
                    flag = line.split("=")[1].strip()
                    bad_flags.add(flag)
        for flag in bad_flags:
            df.replace(to_replace=flag, value=np.nan, inplace=True)
        return df

    def set_dtype_to_float(self, df: pd.DataFrame) -> pd.DataFrame:
        """

        Parameters
        ----------
        df: pd.DataFrame :


        Returns
        -------

        """
        for parameter in df.columns:
            if parameter in ["datetime"]:
                continue
            try:
                df[parameter] = df[parameter].astype("float")
            finally:
                continue
        return df

    def select_real_scan_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """

        Parameters
        ----------
        df: pd.DataFrame :


        Returns
        -------

        """
        # TODO: fix this hardcoded name
        try:
            df = df.loc[df["Scan Count"].notna()]
        finally:
            pass
        return df

    def to_csv(self, file_name):
        """

        Parameters
        ----------
        file_name :


        Returns
        -------

        """
        self.get_collection_dataframe().to_csv(file_name)

    def get_data_table_meta_info(self) -> list[list[dict]]:
        """ """
        return [file.parameters.metadata for file in self.data]
