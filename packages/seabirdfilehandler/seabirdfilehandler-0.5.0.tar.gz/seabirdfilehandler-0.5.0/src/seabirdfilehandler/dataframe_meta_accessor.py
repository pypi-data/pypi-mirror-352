import pandas as pd
import logging
from pandas.api.extensions import register_series_accessor
from pandas.api.extensions import register_dataframe_accessor
import warnings


logger = logging.getLogger(__name__)


class MetadataHandler:
    """
    The base class for the pandas series and dataframe accessors.
    Offers a very basic metadata handling, by using a dictionary as metadata
    store. The accessors then allow to access this metadata store and
    corresponding methods by calling 'df.meta' or 'series.meta', respectively.
    Mainly targeted for usage with dataframes featuring data from CNV files,
    it for example allows the attachement of parameter metadata found in the
    CNV header to individual dataframe columns.

    This approach was chosen over others, like directly subclassing the pandas
    dataframe or series class, or a seperate metadata storage, due to its
    simplicity and ability to keep using the full powerfull pandas library
    without the need to implement each and every transformation. Of course,
    the 'attrs' attribute does offer a similar metadata storage. But at the
    time of writing this, it is still in a very experimental condition and does
    not propagate reliably.
    """

    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        if not hasattr(self._obj, "_metadata_store"):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                self._obj._metadata_store = {}

    @property
    def metadata(self):
        return self._obj._metadata_store

    @metadata.setter
    def metadata(self, value):
        self._obj._metadata_store = value

    def get(self, key, default=None):
        return self._obj._metadata_store.get(key, default)

    def set(self, key, value):
        self._obj._metadata_store[key] = value

    def clear(self):
        self._obj._metadata_store.clear()


@register_series_accessor("meta")
class SeriesMetaAccessor(MetadataHandler):
    """
    Series implementation of the Metadata Accessor.
    Does not offer anything more than the base class at the moment.
    """

    def __init__(self, pandas_obj):
        super().__init__(pandas_obj)


@register_dataframe_accessor("meta")
class DataFrameMetaAccessor(MetadataHandler):
    """
    DataFrame implementation of the Metadata Accessor.
    Introduces another attribute, '_header_level_detail', that stores the
    currently displayed metadata as column names. Additionally offers methods
    to sync metadata between the dataframe and its series, and the handling of
    common operations, like renaming or the addition of new columns.
    """

    def __init__(self, pandas_obj):
        super().__init__(pandas_obj)
        if not hasattr(self._obj, "_header_level_detail"):
            self._obj._header_level_detail = "shortname"
        # Initialize DataFrame metadata
        self.aggregate_series_metadata()

    @property
    def header_detail(self):
        return self._obj._header_level_detail

    @header_detail.setter
    def header_detail(self, value):
        self._obj._header_level_detail = value

    @property
    def metadata(self):
        return self._obj._metadata_store

    @metadata.setter
    def metadata(self, value):
        meta_dict = {
            shortname: self.add_default_metadata(shortname, metainfo)
            for shortname, metainfo in value.items()
        }
        self._obj._metadata_store = meta_dict
        self.propagate_metadata_to_series()

    def aggregate_series_metadata(self):
        """Aggregate metadata from Series within the DataFrame."""
        for column in self._obj.columns:
            if isinstance(self._obj[column], pd.Series) and hasattr(
                self._obj[column], "meta"
            ):
                self.metadata[column] = self._obj[column].meta.metadata

    def propagate_metadata_to_series(self):
        """Propagate DataFrame-level metadata back to Series."""
        for column in self._obj.columns:
            if isinstance(self._obj[column], pd.Series) and hasattr(
                self._obj[column], "meta"
            ):
                for key, value in self.metadata.items():
                    if key == column:
                        try:
                            self._obj[column].meta.metadata = value
                        except TypeError:
                            logger.error(f"{column}: {value}")

    def update_metadata_on_rename(self, rename_dict):
        """Update metadata when columns are renamed."""
        new_metadata = {}
        for old_name, new_name in rename_dict.items():
            for key, value in self.metadata.items():
                if key == old_name:
                    new_metadata[new_name] = value
        self.metadata = new_metadata
        self.propagate_metadata_to_series()

    def rename(self, rename_key):
        """Rename the column names by using a metadata point."""
        rename_dict = {
            column: (
                self._obj[column].meta.get(rename_key)
                if rename_key in list(self._obj[column].meta.metadata.keys())
                else column
            )
            for column in self._obj.columns
        }
        self._obj.rename(columns=rename_dict, inplace=True)
        self.header_detail = rename_key
        self.update_metadata_on_rename(rename_dict)

    def add_column(
        self,
        name: str,
        data: pd.Series | list,
        location: int | None = None,
        metadata: dict = {},
    ):
        """Add a column and use or generate metadata for it."""
        location = len(self._obj.columns) if location is None else location
        self._obj.insert(
            loc=location,
            column=name,
            value=data,
            allow_duplicates=False,
        )
        self.metadata[name] = self.add_default_metadata(name, metadata)
        self.propagate_metadata_to_series()

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
        """Fill up missing metadata points with a default value."""
        default = {}
        for key in list_of_keys:
            if key not in list(metadata.keys()):
                default[key] = name
        return {**metadata, **default}
