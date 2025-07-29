from typing import List, Dict, Union, Optional, Literal, Tuple
import os
import json
from enum import Enum
from tqdm import tqdm
from pathlib import Path
from requests.auth import HTTPBasicAuth
from functools import singledispatchmethod

from ._constants import SpatialAttrs
from ._constants import DefaultGroup
from ._constants import ConnectorKeys
from ._constants import SubmissionType
from ._constants import ExpressionSubmission
from ._constants import SubmissionElementKeys

from ._api import PyAPI
from ._api import OpenAPI
from ._api import Connector
from ._analysis import Analysis
from ._spatialdata import SpatialData
from ._anndata import ConnectorAnnData
from ._studies import Studies, Study, Data
from ._utils import get_chunk_size, format_print


class SpatialXConnector(Connector):
    """
    SpatialX Connector
    Supporting to work with spatial data via notebook.
    """

    def __init__(
        self,
        domain: str,
        token: str,
        verify_ssl: bool = False,
        authentication: Optional[HTTPBasicAuth] = None,
    ):
        """
        Construct parameters for train and query k-nearest neighbors

        Parameters
        ----------
        domain: ``str``
            SpatialX domain
        token: ``str``
            User's token
        verify_ssl: ``bool``, default: False
            Verify SSL or not.
        """
        super().__init__(domain, token, verify_ssl=verify_ssl, authentication=authentication)
        self.__pyapi = self.self_init(PyAPI)
        self.__openapi = self.self_init(OpenAPI)
        self.__analysis = self.self_init(Analysis)

    @property
    def pyapi(self) -> PyAPI:
        return self.__pyapi

    @property
    def openapi(self) -> OpenAPI:
        return self.__openapi

    @property
    def analysis(self) -> Analysis:
        return self.__analysis

    @property
    def info(self):
        """Current user's information"""
        info = self.openapi.info
        return {
            field: info[field]
            for field in ConnectorKeys.INFORMATION_FIELDS.value
        }

    @property
    def groups(self):
        """List all reachable groups of current user in domain server."""
        group_info = self.openapi.groups
        groups = {
            v: k for k, v in group_info[ConnectorKeys.DEFAULT.value].items()
        }
        for group in group_info[ConnectorKeys.GROUPS.value]:
            groups[group["name"]] = group["id"]
        return groups

    @property
    def external_folders(self):
        """List all reachable mounted shared folders of current user from BBrowserX/BioStudio."""
        mounts = self.openapi.mounts
        return {
            folder["name"]: folder["path"]
            for folder in mounts["folders"]
        } if mounts.get("folders", None) else {}

    @property
    def external_s3(self):
        """List all reachable mounted s3 of current user from BBrowserX/BioStudio."""
        mounts = self.openapi.mounts
        return mounts.get("s3", {})

    @property
    def folders(self):
        """List all reachable mounted shared folders of current user in domain server."""
        defaults = {
            folder["name"]: folder["path"]
            for folder in self.openapi.info["default_mount"]["folders"]
        }
        return dict(self.external_folders.items() | defaults.items())

    @property
    def s3(self):
        """List all reachable mounted s3 clouds of current user in domain server."""
        s3_buckets = {}
        for s3 in self.openapi.info["default_mount"]["s3"]:
            name = s3.get("name", "")
            if len(name) == 0 or name in s3_buckets:
                name = s3["id"]
            s3_buckets[name] = s3["path"]

        for external_s3 in self.external_s3:
            name = external_s3.get("name", "")
            if len(name) == 0 or name in s3_buckets:
                name = external_s3["id"]
            if name in s3_buckets:
                name = f"{name} - External AWS"
            s3_buckets[name] = external_s3["path"]

        for internal_s3 in self.openapi.s3:
            name = internal_s3["map_settings"].get("name", "")
            if len(name) == 0 or name in s3_buckets:
                name = internal_s3["map_settings"]["id"]
            if name in s3_buckets:
                name = f"{name} - Internal AWS"
            s3_buckets[name] = internal_s3["map_settings"]["path"]

        return s3_buckets

    def listdir(
        self,
        path: str,
        ignore_hidden: bool = True,
        get_details: bool = False,
    ) -> Union[List[Dict[str, Union[str, int, dict]]], List[str]]:
        """
        List all files and folders with path in domain server

        Parameters
        ----------
        path: ``str``
            path of folder to list
        ignore_hidden: ``bool``, default: True
            Ignore hidden files/folders or not
        get_details: ``bool``, default: False
            Get details information or not

        Returns
        -------
        results: ``Union[List[Dict[str, Union[str, int, dict]]], List[str]]``
            Folders and files with their information
        """
        dir_elements = self.openapi.list_dir(
            path, ignore_hidden=ignore_hidden
        )[ConnectorKeys.ENTITIES.value]
        if get_details:
            return dir_elements
        return [element[ConnectorKeys.NAME.value] for element in dir_elements]

    def parse_data_information(
        self,
        data_name: str,
        technology: str,
        data_path: str,
        args: dict = None,
        min_genes: int = 1,
        min_counts: int = 1,
        mito_controls_percentage: float = 0.25,
    ) -> dict:
        """
        Parse information of data to valid format for submission

        Parameters
        ----------
        data_name: ``str``
            Name of spatial data
        technology: ``str``
            Technology of spatial data
        data_path: ``str``
            Path to spatial data

        Returns
        -------
        submission_data: ``dict``
            Auto-detect information for submission
        """
        info = self.pyapi.parse_data_information(data_name, technology, data_path)
        if args is not None:
            args = [
                {
                    ConnectorKeys.KEY.value: key,
                    ConnectorKeys.VALUE.value: value,
                }
                for key, value in args.items()
            ]
            for sample_data in info:
                sample_data[ConnectorKeys.ARGS.value] = sample_data[ConnectorKeys.ARGS.value] + args

        for sample_data in info:
            if sample_data[ConnectorKeys.KWARGS.value] is None:
                sample_data[ConnectorKeys.KWARGS.value] = []
            sample_data[ConnectorKeys.KWARGS.value] = sample_data[ConnectorKeys.KWARGS.value] + [
                {ConnectorKeys.KEY.value: key, ConnectorKeys.VALUE.value: value}
                for key, value in dict(
                    min_genes=min_genes,
                    min_counts=min_counts,
                    mito_controls_percentage=mito_controls_percentage,
                ).items()
            ]

        return info

    def parse_multiple_samples_information(
        self,
        technology: str,
        data_path: str,
        sample_name_mapping: dict = {},
        data_name_mapping: dict = {},
        args: dict = None,
        min_genes: int = 1,
        min_counts: int = 1,
        mito_controls_percentage: float = 0.25,
    ) -> List[dict]:
        """
        Parse information of multiple samples to valid format for submission

        Parameters
        ----------
        technology: ``str``
            Technology of spatial data
        data_path: ``str``
            Path to spatial data

        Returns
        -------
        submission_samples: ``dict``
            Auto-detect information for submission
        """
        if args is not None:
            args = [
                {
                    ConnectorKeys.KEY.value: key,
                    ConnectorKeys.VALUE.value: value,
                }
                for key, value in args.items()
            ]

        results: List[dict] = []
        for folder in self.listdir(data_path, get_details=True):
            if folder[ConnectorKeys.TYPE.value] != ConnectorKeys.DIRECTORY.value:
                continue
            try:
                info = self.pyapi.parse_data_information(
                    data_name_mapping.get(folder[ConnectorKeys.NAME.value], folder[ConnectorKeys.NAME.value]),
                    technology,
                    os.path.join(data_path, folder[ConnectorKeys.NAME.value]),
                )
                if args is not None:
                    for sample_data in info:
                        sample_data[ConnectorKeys.ARGS.value] = sample_data[ConnectorKeys.ARGS.value] + args

                for sample_data in info:
                    if sample_data.get(ConnectorKeys.KWARGS.value, None) is None:
                        sample_data[ConnectorKeys.KWARGS.value] = []
                    sample_data[ConnectorKeys.KWARGS.value] = sample_data[ConnectorKeys.KWARGS.value] + [
                        {ConnectorKeys.KEY.value: key, ConnectorKeys.VALUE.value: value}
                        for key, value in dict(
                            min_genes=min_genes,
                            min_counts=min_counts,
                            mito_controls_percentage=mito_controls_percentage,
                        ).items()
                    ]

                results.append({
                    ConnectorKeys.SAMPLE_NAME.value: sample_name_mapping.get(
                        folder[ConnectorKeys.NAME.value], folder[ConnectorKeys.NAME.value]
                    ),
                    ConnectorKeys.DATA.value: info,
                })
            except Exception as e:
                print(f"Fail to parse data in {folder[ConnectorKeys.NAME.value]}: {e}")

        return results

    def list_study(
        self, group: str, species: str, **kwargs
    ) -> Studies:
        """
        List reachable studies

        Parameters
        ----------
        group: ``str``
            Group of studies
        species: ``str``
            Species of studies

        Returns
        -------
        results: ``Studies``
            List of studies and their information

        Keyword Arguments
        -----------------
        limit: ``int``, default: 50
            Limit of responsing data
        offset: ``int``, default: 50
            Starting point of responsing data
        """
        if isinstance(group, Enum):
            group = group.value
        group = self.groups.get(group, group)
        return self.self_init(
            Studies,
            data=self.openapi.list_study(group, species, **kwargs)["list"],
        )

    def get_study_detail(self, study_id: str, **kwargs) -> Study:
        """
        Get details information of study

        Parameters
        ----------
        study_id: ``str``
            Id of study

        Returns
        -------
        results: ``Dict[str, Union[str, dict, List[dict]]]``
            Information of study

        Keyword Arguments
        -----------------
        limit: ``int``, default: 50
            Limit of responsing data
        offset: ``int``, default: 50
            Starting point of responsing data
        """
        return self.openapi.get_study_detail(study_id, **kwargs)

    def list_sample(self, study_id: str, **kwargs) -> Dict[str, Union[str, dict, List[dict]]]:
        """
        List samples in a study

        Parameters
        ----------
        study_id: ``str``
            Id of study

        Returns
        -------
        results: ``Dict[str, Union[str, dict, List[dict]]]``
            List of samples and their information

        Keyword Arguments
        -----------------
        limit: ``int``, default: 50
            Limit of responsing data
        offset: ``int``, default: 50
            Starting point of responsing data
        """
        return self.openapi.list_sample(study_id, **kwargs)["list"]

    def get_sample_detail(self, sample_id: str, **kwargs) -> Dict[str, Union[str, dict, List[dict]]]:
        """
        Get details information of sample data

        Parameters
        ----------
        sample_id: ``str``
            Id of sample

        Returns
        -------
        results: ``Dict[str, Union[str, dict, List[dict]]]``
            Information of data

        Keyword Arguments
        -----------------
        limit: ``int``, default: 50
            Limit of responsing data
        offset: ``int``, default: 50
            Starting point of responsing data
        """
        return self.openapi.get_sample_detail(sample_id, **kwargs)

    def rename_sample(self, sample_id: str, new_name: str, **_):
        """
        Rename sample

        Parameters
        ----------
        sample_id: ``str``
            Id of sample of rename
        new_name: ``str``
            New name of sample
        """
        return self.openapi.rename_sample(sample_id, new_name)

    def delete_sample(self, sample_id: str, **_):
        """
        Delete sample

        Parameters
        ----------
        sample_id: ``str``
            Id of sample of delete
        """
        return self.openapi.delete_sample(sample_id)

    def get_sample_data_detail(self, data_id: str, **kwargs) -> Dict[str, Union[str, dict, List[dict]]]:
        """
        Get details information of sample data

        Parameters
        ----------
        data_id: ``str``
            Id of data

        Returns
        -------
        results: ``Dict[str, Union[str, dict, List[dict]]]``
            Information of data

        Keyword Arguments
        -----------------
        limit: ``int``, default: 50
            Limit of responsing data
        offset: ``int``, default: 50
            Starting point of responsing data
        """
        return self.openapi.get_sample_data_detail(data_id, **kwargs)

    def get_sample_data_elements(self, data_id: str) -> Dict[str, List[str]]:
        """
        Get elements of sample data

        Parameters
        ----------
        data_id: ``str``
            Id of data

        Returns
        -------
        results: ``Dict[str, List[str]]``
            Elements of data
        """
        results: Dict[str, Dict[str, dict]] =  \
            self.openapi.get_sample_data_detail(data_id).get("map_submit_result", None)
        spdata = self.self_init(SpatialData, data_id=data_id)
        if results is None:
            return {}
        elements: Dict[str, List[str]] = {}
        for value in results.values():
            if not isinstance(value, dict):
                continue
            for k, v in value.items():
                if k not in elements:
                    elements[k] = []
                elements[k].extend(
                    getattr(spdata, SpatialAttrs.SPATIAL_ELEMENT_MAPPING.value[k]).get_name_by_id(
                        [v] if isinstance(v, str) else v.keys()
                    )
                )
        return elements

    def rename_sample_data(self, data_id: str, new_name: str, **_):
        """
        Rename sample data

        Parameters
        ----------
        data_id: ``str``
            Id of data to rename
        new_name: ``str``
            New name of data
        """
        return self.openapi.rename_sample_data(data_id, new_name)

    def delete_sample_data(self, data_id: str, **_):
        """
        Delete sample data

        Parameters
        ----------
        data_id: ``str``
            Id of data to delete
        """
        return self.openapi.delete_sample_data(data_id)

    def get_anndata(self, data_id: str, anndata_id: str) -> ConnectorAnnData:
        return self.self_init(SpatialData, data_id=data_id).tables[anndata_id]

    def add_sample(
        self,
        study_id: str,
        sample_name: str,
        sample_data: List[dict] = [],
    ) -> Dict[str, Union[str, List[dict]]]:
        """
        Add a sample to a existed study

        Parameters
        ----------
        study_id: ``str``
            Id of study
        sample_name: ``str``
            Sample name
        sample_data: ``List[dict]``, default: []
            List of data in sample, each data is result of ``parse_data_information`` function

        Returns
        -------
        results: ``Dict[str, Union[str, List[dict]]]``
            Submission information
        """

        return self.openapi.create_sample(study_id, sample_name, sample_data)

    def add_sample_data(
        self,
        study_id: str,
        sample_id: str,
        sample_data: List[dict],
    ) -> Dict[str, Union[str, List[dict]]]:
        """
        Add data to a existed sample

        Parameters
        ----------
        study_id: ``str``
            Id of sample's root study
        sample_id: ``str``
            Id of sample
        sample_data: ``List[dict]``
            List of data in sample, each data is result of ``parse_data_information`` function

        Returns
        -------
        results: ``Dict[str, Union[str, List[dict]]]``
            Submission information
        """
        return self.openapi.add_sample_data(study_id, sample_id, sample_data)

    def create_study(self, group: str, species: str, title: str, description: str = ""):
        """
        Create new study.

        Parameters
        ----------
        group: ``str``
            Group of study
        species: ``str``
            Species of data in study
        title: ``str``
            Title of study

        Returns
        -------
        study_id: `str`
            ID of the new study
        """
        if isinstance(group, Enum):
            group = group.value
        return self.openapi.create_study(
            self.groups.get(group, group), species, title, description
        )[ConnectorKeys.STUDY_ID.value]

    def __tracking_log_add_sample(self, res: dict, max_time: int = 600):
        data_path = self.get_study_detail(
            res[ConnectorKeys.STUDY_ID.value]
        )[ConnectorKeys.STUDY.value][ConnectorKeys.DATA_PATH.value]

        if ConnectorKeys.SUBMIT_ID.value in res:
            submission_id = res[ConnectorKeys.SUBMIT_ID.value]
            self.tracking_log(
                os.path.join(data_path, f"submit/{submission_id}/submission.log"), max_time=max_time
            )
            return

        for data in res[ConnectorKeys.SAMPLE_DATA.value]:
            submission_id = data[ConnectorKeys.SUBMIT_ID.value]
            self.tracking_log(
                os.path.join(data_path, f"submit/{submission_id}/submission.log"), max_time=max_time
            )

    def submit(
        self,
        group: str,
        species: str,
        title: str,
        sample_name: str,
        sample_data: List[dict],
        description: str = "",
        tracking: bool = False,
        max_time: int = 600,
    ) -> Dict[str, Union[str, List[dict]]]:
        """
        Create new study and submit the first sample.

        Parameters
        ----------
        group: ``str``
            Group of study
        species: ``str``
            Species of data in study
        title: ``str``
            Title of study
        sample_name: ``str``
            Sample name
        sample_data: ``List[dict]``
            List of data in sample, each data is result of ``parse_data_information`` function
        description: ``str``
            Description of the new study.

        Returns
        -------
        results: ``Dict[str, Union[str, List[dict]]]``
            Submission information
        """
        study_id = self.create_study(group, species, title, description=description)
        res = self.add_sample(study_id, sample_name, sample_data)
        if tracking:
            self.__tracking_log_add_sample(res, max_time)
        return res

    def add_multiple_samples(
        self,
        study_id: str,
        sample_data: List[dict],
    ) -> List[Dict[str, Union[str, List[dict]]]]:
        """
        Create new study and submit the first sample.

        Parameters
        ----------
        study_id: ``str``
            ID of study to add samples.
        sample_data: ``List[dict]``
            List of data in sample, each data is result of ``parse_multiple_samples_information`` function

        Returns
        -------
        results: ``List[Dict[str, Union[str, List[dict]]]]``
            Submission information
        """
        results = []
        for sample in sample_data:
            sample_name = sample[ConnectorKeys.SAMPLE_NAME.value]
            data = sample[ConnectorKeys.DATA.value]
            results.append(self.add_sample(study_id, sample_name, data))

        return results

    def submit_multiple_samples(
        self,
        group: str,
        species: str,
        title: str,
        sample_data: List[dict],
        description: str = "",
    ) -> List[Dict[str, Union[str, List[dict]]]]:
        """
        Create new study and submit the first sample.

        Parameters
        ----------
        group: ``str``
            Group of study
        species: ``str``
            Species of data in study
        title: ``str``
            Title of study
        sample_data: ``List[dict]``
            List of data in sample, each data is result of ``parse_multiple_samples_information`` function
        description: ``str``
            Description of the new study.

        Returns
        -------
        results: ``List[Dict[str, Union[str, List[dict]]]]``
            Submission information
        """
        study_id = self.create_study(group, species, title, description=description)
        return self.add_multiple_samples(study_id, sample_data)

    def add_custom_sample(
        self,
        study_id: str,
        sample_name: str,
        data_name: str,
        technology: str,
        adding_types: List[str],
        paths: Dict[str, str] = {},
        args: Dict[str, str] = {},
        kwargs: Dict[str, str] = {},
        tracking: bool = False,
        max_time: int = 600,
    ) -> Dict[str, Union[str, List[dict]]]:
        """
        Create new study and submit the first sample.

        Parameters
        ----------
        title: ``str``
            Title of elements
        study_id: ``str``
            Study ID
        sample_name: ``str``
            Sample Name
        data_name: `str`
            Sample Data Name
        technology: `str`
            Technology of data
        adding_types: `List[str]`
            Type of element to adding, defined in [
                `spatialx_connector.ImagesSubmission`,
                `spatialx_connector.SegmentationSubmission`,
                `spatialx_connector.TrasncriptsSubmission`,
                `spatialx_connector.ExpressionSubmission`,
            ]
        paths: `Dict[str, str]`
            Mapping of elements defined in `spatialx_connector.SubmissionElementKeys` and their paths.
        args: `Dict[str, str]`
            Mapping of elements defined in `spatialx_connector.SubmissionElementKeys` and values.

        Returns
        -------
        results: ``List[Dict[str, Union[str, List[dict]]]]``
            Submission information
        """
        res = self.add_sample(
            study_id,
            sample_name,
            [
                dict(
                    name=data_name,
                    submission_type=SubmissionType.detect_submission_type(technology),
                    technology=technology,
                    identities=adding_types,
                    files=[
                        {
                            ConnectorKeys.KEY.value: key,
                            ConnectorKeys.VALUE.value: value,
                        }
                        for key, value in paths.items()
                    ],
                    folders=[],
                    args=[
                        {
                            ConnectorKeys.KEY.value: key,
                            ConnectorKeys.VALUE.value: value,
                        }
                        for key, value in args.items()
                    ] + [
                        {
                            # Ignore default types of technologies.
                            ConnectorKeys.KEY.value: "ignore_technology_elements",
                            ConnectorKeys.VALUE.value: True,
                        }
                    ],
                    kwargs=[
                        {
                            ConnectorKeys.KEY.value: key,
                            ConnectorKeys.VALUE.value: value,
                        }
                        for key, value in kwargs.items()
                    ],
                )
            ]
        )
        if tracking:
            self.__tracking_log_add_sample(res, max_time)
        return res

    def add_sample_data_element(
        self,
        title: str,
        data_id: str,
        adding_types: List[str],
        paths: Dict[str, str] = {},
        args: Dict[str, str] = {},
        tracking: bool = False,
        max_time: int = 600,
        **_,
    ) -> Dict[str, Union[str, List[dict]]]:
        """
        Create new study and submit the first sample.

        Parameters
        ----------
        title: ``str``
            Title of elements
        data_id: ``str``
            Data ID
        adding_types: `List[str]`
            Type of element to adding, defined in [
                `spatialx_connector.ImagesSubmission`,
                `spatialx_connector.SegmentationSubmission`,
                `spatialx_connector.TrasncriptsSubmission`,
                `spatialx_connector.ExpressionSubmission`,
            ]
        paths: `Dict[str, str]`
            Mapping of elements defined in `spatialx_connector.SubmissionElementKeys` and their paths.
        args: `Dict[str, str]`
            Mapping of elements defined in `spatialx_connector.SubmissionElementKeys` and values.

        Returns
        -------
        results: ``List[Dict[str, Union[str, List[dict]]]]``
            Submission information
        """
        data: Data = self.self_init(Data, data=data_id)
        res = data.add_elements(
            title,
            adding_types=adding_types,
            paths=paths,
            args=args,
        )
        if tracking:
            self.__tracking_log_add_sample(res, max_time)
        return res

    @singledispatchmethod
    def combine_multiple_datasets(
        self,
        study_id: str,
        data_name: str,
        technology: str,
        reference_anndata_paths: List[Tuple[str, str, str]],
        included_images: Optional[Dict[str, str]] = None,
        included_segmentation: Optional[Dict[str, str]] = None,
        metadata_action: Literal["ignore", "combine", "separate"] = "ignore",
    ):
        """
        Combine multiple datasets into one.

        Parameters
        ----------
        study_id: ``str``
            Study ID
        data_name: ``str``
            Name of the new combined dataset
        technology: ``str``
            Technology of the combined dataset
        reference_anndata_paths: ``List[Tuple[str, str, str]]``
            Information of multiple datasets, list of tuple (sample name, sample id, table name)
        included_images: ``Dict[str, str]``
            Mapping of table and its images
        included_segmentation: ``Dict[str, str]``
            Mapping of table and its segmentation
        metadata_action: ``Literal["ignore", "combine", "separate"]``
            What we do with multiple metadata
        """
        args = [
            {
                ConnectorKeys.KEY.value: SubmissionElementKeys.REFERENCE_ANNDATA_PATHS,
                ConnectorKeys.VALUE.value: json.dumps(reference_anndata_paths),
            },
            {
                ConnectorKeys.KEY.value: SubmissionElementKeys.METADATA_ACTION,
                ConnectorKeys.VALUE.value: metadata_action,
            },
            {
                # Ignore default types of technologies.
                ConnectorKeys.KEY.value: "ignore_technology_elements",
                ConnectorKeys.VALUE.value: True,
            }
        ]
        if included_images is not None and len(included_images) > 0:
            args.append(
                {
                    ConnectorKeys.KEY.value: SubmissionElementKeys.INCLUDED_IMAGES,
                    ConnectorKeys.VALUE.value: json.dumps(included_images),
                }
            )
        if included_segmentation is not None and len(included_segmentation) > 0:
            args.append(
                {
                    ConnectorKeys.KEY.value: SubmissionElementKeys.INCLUDED_SEGMENTATION,
                    ConnectorKeys.VALUE.value: json.dumps(included_segmentation),
                }
            )

        return self.add_sample(
            study_id=study_id,
            sample_name="Default combined samples",
            sample_data=[
                dict(
                    name=data_name,
                    submission_type="COMBINED_DATASETS",
                    technology=technology,
                    identities=[ExpressionSubmission.MERGE_MULTIPLE_ANNDATA],
                    files=[],
                    folders=[],
                    args=args,
                    kwargs=[],
                )
            ]
        )

    @combine_multiple_datasets.register(list)
    def _combine_multiple_datasets(
        self,
        data_ids: List[str],
        data_name: str,
        technology: str,
        metadata_action: Literal["ignore", "combine", "separate"] = "ignore",
    ):
        reference_anndata_paths = []
        included_images = {}
        included_segmentation = {}
        study_id = ""

        for data_id in data_ids:
            elements = self.get_sample_data_elements(data_id)
            if SpatialAttrs.ANNOTATED_DATA.value not in elements:
                continue

            details = self.get_sample_data_detail(data_id)
            study_id = details[ConnectorKeys.STUDY_ID.value]
            sample_id = details[ConnectorKeys.SAMPLE_ID.value]
            sample_name = self.get_sample_detail(sample_id)[ConnectorKeys.SAMPLE.value][ConnectorKeys.TITLE.value]
            reference_anndata_paths.append((sample_name, sample_id, elements[SpatialAttrs.ANNOTATED_DATA.value][0]))
            if SpatialAttrs.IMAGES_ELEMENT.value in elements:
                included_images[reference_anndata_paths[-1][-1]] = elements[SpatialAttrs.IMAGES_ELEMENT.value][0]
            if SpatialAttrs.SEGMENTATION_ELEMENT.value in elements:
                included_segmentation[reference_anndata_paths[-1][-1]] = \
                    elements[SpatialAttrs.SEGMENTATION_ELEMENT.value][0]

        return self.combine_multiple_datasets(
            study_id,
            data_name,
            technology,
            reference_anndata_paths,
            included_images=included_images,
            included_segmentation=included_segmentation,
            metadata_action=metadata_action,
        )

    def upload_file(
        self,
        file_path: str,
        server_folder_name: str = "",
        upload_id: str = "",
        is_chunk: bool = False,
    ) -> Dict[str, Union[str, List[dict]]]:
        """
        upload a small file

        Parameters
        ----------
        file_path: ``str``
            File location
        server_folder_name: ``str``
            Folder location in spatialx server
        upload_id: ``str``
            Upload ID

        Returns
        -------
        results: ``Dict[str, Union[str, List[dict]]]``
            Upload information
        """
        return self.openapi.upload_file(
            file_path=file_path,
            folder_name=server_folder_name,
            upload_id=upload_id,
            is_chunk=is_chunk,
        )

    def upload_big_file(
        self,
        file_path: str,
        chunk_size: int = 0,
        debug_mode: bool = False,
        server_folder_name: str = "",
        chunk_resp: dict = {},
        move_to_parent: bool = True,
        is_chunk: bool = False,
    ) -> Dict[str, Union[str, List[dict]]]:
        """
        Upload a big file

        Parameters
        ----------
        file_path: ``str``
            File location
        chunk_size: ``int``
            Chunk size (bytes), 0: auto
        debug_mode: ``bool``
            Debug mode
        server_folder_name: ``str``
            Folder location in spatialx server

        Returns
        -------
        results: ``Dict[str, Union[str, List[dict]]]``
            Upload information
        """
        if not os.path.isfile(file_path):
            raise Exception(f"Invalid file: {file_path}")

        file_size = os.stat(os.path.abspath(file_path)).st_size
        upload_id = ""
        resp = chunk_resp
        if ConnectorKeys.UNIQUE_ID.value in resp:
            upload_id = resp[ConnectorKeys.UNIQUE_ID.value]

        # Direct upload if small file
        if file_size < ConnectorKeys.UPLOAD_CHUNK_SMALL_SIZE.value:
            if ConnectorKeys.UNIQUE_ID.value in resp:
                upload_id = resp[ConnectorKeys.UNIQUE_ID.value]
            return self.upload_file(
                file_path=file_path,
                server_folder_name=server_folder_name,
                upload_id=upload_id,
                is_chunk=is_chunk,
            )

        file_name = Path(file_path).name
        item_chunk_size = get_chunk_size(chunk_size, file_size)

        if (len(resp.keys()) == 0) or (len(upload_id) == 0):
            resp = self.openapi.upload_chunk_start(
                folder_name=server_folder_name,
                parent_is_file=2,
            )

            if ConnectorKeys.UNIQUE_ID.value in resp:
                upload_id = resp[ConnectorKeys.UNIQUE_ID.value]

        file = open(file_path, "rb")
        file.seek(0, 0)
        sending_index = 0
        offset_size = 0
        progress_bar = None
        if debug_mode:
            progress_bar = tqdm(total=file_size, unit="B", unit_scale=True)

        while True:
            data = file.read(item_chunk_size)
            if not data:
                break

            offset_size = offset_size + item_chunk_size
            offset_size = min(file_size, offset_size)

            if debug_mode:
                format_print(f"Upload {file_path}, chunk index : {sending_index + 1} ...")

            if ConnectorKeys.ROOT_FOLDER.value in resp:
                resp_path = resp[ConnectorKeys.ROOT_FOLDER.value]
            else:
                resp_path = resp[ConnectorKeys.PATH.value]
            self.openapi.upload_chunk_process(
                chunk_size=item_chunk_size,
                file_size=file_size,
                offset=offset_size,
                file_name=file_name,
                folder_name=server_folder_name,
                upload_id=upload_id,
                path=resp_path,
                sending_index=sending_index,
                parent_is_file=2,
                file_data=data,
            )

            if debug_mode:
                if progress_bar is not None:
                    progress_bar.update(len(data))

            sending_index = sending_index + 1

        total_index = sending_index
        file.close()

        if ConnectorKeys.ROOT_FOLDER.value in resp:
            resp_path = resp[ConnectorKeys.ROOT_FOLDER.value]
        else:
            resp_path = resp[ConnectorKeys.PATH.value]
        resp2 = self.openapi.upload_chunk_merge(
            total_chunk=total_index,
            file_name=file_name,
            folder_name=server_folder_name,
            upload_id=upload_id,
            path=resp_path,
            parent_is_file=2,
            move_to_parent=move_to_parent,
        )

        if move_to_parent:
            return resp2
        return resp

    def upload_folder(
        self,
        dir_path: str,
        chunk_size: int = 0,
        debug_mode: bool = False,
        server_folder_name: str = "",
        chunk_resp: dict = None,
        is_chunk: bool = False,
    ) -> bool:
        """
        Upload folder as: zarr

        Parameters
        ----------
        dir_path: ``str``
            Folder location
        chunk_size: ``int``
            Chunk size (bytes), 0: auto
        debug_mode: ``bool``
            Debug mode
        server_folder_name: ``str``
            Folder location in spatialx server
        """
        if chunk_resp is None:
            chunk_resp = {}

        if not Path(dir_path).is_dir():
            raise Exception(f"Invalid directory: {dir_path}.")

        root_folder_path = os.path.basename(dir_path)
        if server_folder_name and len(server_folder_name) > 0:
            root_folder_path = os.path.join(server_folder_name, root_folder_path)

        src_path = Path(dir_path)
        resp = chunk_resp

        for src_child in src_path.iterdir():
            if src_child.is_dir():
                dst_child = os.path.join(dir_path, src_child.name)
                resp = self.upload_folder(
                    dir_path=dst_child,
                    chunk_size=chunk_size,
                    debug_mode=debug_mode,
                    server_folder_name=root_folder_path,
                    chunk_resp=resp,
                    is_chunk=True,
                )
            else:
                if src_child.is_symlink():
                    continue

                dst_child = os.path.join(dir_path, src_child.name)
                resp = self.upload_big_file(
                    file_path=dst_child,
                    chunk_size=chunk_size,
                    debug_mode=debug_mode,
                    server_folder_name=root_folder_path,
                    chunk_resp=resp,
                    move_to_parent=False,
                    is_chunk=True,
                )

        if is_chunk:
            return resp
        return self.openapi.upload_folder_finish(
            root_folder_path,
            resp[ConnectorKeys.UNIQUE_ID.value],
        )

    def list_lens_bulk_studies(self, host: str, token: str, group: str, species: str):
        from bioturing_connector.lens_bulk_connector import LensBulkConnector  # type: ignore

        connector = LensBulkConnector(host=host, token=token, ssl=True)
        connector.test_connection()
        if group == DefaultGroup.PERSONAL_WORKSPACE.value:
            group_id = DefaultGroup.LENS_GROUP_ID_PERSONAL_WORKSPACE.value
        elif group == DefaultGroup.ALL_MEMBERS.value:
            group_id = DefaultGroup.LENS_GROUP_ID_ALL_MEMBERS.value
        else:
            group_id = self.groups.get(group, group)

        studies_info = connector.get_all_studies_info_in_group(group_id=group_id, species=species)
        studies_info = [
            {
                **info,
                ConnectorKeys.SPECIES.value: species,
                ConnectorKeys.GROUP_ID.value: self.groups.get(
                    group, DefaultGroup.PERSONAL_WORKSPACE.value
                ),
            }
            for info in studies_info
        ]
        return studies_info

    def list_lens_sc_studies(self, host: str, token: str, group: str, species: str):
        from bioturing_connector.lens_sc_connector import LensSCConnector  # type: ignore

        connector = LensSCConnector(host=host, token=token, ssl=True)
        connector.test_connection()
        if isinstance(group, Enum):
            group = group.value
        if group == DefaultGroup.PERSONAL_WORKSPACE.value:
            group_id = DefaultGroup.LENS_GROUP_ID_PERSONAL_WORKSPACE.value
        elif group == DefaultGroup.ALL_MEMBERS.value:
            group_id = DefaultGroup.LENS_GROUP_ID_ALL_MEMBERS.value
        else:
            group_id = self.groups[group]

        studies_info = connector.get_all_studies_info_in_group(group_id=group_id, species=species)
        studies_info = [
            {
                **info,
                ConnectorKeys.SPECIES.value: species,
                ConnectorKeys.GROUP_ID.value: self.groups[group],
            }
            for info in studies_info
        ]
        return studies_info

    def convert_data_from_lens(self, study_info: Union[dict, List[dict]]):
        if isinstance(study_info, dict):
            study_info = [study_info]

        for info in study_info:
            self.openapi.convert_from_lens(
                f"ST-{info['id']}",
                info["title"],
                info[ConnectorKeys.GROUP_ID.value],
                info[ConnectorKeys.SPECIES.value],
                info["id"],
            )
