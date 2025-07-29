import os
import logging
from typing import List, Optional, Union
from requests.auth import HTTPBasicAuth

import zarr

from . import _constants as constants
from ._utils import time_cache
from ._api import Connector, ZarrElement, OpenAPI, PyAPI
from ._anndata import ConnectorAnnData


DEBUG_MODE = os.environ.get("DEBUG_MODE", "") == "TRUE"
DEFAULT_LOGGER = logging.getLogger("spatialx_sdks_stdout")


def transform_images(images, transformation):
    from spatial_image import SpatialImage
    from dask import array as dask_array
    from spatialdata import transform
    from spatialdata.transformations._utils import _set_transformations

    spimages = SpatialImage(
        dask_array.from_array(images["0"][:]),
        dims=("c", "y", "x"),
    )
    _set_transformations(spimages, {"trans": transformation})
    return transform(spimages, to_coordinate_system="trans")


def get_images(images: zarr.Group, resolution_level: int = 3):
    from spatialdata.transformations import (
        Affine,
        Scale,
        Sequence,
        Translation,
        Identity,
    )
    from spatialdata.transformations._utils import _set_transformations

    data = images[resolution_level]

    transformation = Identity()
    if "btr_global_transformation" in images.attrs:
        transformation = Affine(
            images.attrs["btr_global_transformation"],
            input_axes=("x", "y", "z"),
            output_axes=("x", "y", "z"),
        ).to_affine(
            input_axes=("x", "y"),
            output_axes=("x", "y"),
        )
    elif "scalefactors" in images.attrs or "translation" in images.attrs:
        transformation = []
        if "scalefactors" in images.attrs:
            transformation.append(
                Scale(
                    [images.attrs["scalefactors"], images.attrs["scalefactors"]],
                    axes=("x", "y"),
                )
            )
        if "scalefactors" in images.attrs:
            transformation.append(
                Translation(images.attrs["translation"], axes=("x", "y"))
            )
        transformation = Sequence(transformation).to_affine(
            input_axes=("x", "y"),
            output_axes=("x", "y"),
        )

    transformation = Sequence([
        Scale([2 ** resolution_level, 2 ** resolution_level], axes=("x", "y")),
        transformation,
        Scale([1 / 2 ** resolution_level, 1 / 2 ** resolution_level], axes=("x", "y"))
    ]).to_affine(
        input_axes=("x", "y"),
        output_axes=("x", "y"),
    )

    data = transform_images(data, transformation)
    transformation = Sequence([
        Translation(data.transform["transformation"].translation, axes=("x", "y")),
        Scale([2 ** resolution_level, 2 ** resolution_level], axes=("x", "y")),
    ]).to_affine(
        input_axes=("x", "y"),
        output_axes=("x", "y"),
    )
    _set_transformations(data, {"origin": transformation})
    return data


class Images(ZarrElement):
    def __getitem__(self, key: str):
        return self.group[self.get_id_by_name(key)]

    def get_images(self, key: str, resolution_level: int = 3):
        return get_images(self[key], resolution_level=resolution_level)

    def get_channel_names(self, elem: Union[str, zarr.Group]):
        if isinstance(elem, str):
            elem = self[elem]
        for attr in elem.attrs.asdict().values():
            if isinstance(attr, dict) and constants.SpatialAttrs.CHANNELS_KEY.value in attr:
                return [
                    name[constants.SpatialAttrs.CHANNEL_LABEL.value]
                    for name in attr[constants.SpatialAttrs.CHANNELS_KEY.value]
                ]
        return []

    def set_channel_names(self, elem: Union[str, zarr.Group], channel_names: List[str]):
        if isinstance(elem, str):
            elem = self[elem]
        pyapi: PyAPI = self.self_init(PyAPI)
        return pyapi.rename_image_channels(
            self._extend_information[constants.ConnectorKeys.STUDY_ID.value],
            self._extend_information[constants.ConnectorKeys.SAMPLE_ID.value],
            self.get_id_by_name(elem.path),
            channel_names,
        )


class Shapes(ZarrElement):
    def __getitem__(self, key: str):
        import numpy as np
        from geopandas import GeoDataFrame
        from spatialdata._io.io_shapes import (
            ShapesFormats,
            ShapesFormatV01,
            _parse_version,
            from_ragged_array,
            _get_transformations_from_ngff_dict,
            _set_transformations,
        )

        def _read_shapes(store: zarr.Group) -> GeoDataFrame:
            """Read shapes from a zarr store."""
            f = zarr.open(store, mode="r")
            attrs = f.attrs.asdict()
            version = _parse_version(f, expect_attrs_key=True)
            assert version is not None
            format = ShapesFormats[version]

            if isinstance(format, ShapesFormatV01):
                coords = np.array(f["coords"][:])
                index = np.array(f["Index"][:])
                typ = format.attrs_from_dict(attrs)
                if typ.name == "POINT":
                    radius = np.array(f["radius"][:])
                    geometry = from_ragged_array(typ, coords)
                    geo_df = GeoDataFrame({"geometry": geometry, "radius": radius}, index=index)
                else:
                    offsets = []
                    for i in range(3):
                        try:
                            offsets.append(np.array(f[f"offset{i}"][:]).flatten())
                        except:
                            break
                    geometry = from_ragged_array(typ, coords, offsets)
                    geo_df = GeoDataFrame({"geometry": geometry}, index=index)
            else:
                raise ValueError(
                    f"Unsupported shapes format {format} from version {version}. "
                    "Please update the spatialdata library."
                )

            transformations = _get_transformations_from_ngff_dict(attrs["coordinateTransformations"])
            _set_transformations(geo_df, transformations)

            if constants.ConnectorKeys.MPP.value in attrs:
                geo_df[constants.ConnectorKeys.MPP.value] = attrs[constants.ConnectorKeys.MPP.value]

            return geo_df

        return _read_shapes(
            self._open_zarr_root(os.path.join(self._path, self.get_id_by_name(key)))
        )

    def simplify(self, key: str, tolerance: Optional[float]):
        pyapi: PyAPI = self.self_init(PyAPI)
        return pyapi.simplify_segmentation(
            self._extend_information[constants.ConnectorKeys.STUDY_ID.value],
            self._extend_information[constants.ConnectorKeys.SAMPLE_ID.value],
            self.get_id_by_name(key),
            tolerance,
        )


class Points(ZarrElement):
    def __getitem__(self, key: str):
        import io
        import requests

        import zarr
        import pandas as pd
        import dask
        from dask import dataframe as dd
        from spatialdata._io.io_points import (
            DaskDataFrame,
            PointsFormats,
            _parse_version,
            _get_transformations_from_ngff_dict,
            _set_transformations,
        )

        @dask.delayed
        def parquet_from_http(url, headers=None, meta=None):
            result = requests.get(url, headers=headers)
            df = pd.read_parquet(io.BytesIO(result.content))
            if meta is not None:
                for k, v in meta.items():
                    df[k] = v
            return df

        key = self.get_id_by_name(key)
        group = zarr.open(self._open_zarr_root(os.path.join(self._path, key)))
        attrs = group.attrs.asdict()
        root_path = os.path.join(
            self._get_zarr_path(os.path.join(self._path, key)),
            "points.parquet",
        )

        paths = []
        divisions = tuple(attrs["divisions"])
        genes = list(attrs.get("gene_to_partition", {}).keys())
        for i in range(len(divisions) - 1):
            paths.append(os.path.join(root_path, f"part.{i}.parquet"))

        delayed_download = [
            parquet_from_http(
                path,
                headers=self._headers,
                meta=None if not genes else dict(gene=genes[i]),
            )
            for i, path in enumerate(paths)
        ]
        points: DaskDataFrame = dd.from_delayed(delayed_download, divisions=divisions)

        version = _parse_version(group, expect_attrs_key=True)
        assert version is not None

        transformations = _get_transformations_from_ngff_dict(attrs["coordinateTransformations"])
        _set_transformations(points, transformations)

        if constants.ConnectorKeys.MPP.value in attrs:
            points[constants.ConnectorKeys.MPP.value] = attrs[constants.ConnectorKeys.MPP.value]

        p_attrs = PointsFormats[version].attrs_from_dict(attrs)
        if len(p_attrs):
            points.attrs["spatialdata_attrs"] = p_attrs

        return points


class Tables(ZarrElement):
    def __getitem__(self, key: str):
        key = self.get_id_by_name(key)
        return self.self_init(
            ConnectorAnnData,
            path=os.path.join(self._path, key),
            extend_information={constants.ConnectorKeys.TABLE_ID.value: key},
        )


class SpatialData(Connector):
    def __init__(
        self,
        domain: str,
        token: str,
        data_id: Optional[str] = None,
        sample_id: Optional[str] = None,
        verify_ssl: bool = False,
        authentication: Optional[HTTPBasicAuth] = None,
    ):
        openapi = OpenAPI(domain, token, verify_ssl=verify_ssl, authentication=authentication)
        if sample_id is not None:
            details = openapi.get_sample_detail(sample_id)[constants.ConnectorKeys.SAMPLE.value]
            self.elements = None
        elif data_id is not None:
            details = openapi.get_sample_data_detail(data_id)

            submitted_elements: dict = details.get("map_submit_result", {})
            elements: List[str] = []
            for value in submitted_elements.values():
                if not isinstance(value, dict):
                    continue
                for v in value.values():
                    elements.extend(v.keys() if isinstance(v, dict) else [v])
            self.elements = elements

        self.study_id = details[constants.ConnectorKeys.STUDY_ID.value]
        self.sample_id = details[constants.ConnectorKeys.SAMPLE_ID.value]
        self.data_id = data_id
        study_path = openapi.get_study_detail(
            self.study_id
        )[constants.ConnectorKeys.STUDY.value][constants.ConnectorKeys.DATA_PATH.value]
        self._path = f"{study_path}/spatial/{self.sample_id}"

        super().__init__(
            domain, token,
            verify_ssl=verify_ssl,
            authentication=authentication,
        )

    def _init_attribute(self, Attribute, key: str):
        return self.self_init(
            Attribute,
            path=os.path.join(self._path, key),
            elements=self.elements,
            extend_information={
                constants.ConnectorKeys.DATA_ID.value: self.data_id,
                constants.ConnectorKeys.STUDY_ID.value: self.study_id,
                constants.ConnectorKeys.SAMPLE_ID.value: self.sample_id,
            },
        )

    @property
    @time_cache(5)
    def images(self) -> Images:
        return self._init_attribute(Images, "images")

    @property
    @time_cache(5)
    def shapes(self) -> Shapes:
        return self._init_attribute(Shapes, "shapes")

    @property
    @time_cache(5)
    def points(self) -> Points:
        return self._init_attribute(Points, "points")

    @property
    @time_cache(5)
    def tables(self) -> Tables:
        return self._init_attribute(Tables, "table")

    def __repr__(self):
        obj_str = f"{type(self).__name__} with elements:"
        for key in ["images", "shapes", "points", "tables"]:
            element: ZarrElement = getattr(self, key)
            if len(element.keys()) == 0:
                continue
            obj_str += "\n\t" + element.repr()
        return obj_str
