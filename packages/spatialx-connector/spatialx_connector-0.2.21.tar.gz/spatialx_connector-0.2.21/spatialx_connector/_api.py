import os
import time
import base64
import logging
import traceback
from functools import cached_property
from urllib.parse import urlparse, parse_qs
from typing import Union, List, Dict, Optional


from pydantic import BaseModel  # pylint: disable=no-name-in-module
from requests.auth import HTTPBasicAuth

import zarr
import zarr.storage
import pandas as pd

from . import _constants as constants
from ._utils import RequestMode
from ._utils import request
from ._utils import parse_to_str


DEBUG_MODE = os.environ.get("DEBUG_MODE", "") == "TRUE"
DEFAULT_LOGGER = logging.getLogger("spatialx_sdks_stdout")


class Connector:
    def __init__(
        self,
        domain: str,
        token: str,
        verify_ssl: bool = False,
        authentication: Optional[HTTPBasicAuth] = None,
        **_,
    ):
        self._token = token
        self._verify_ssl = verify_ssl
        self._authentication = authentication

        headers = {constants.TOKEN_KEY: self._token}
        if self._authentication is not None:
            if isinstance(self._authentication, HTTPBasicAuth):
                authentication = (self._authentication.username, self._authentication.password)
            else:
                authentication = self._authentication
            token = base64.b64encode(f"{authentication[0]}:{authentication[1]}".encode("utf-8")).decode("utf-8")
            headers["Authorization"] = f"Basic {token}"
        self._headers = headers

        link = urlparse(domain)
        if len(link.netloc) == 0:
            raise Exception("invalid domain: {}".format(domain))

        params = dict(parse_qs(link.query))
        params = {k: v[0] for k, v in params.items()}
        self.params = params
        self._domain = "{}://{}{}".format(link.scheme, link.netloc, link.path)

    def self_init(self, obj_type, *args, **kwargs):
        return obj_type(
            self._domain, self._token, *args,
            verify_ssl=self._verify_ssl,
            authentication=self._authentication,
            **kwargs,
        )

    def request(
            self,
            url: str,
            params: dict = {},
            json: dict = {},
            data: dict = {},
            mode: str = RequestMode.POST,
            files: dict = {},
    ):
        for k, v in self.params.items():
            params[k] = v

        res: Union[str, dict] = request(
            url=url.replace(os.sep, "/"),
            params=params,
            json=json,
            data=data,
            files=files,
            headers=self._headers,
            mode=mode,
            verify=self._verify_ssl,
            authentication=self._authentication,
        )
        if not isinstance(res, dict):
            return res

        if res.get(constants.ConnectorKeys.STATUS.value, 0) != 0:
            raise Exception(parse_to_str(res))

        return res.get(constants.ConnectorKeys.MESSAGE.value, res)

    def post_pyapi_request(
            self, url: str,
            params: dict = {},
            json: dict = {},
            data: dict = {},
            mode: str = RequestMode.POST,
            files: dict = {},
    ) -> Union[BaseModel, str]:
        return self.request(
            os.path.join(self._domain, constants.V1_API, url),
            params=params, json=json, data=data,
            mode=mode, files=files,
        )

    def post_openapi_request(
            self, url: str,
            params: dict = {},
            json: dict = {},
            data: dict = {},
            mode: str = RequestMode.POST,
            files: dict = {},
    ) -> dict:
        return self.request(
            os.path.join(self._domain, constants.OPEN_API, url),
            params=params, json=json, data=data,
            mode=mode, files=files,
        )

    def _get_zarr_path(self, path: str):
        return os.path.join(self._domain, constants.UCC, path)

    def _open_zarr_root(self, path: str):
        url = self._get_zarr_path(path)
        return zarr.storage.FSStore(url=url, client_kwargs={"headers": self._headers})

    def tracking_log(self, log_path: str, max_time: int = 60):
        log_path = os.path.join(self._domain, constants.UCC, log_path)
        curr_row = 0
        curr_time = time.time()
        for _ in range(max_time):
            if time.time() - curr_time > max_time:
                break
            data = self.request(log_path, mode=RequestMode.GET)
            if data.endswith("\n"):
                data = data[:-1]
            lines = data.split("\n")
            if len(lines) > curr_row:
                print("\n".join(lines[curr_row:]))
            curr_row = len(lines)
            if "DONE." in data[-1000:] or "maximum retry limit" in data[-1000:]:
                break
            time.sleep(1)


class PyAPI(Connector):
    def parse_data_information(self, name: str, technology: str, data_path: str) -> dict:
        return self.post_pyapi_request(
            url=constants.PARSE_DATA_URL,
            json={
                constants.ConnectorKeys.DATA_NAME.value: name,
                constants.ConnectorKeys.TECHNOLOGY.value: technology,
                constants.ConnectorKeys.DATA_PATH.value: data_path,
                constants.ConnectorKeys.HTTP_REQ_PERMISISON_NAME_KEY:
                constants.USER_ROLE_PERMISSION_HASH2.CREATE_NEW_STUDY,
            }
        )

    def rename_image_channels(
        self,
        study_id: str,
        sample_id: str,
        images_id: str,
        channel_names: List[str],
    ) -> dict:
        return self.post_pyapi_request(
            url=constants.RENAME_IMAGE_CHANNELS,
            json={
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.SAMPLE_ID.value: sample_id,
                constants.ConnectorKeys.IMAGES_ID.value: images_id,
                constants.ConnectorKeys.CHANNEL_NAMES.value: channel_names,
                constants.ConnectorKeys.HTTP_REQ_PERMISISON_NAME_KEY:
                constants.USER_ROLE_PERMISSION_HASH2.MODIFY_STUDY,
            }
        )

    def simplify_segmentation(
        self,
        study_id: str,
        sample_id: str,
        segmentation_id: str,
        tolerance: Optional[float],
    ) -> dict:
        return self.post_pyapi_request(
            url=constants.SIMPLIFY_SEGMENTATION,
            json={
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.SAMPLE_ID.value: sample_id,
                constants.ConnectorKeys.SEGMENTATION_ID.value: segmentation_id,
                constants.ConnectorKeys.TOLERANCE.value: tolerance,
                constants.ConnectorKeys.HTTP_REQ_PERMISISON_NAME_KEY:
                constants.USER_ROLE_PERMISSION_HASH2.MODIFY_STUDY,
            }
        )

    def import_metadata(
        self,
        study_id: str,
        sample_id: str,
        table_id: str,
        csv_path: str,
    ) -> dict:
        return self.post_pyapi_request(
            url=constants.IMPORT_METADATA,
            json={
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.SAMPLE_ID.value: sample_id,
                constants.ConnectorKeys.TABLE_ID.value: table_id,
                constants.ConnectorKeys.CSV_PATH.value: csv_path,
                constants.ConnectorKeys.HTTP_REQ_PERMISISON_NAME_KEY:
                constants.USER_ROLE_PERMISSION_HASH2.ADD_NEW_METADATA,
            }
        )

    def list_deconvolution_models(self) -> dict:
        data = self.post_pyapi_request(
            url=constants.LIST_DECONVOLUTION_MODELS,
            mode=RequestMode.GET,
        )
        return pd.DataFrame(data).T


class OpenAPI(Connector):
    @property
    def info(self):
        return self.post_openapi_request(
            url=constants.INFO_URL,
            mode=RequestMode.GET,
        )

    @property
    def mounts(self):
        return self.post_openapi_request(
            url=constants.EXTERNAL_MOUNT_URL,
            mode=RequestMode.GET,
        )

    def list_s3(self, offset: int = 0, limit: int = 100):
        return self.post_openapi_request(
            url=constants.LIST_S3,
            mode=RequestMode.POST,
            data={
                constants.ConnectorKeys.LIMIT.value: limit,
                constants.ConnectorKeys.OFFSET.value: offset,
            }
        )

    @property
    def s3(self):
        return self.list_s3()

    @property
    def groups(self):
        return self.post_openapi_request(
            url=constants.GROUPS_URL,
            mode=RequestMode.GET,
        )

    def list_dir(self, path: str, ignore_hidden: bool = True):
        return self.post_openapi_request(
            constants.LIST_URL,
            data={
                constants.ConnectorKeys.PATH.value: path,
                constants.ConnectorKeys.IGNORE_HIDDEN.value: ignore_hidden,
            }
        )

    def create_study(
        self,
        group_id: str,
        species: str,
        title: str,
        description: str,
        create_type: int = constants.StudyType.SPATIAL_STUDY_TYPE_NUMBER.value,
    ):
        return self.post_openapi_request(
            url=constants.CREATE_STUDY_URL,
            json={
                constants.ConnectorKeys.GROUP_ID.value: group_id,
                constants.ConnectorKeys.SPECIES.value: species,
                constants.ConnectorKeys.TITLE.value: title,
                constants.ConnectorKeys.DESCRIPTION.value: description,
                constants.ConnectorKeys.TYPE.value: create_type,
            }
        )

    def list_study(
        self,
        group_id: str,
        species: str,
        limit: int = 50,
        offset: int = 0,
        active: int = constants.StudyStatus.PROCESSING_STATUS.value,
        compare: int = constants.StudyFilter.NOT_LARGER.value,
    ):
        return self.post_openapi_request(
            url=constants.LIST_STUDY_URL,
            data={
                constants.ConnectorKeys.GROUP_ID.value: group_id,
                constants.ConnectorKeys.SPECIES.value: species,
                constants.ConnectorKeys.LIMIT.value: limit,
                constants.ConnectorKeys.OFFSET.value: offset,
                constants.ConnectorKeys.ACTIVE.value: active,
                constants.ConnectorKeys.COMPARE.value: compare,
            }
        )

    def get_study_detail(self, study_id: str, limit: int = 50, offset: int = 0):
        return self.post_openapi_request(
            url=constants.DETAIL_STUDY_URL,
            params={
                constants.ConnectorKeys.KEY.value: study_id,
                constants.ConnectorKeys.LIMIT.value: limit,
                constants.ConnectorKeys.OFFSET.value: offset,
            },
            mode=RequestMode.GET,
        )

    def update_study(
        self,
        study_id: str,
        title,
        description,
        email_id,
        group_id,
        species,
        publication: List[str] = [],
        tags: List[str] = [],
        author: List[str] = [],
    ):
        return self.post_openapi_request(
            url=constants.UPDATE_STUDY_URL,
            params={
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.TITLE.value: title,
                constants.ConnectorKeys.DESCRIPTION.value: description,
                constants.ConnectorKeys.EMAIL_ID.value: email_id,
                constants.ConnectorKeys.GROUP_ID.value: group_id,
                constants.ConnectorKeys.SPECIES.value: species,
                constants.ConnectorKeys.PUBLICATION.value: publication,
                constants.ConnectorKeys.TAGS.value: tags,
                constants.ConnectorKeys.AUTHOR.value: author,
            },
            mode=RequestMode.POST,
        )

    def rename_study(
        self,
        study_id: str,
        title: str,
    ):
        details = self.get_study_detail(study_id)[constants.ConnectorKeys.STUDY.value]
        return self.update_study(
            study_id=details[constants.ConnectorKeys.STUDY_ID.value],
            title=title,
            description=details[constants.ConnectorKeys.DESCRIPTION.value],
            email_id=details[constants.ConnectorKeys.EMAIL_ID.value],
            group_id=details[constants.ConnectorKeys.GROUP_ID.value],
            species=details[constants.ConnectorKeys.SPECIES.value],
            publication=details[constants.ConnectorKeys.PUBLICATION.value],
            tags=details[constants.ConnectorKeys.TAGS.value],
            author=details[constants.ConnectorKeys.AUTHOR.value],
        )

    def delete_study(self, study_id: str):
        return self.post_openapi_request(
            url=constants.DELETE_STUDY_URL,
            params={
                constants.ConnectorKeys.KEY.value: study_id,
                constants.ConnectorKeys.CLEANUP.value: False,
            },
            mode=RequestMode.POST,
        )

    def create_sample(
        self,
        study_id: str,
        name: str,
        data: List[dict],
    ):
        return self.post_openapi_request(
            url=constants.CREATE_SAMPLE_URL,
            json={
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.NAME.value: name,
                constants.ConnectorKeys.DATA.value: data,
            }
        )

    def add_sample_data(
        self,
        study_id: str,
        sample_id: str,
        data: List[dict],
    ):
        return self.post_openapi_request(
            url=constants.ADD_SAMPLE_DATA_URL,
            json={
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.SAMPLE_ID.value: sample_id,
                constants.ConnectorKeys.DATA.value: data,
            }
        )

    def add_sample_data_element(
        self,
        title: str,
        study_id: str,
        sample_id: str,
        data_id: str,
        identities: List[str] = [],
        files: List[Dict[str, str]] = [],
        folders: List[Dict[str, str]] = [],
        args: List[Dict[str, str]] = [],
        kwargs: List[Dict[str, str]] = [],
    ):
        return self.post_openapi_request(
            url=constants.ADD_URL,
            json={
                constants.ConnectorKeys.TITLE.value: title,
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.SAMPLE_ID.value: sample_id,
                constants.ConnectorKeys.DATA_ID.value: data_id,
                constants.ConnectorKeys.FILES.value: files,
                constants.ConnectorKeys.FOLDERS.value: folders,
                constants.ConnectorKeys.ARGS.value: args,
                constants.ConnectorKeys.KWARGS.value: kwargs,
                constants.ConnectorKeys.IDENTITIES.value: identities,
            },
        )

    def list_sample(
        self,
        study_id: str,
        limit: int = 50,
        offset: int = 0,
        need_data: bool = False,
    ):
        return self.post_openapi_request(
            url=constants.LIST_SAMPLE_URL,
            params={
                constants.ConnectorKeys.KEY.value: study_id,
                constants.ConnectorKeys.LIMIT.value: limit,
                constants.ConnectorKeys.OFFSET.value: offset,
                constants.ConnectorKeys.NEED_DATA.value: need_data,
            },
            mode=RequestMode.GET,
        )

    def get_sample_detail(self, sample_id: str, limit: int = 50, offset: int = 0):
        return self.post_openapi_request(
            url=constants.DETAIL_SAMPLE_URL,
            params={
                constants.ConnectorKeys.KEY.value: sample_id,
                constants.ConnectorKeys.LIMIT.value: limit,
                constants.ConnectorKeys.OFFSET.value: offset,
            },
            mode=RequestMode.GET,
        )

    def rename_sample(self, sample_id: str, new_name: str):
        return self.post_openapi_request(
            url=constants.RENAME_SAMPLE_URL,
            json={
                constants.ConnectorKeys.SAMPLE_ID.value: sample_id,
                constants.ConnectorKeys.NEW_NAME.value: new_name,
            }
        )

    def delete_sample(self, sample_id: str):
        return self.post_openapi_request(
            url=constants.DELETE_SAMPLE_URL,
            json={constants.ConnectorKeys.SAMPLE_ID.value: sample_id}
        )

    def get_sample_data_detail(self, data_id: str, limit: int = 50, offset: int = 0):
        return self.post_openapi_request(
            url=constants.DETAIL_SAMPLE_DATA_URL,
            params={
                constants.ConnectorKeys.KEY.value: data_id,
                constants.ConnectorKeys.LIMIT.value: limit,
                constants.ConnectorKeys.OFFSET.value: offset,
            },
            mode=RequestMode.GET,
        )

    def rename_sample_data(self, data_id: str, new_name: str):
        return self.post_openapi_request(
            url=constants.RENAME_SAMPLE_DATA_URL,
            json={
                constants.ConnectorKeys.DATA_ID.value: data_id,
                constants.ConnectorKeys.NEW_NAME.value: new_name,
            }
        )

    def delete_sample_data(self, data_id: str):
        return self.post_openapi_request(
            url=constants.DELETE_SAMPLE_DATA_URL,
            json={constants.ConnectorKeys.DATA_ID.value: data_id}
        )

    def delete_sample_data_element(self, data_id: str, element_id: str):
        return self.post_openapi_request(
            url=constants.DELETE_SAMPLE_DATA_ELEMENT_URL,
            json={
                constants.ConnectorKeys.DATA_ID.value: data_id,
                constants.ConnectorKeys.ELEMENT_ID.value: element_id,
            }
        )

    def list_public_study(
        self,
        group_id: str,
        species: str,
        limit: int = 50,
        offset: int = 0,
        active: int = constants.StudyStatus.PROCESSING_STATUS.value,
    ):
        return self.post_openapi_request(
            url=constants.LIST_PUBLIC_STUDY_URL,
            json={
                constants.ConnectorKeys.GROUP_ID.value: group_id,
                constants.ConnectorKeys.SPECIES.value: species,
                constants.ConnectorKeys.LIMIT.value: limit,
                constants.ConnectorKeys.OFFSET.value: offset,
                constants.ConnectorKeys.ACTIVE.value: active,
            }
        )

    def upload_file(
        self, file_path: str,
        folder_name: str,
        upload_id: str,
        is_chunk: bool = False,
    ):
        file = open(file_path, "rb")
        resp = self.post_openapi_request(
            url=constants.UPLOAD_FILE_URL,
            data={
                constants.ConnectorKeys.UPLOAD_FOLDER_NAME.value: folder_name,
                constants.ConnectorKeys.UPLOAD_UNIQUE_ID.value: upload_id,
                constants.ConnectorKeys.UPLOAD_IS_CHUNK.value: is_chunk,
            },
            files={
                constants.ConnectorKeys.UPLOAD_FILE_DATA.value: file,
            },
        )
        file.close()
        return resp

    def upload_chunk_start(self, folder_name: str, parent_is_file: int):
        return self.post_openapi_request(
            url=constants.UPLOAD_CHUNK_START_URL,
            json={
                constants.ConnectorKeys.UPLOAD_FOLDER_NAME.value: folder_name,
                constants.ConnectorKeys.UPLOAD_PARENT_IS_FILE.value: parent_is_file,
            }
        )

    def upload_chunk_process(
        self,
        chunk_size: int,
        file_size: int,
        offset: int,
        file_name: str,
        folder_name: str,
        upload_id: str,
        path: str,
        sending_index: int,
        parent_is_file: int,
        file_data: list[str],
    ):
        return self.post_openapi_request(
            url=constants.UPLOAD_CHUNK_PROCESS_URL,
            data={
                constants.ConnectorKeys.UPLOAD_FOLDER_NAME.value: folder_name,
                constants.ConnectorKeys.UPLOAD_PARENT_IS_FILE.value: parent_is_file,
                constants.ConnectorKeys.UPLOAD_CHUNK_SIZE.value: chunk_size,
                constants.ConnectorKeys.UPLOAD_FILE_SIZE.value: file_size,
                constants.ConnectorKeys.UPLOAD_OFFSET.value: offset,
                constants.ConnectorKeys.UPLOAD_FILE_NAME.value: file_name,
                constants.ConnectorKeys.UPLOAD_UNIQUE_ID.value: upload_id,
                constants.ConnectorKeys.UPLOAD_PATH.value: path,
                constants.ConnectorKeys.UPLOAD_SENDING_INDEX.value: sending_index,
            },
            files={
                constants.ConnectorKeys.UPLOAD_FILE_DATA.value: file_data,
            }
        )

    def upload_chunk_merge(
        self,
        total_chunk: int,
        file_name: str,
        folder_name: str,
        upload_id: str,
        path: str,
        parent_is_file: int,
        move_to_parent: bool,
    ):
        return self.post_openapi_request(
            url=constants.UPLOAD_CHUNK_MERGE_URL,
            json={
                constants.ConnectorKeys.UPLOAD_FOLDER_NAME.value: folder_name,
                constants.ConnectorKeys.UPLOAD_PARENT_IS_FILE.value: parent_is_file,
                constants.ConnectorKeys.UPLOAD_TOTAL_CHUNK.value: total_chunk,
                constants.ConnectorKeys.UPLOAD_FILE_NAME.value: file_name,
                constants.ConnectorKeys.UPLOAD_UNIQUE_ID.value: upload_id,
                constants.ConnectorKeys.UPLOAD_PATH.value: path,
                constants.ConnectorKeys.UPLOAD_MOVE_TO_PARENT.value: move_to_parent,
            }
        )

    def upload_folder_finish(self, folder_name: str, upload_id: str):
        return self.post_openapi_request(
            url=constants.UPLOAD_FOLDER_FINISH_URL,
            data={
                constants.ConnectorKeys.UPLOAD_FOLDER_NAME.value: folder_name,
                constants.ConnectorKeys.UPLOAD_UNIQUE_ID.value: upload_id,
            },
        )

    def convert_from_lens(
        self, study_id: str, study_name: str,
        group_id: str, species: str, lens_data_path: str
    ):
        return self.post_openapi_request(
            url=constants.STUDY_CONVERT_FROM_LENS_URL,
            data={
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.TITLE.value: study_name,
                constants.ConnectorKeys.GROUP_ID.value: group_id,
                constants.ConnectorKeys.SPECIES.value: species,
                constants.ConnectorKeys.LENS_DATA_PATH.value: lens_data_path,
            }
        )


class ZarrElement(Connector):
    def __init__(
        self,
        domain: str,
        token: str,
        path: str = "",
        verify_ssl: bool = False,
        authentication: Optional[HTTPBasicAuth] = None,
        elements: List[str] = None,
        extend_information: dict = None,
    ):
        super().__init__(domain, token, verify_ssl=verify_ssl, authentication=authentication)
        self._path = path
        self._elements = elements
        self._extend_information = extend_information if extend_information is not None else {}

    def self_init(self, obj_type, path=None, elements=None, extend_information=None):
        information = self._extend_information
        if extend_information is not None:
            information.update(extend_information)

        if path is None:
            path = self._path

        return obj_type(
            self._domain,
            self._token,
            verify_ssl=self._verify_ssl,
            authentication=self._authentication,
            path=path,
            elements=elements,
            extend_information=information,
        )

    def update(self):
        return self.__init__(
            self._domain,
            self._token,
            verify_ssl=self._verify_ssl,
            authentication=self._authentication,
            path=self._path,
            elements=self._elements,
            extend_information=self._extend_information,
        )

    @cached_property
    def group(self) -> zarr.Group:
        return zarr.Group(self._open_zarr_root(self._path), read_only=True)

    @property
    def attrs(self):
        try:
            res = self.group.attrs.asdict()
        except Exception as e:
            import logging

            logger = logging.getLogger("spatialx_sdks_stdout")
            if DEBUG_MODE:
                logger.error("".join(traceback.format_exception(e)))
            else:
                logger.warning(e)
            res = {}

        return res

    @property
    def _name2id(self) -> Dict[str, str]:
        elements = self.attrs.get("elements", {})
        if self._elements is None:
            return elements
        return {name: ele_id for name, ele_id in elements.items() if ele_id in self._elements}

    def get_id_by_name(self, name: Union[str, List[str]], name2id=None) -> str:
        if name2id is None:
            name2id = self._name2id

        if isinstance(name, str):
            return name2id.get(name, name)
        return [self.get_id_by_name(n, name2id) for n in name]

    def get_name_by_id(self, elem_id: Union[str, List[str]], id2name=None) -> str:
        if id2name is None:
            id2name = {v: k for k, v in self._name2id.items()}

        if isinstance(elem_id, str):
            return id2name.get(elem_id, elem_id)
        return [self.get_name_by_id(n, id2name) for n in elem_id]

    def read_attrs(self, key: str):
        key_id = self.get_id_by_name(key)
        if self._elements is not None and key_id not in self._elements:
            raise KeyError(key)
        return self.group[key_id].attrs.asdict()

    def keys(self):
        return self._name2id.keys()

    def repr(self):
        return (f"{type(self).__name__}: {', '.join(self.keys())}")

    def __repr__(self):
        str_obj = f"{type(self).__name__} at path `{self._path}`"
        if len(self.keys()) > 0:
            str_obj += f" with elements: {', '.join(self.keys())}"
        return str_obj

    def __contains__(self, key: str):
        return key in self.keys() or key in self._name2id.values()

    def __iter__(self):
        yield from self.keys()

    def __len__(self):
        return len(self.keys())
