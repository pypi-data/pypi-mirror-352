from typing import Union, Dict, List
from functools import cached_property
import logging

import numpy as np
import pandas as pd

from ._api import Connector, OpenAPI
from ._spatialdata import SpatialData
from ._utils import left_aligning, right_aligning, confirm
from ._constants import ConnectorKeys, EnableStatus, SpatialAttrs


class Data(Connector):
    def __init__(
        self,
        domain: str,
        token: str,
        data: Union[dict, str] = {},
        **kwargs,
    ):
        super().__init__(domain, token, **kwargs)
        self.__openapi: OpenAPI = self.self_init(OpenAPI)

        if isinstance(data, str):
            data = self.__openapi.get_sample_data_detail(data_id=data)
        self.__details = data

        self.data_id = self.__details[ConnectorKeys.DATA_ID.value]
        self.sample_id = self.__details[ConnectorKeys.SAMPLE_ID.value]
        self.study_id = self.__details[ConnectorKeys.STUDY_ID.value]
        self.title = self.__details[ConnectorKeys.TITLE.value]
        self.technology = self.__details[ConnectorKeys.TECHNOLOGY.value]
        self.enable_status = self.__details[ConnectorKeys.ENABLE_STATUS.value]

    def update(self):
        self = self.self_init(Data, data=self.data_id)

    def repr(self):
        return f"[Data - {self.data_id}] {self.title} "\
            f"(Technology: {self.technology} - Status: {EnableStatus.get_status(self.enable_status)})"

    def __repr__(self):
        text = self.repr() + "\n with elements:"

        mapping_elements = {
            "images": "Images",
            "segmentation": "Segmentation",
            "spot": "Spots",
            "cell_centers": "Cells centers",
            "transcripts": "Transcripts",
            "annotated_data": "AnnData",
        }

        for k in mapping_elements.keys():
            if k not in self.elements:
                continue
            values = self.elements[k]
            text += f"\n\t{mapping_elements[k]}: " + ", ".join([self.id2name[v] for v in values])
        return text

    def rename(self, new_name: str):
        if self.title == new_name:
            return
        self.__openapi.rename_sample_data(self.data_id, new_name)
        self.update()

    def delete(self):
        logger = logging.getLogger("spatialx_sdks_stdout")
        logger.info(f"Do you confirm to delete data {self.repr()}?")

        text = f"Do you confirm to delete data {self.repr()}?"
        if not confirm(text):
            logger.info("Canceled!")
            return
        res = self.__openapi.delete_sample_data(self.data_id)
        self.update()
        return res

    @cached_property
    def elements(self) -> Dict[str, List[str]]:
        results: dict = self.__details.get("map_submit_result", {})

        elements: Dict[str, List[str]] = {}
        for value in results.values():
            if not isinstance(value, dict):
                continue
            for k, v in value.items():
                if k not in elements:
                    elements[k] = []
                elements[k].extend(v.keys() if isinstance(v, dict) else [v])
        return elements

    @cached_property
    def id2name(self) -> dict:
        id2name = {}
        spdata = self.self_init(SpatialData, data_id=self.data_id)
        for k, values in self.elements.items():
            k = SpatialAttrs.SPATIAL_ELEMENT_MAPPING.value[k]
            for v in values:
                id2name[v] = getattr(spdata, k).get_name_by_id(v)
        return id2name

    @cached_property
    def name2id(self) -> dict:
        names, counts = np.unique(list(self.id2name.values))
        names = names[counts == 1]
        return {v: k for k, v in self.id2name.items() if v in names}

    def __name2id(self, element_id: str):
        if element_id not in self.elements:
            if element_id not in self.name2id:
                raise ValueError(f"Element {element_id} is not found or is duplicated in data.")
            element_id = self.name2id[element_id]
        return element_id

    def delete_element(self, element_id: str):
        logger = logging.getLogger("spatialx_sdks_stdout")
        element_id = self.__name2id(element_id)
        logger.info(f"Do you confirm to delete element {self.id2name[element_id]}?")

        text = f"Do you confirm to delete element {self.id2name[element_id]}?"
        if not confirm(text):
            logger.info("Canceled!")
            return
        res = self.__openapi.delete_sample_data_element(self.data_id, element_id)
        self.update()
        return res

    def add_elements(
        self,
        title: str,
        adding_types: List[str],
        paths: Dict[str, str] = {},
        args: Dict[str, str] = {},
        kwargs: Dict[str, str] = {},
    ) -> Dict[str, Union[str, List[dict]]]:
        """
        Create new study and submit the first sample.

        Parameters
        ----------
        title: ``str``
            Title of elements
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
        res = self.__openapi.add_sample_data_element(
            title,
            self.study_id,
            self.sample_id,
            self.data_id,
            identities=adding_types,
            files=[
                {
                    ConnectorKeys.KEY.value: key,
                    ConnectorKeys.VALUE.value: value,
                }
                for key, value in paths.items()
            ],
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
            ]
        )
        return res

    @cached_property
    def spatialdata(self) -> SpatialData:
        return self.self_init(SpatialData, data_id=self.data_id)


class Sample(Connector):
    def __init__(
        self,
        domain: str,
        token: str,
        data: Union[dict, str] = {},
        **kwargs,
    ):
        super().__init__(domain, token, **kwargs)
        self.__openapi: OpenAPI = self.self_init(OpenAPI)

        if isinstance(data, dict) and ("sample" not in data or "sample_data" not in data):
            data = data[ConnectorKeys.SAMPLE_ID.value]

        if isinstance(data, str):
            data = self.__openapi.get_sample_detail(sample_id=data)
        self.__sampe_details = data["sample"]
        self.__data_details = data["sample_data"]

        self.sample_id = self.__sampe_details[ConnectorKeys.SAMPLE_ID.value]
        self.study_id = self.__sampe_details[ConnectorKeys.STUDY_ID.value]
        self.title = self.__sampe_details[ConnectorKeys.TITLE.value]
        self.enable_status = self.__sampe_details[ConnectorKeys.ENABLE_STATUS.value]

        self.sample_data: Dict[str, Data] = {}
        self.index_sample_data = {}
        for i, data in enumerate(self.__data_details):
            if data[ConnectorKeys.ENABLE_STATUS.value] >= 3:
                continue
            self.sample_data[data[ConnectorKeys.DATA_ID.value]] = self.self_init(Data, data=data)
            self.index_sample_data[data[ConnectorKeys.DATA_ID.value]] = i
            self.index_sample_data[i] = data[ConnectorKeys.DATA_ID.value]

    def update(self):
        self = self.self_init(Sample, data=self.sample_id)

    def __repr__(self):
        text = f"[Sample - {self.sample_id}] {self.title} (Status: {EnableStatus.get_status(self.enable_status)})"
        for data in self.sample_data.values():
            text += f"\n\t{self.index_sample_data[data.data_id]}. " + data.repr()
        return text

    def __getitem__(self, key) -> Data:
        if isinstance(key, int):
            key = self.index_sample_data[key]
        return self.sample_data[key]

    def __iter__(self):
        for sample_data in self.sample_data.values():
            yield sample_data

    def rename(self, new_name: str):
        if self.title == new_name:
            return
        self.__openapi.rename_sample(self.sample_id, new_name)
        self.update()

    def delete(self):
        logger = logging.getLogger("spatialx_sdks_stdout")
        desc = "\t" + self.__repr__().replace('\n', '\n\t')
        logger.info(f"Do you confirm to delete sample and all its data below:\n{desc}")

        text = f"Delete sample `{self.title}` with its {len(self.sample_data)} data?"
        if not confirm(text):
            logger.info("Canceled!")
            return
        res = self.__openapi.delete_sample(self.sample_id)
        self.update()
        return res


class Study(Connector):
    def __init__(
        self,
        domain: str,
        token: str,
        data: Union[dict, str] = {},
        **kwargs,
    ):
        super().__init__(domain, token, **kwargs)
        self.__openapi: OpenAPI = self.self_init(OpenAPI)

        if isinstance(data, str):
            data = self.__openapi.get_study_detail(study_id=data)
        self.__details = data

        self.study_id = self.__details[ConnectorKeys.STUDY.value][ConnectorKeys.STUDY_ID.value]
        self.title = self.__details[ConnectorKeys.STUDY.value][ConnectorKeys.TITLE.value]
        self.species = self.__details[ConnectorKeys.STUDY.value][ConnectorKeys.SPECIES.value]

        self.sample: Dict[str, Sample] = {}
        self.index_sample = {}
        for i, sample in enumerate(self.__details["samples"]):
            if sample[ConnectorKeys.ENABLE_STATUS.value] >= 3:
                continue
            self.sample[sample[ConnectorKeys.SAMPLE_ID.value]] = self.self_init(Sample, data=sample)
            self.index_sample[sample[ConnectorKeys.SAMPLE_ID.value]] = i
            self.index_sample[i] = sample[ConnectorKeys.SAMPLE_ID.value]

    def update(self):
        self = self.self_init(Study, data=self.study_id)

    def __repr__(self):
        text = f"{self.title} (Species: {self.species})"
        for sample in self.sample.values():
            text += f"\n\t{self.index_sample[sample.sample_id]}. " + sample.__repr__().replace("\n", "\n\t")
        return text

    def __getitem__(self, key) -> Sample:
        if isinstance(key, int):
            key = self.index_sample[key]
        return self.sample[key]

    def __iter__(self):
        for sample in self.sample.values():
            yield sample

    def rename(self, new_name: str):
        if self.title == new_name:
            return
        self.__openapi.rename_study(self.study_id, new_name)
        self.update()

    def delete(self):
        logger = logging.getLogger("spatialx_sdks_stdout")
        logger.info(f"Do you confirm to delete study {self.title}?")

        text = f"Do you confirm to delete study {self.title}?"
        if not confirm(text):
            logger.info("Canceled!")
            return
        res = self.__openapi.delete_study(self.study_id)
        self.update()
        return res


class Studies(Connector):
    def __init__(
        self,
        domain: str,
        token: str,
        data: Union[list, dict] = {},
        **kwargs,
    ):
        super().__init__(domain, token, **kwargs)
        self.__openapi: OpenAPI = self.self_init(OpenAPI)

        if isinstance(data, dict):
            data: list = self.__openapi.list_study(**data)["list"]
        self.__details = data

        fields = [
            ConnectorKeys.STUDY_ID.value,
            ConnectorKeys.TITLE.value,
            ConnectorKeys.TOTAL_SAMPLE.value,
            ConnectorKeys.TOTAL_DATA.value,
        ]
        info: Dict[str, List] = {"ID": []}
        info.update({field: [] for field in fields})
        for i, study in enumerate(self.__details):
            info["ID"].append(i)
            for field in fields:
                info[field].append(study[field])
        study_id = info[ConnectorKeys.STUDY_ID.value]
        self.info: pd.DataFrame = pd.DataFrame(info, index=study_id)

    def __repr__(self):
        columns = ["", "Study ID", "Title", "Total Sample", "Total Data"]
        column_aligning = [left_aligning, left_aligning, left_aligning, right_aligning, right_aligning]

        sizes = [
            max(
                len(columns[i]),
                np.max([len(str(v)) for v in self.info.values[:, i]])
            )
            for i in range(len(column_aligning))
        ]
        text = " │ ".join([
            left_aligning(column, sizes[i])
            for i, column in enumerate(columns)
        ]) + " │"
        text += "\n" + "─┼─".join(["─" * size for size in sizes]) + "─┤"
        for values in self.info.values:
            text += "\n" + " │ ".join([
                column_aligning[i](values[i], sizes[i])
                for i in range(len(values))
            ]) + " │"
        return text

    def head(self, n: int):
        return self.info.head(n)

    def tail(self, n: int):
        return self.info.tail(n)

    def __getitem__(self, k: Union[int, str]) -> Study:
        if isinstance(k, int):
            k = str(self.info.index.values[k])
        return self.self_init(Study, data=k)
