import os
from enum import Enum
from typing import Optional, Dict, Literal, List

import json
from requests.auth import HTTPBasicAuth

from . import _constants as constants
from ._api import OpenAPI, PyAPI


class BaseAnalysis(OpenAPI):
    def _extract_id(self, data_id: str, table_id: Optional[str] = None):
        data_details = self.get_sample_data_detail(data_id)
        study_id = data_details[constants.ConnectorKeys.STUDY_ID.value]
        sample_id = data_details[constants.ConnectorKeys.SAMPLE_ID.value]
        if table_id is None:
            table_results = []
            submitted_results: Dict[str, Dict[str, dict]] = \
                data_details[constants.ConnectorKeys.MAP_SUBMIT_RESULT.value]
            for _, res in submitted_results.items():
                table_results.extend(
                    res.get(constants.ConnectorKeys.ANNOTATED_DATA.value, {}).keys())
            if len(table_results) == 0:
                raise RuntimeError("Not found any annotated data.")
            if len(table_results) > 1:
                raise RuntimeError(
                    f"Found too many annotated data: {table_results}. "
                    "Please identify an ID by `table_id=...`"
                )
            table_id = table_results[0]
        return study_id, sample_id, table_id

    def _post_analysis(
        self,
        title: str,
        params: dict,
        sub_type: str,
        group_type: str,
        data_id: Optional[str] = None,
        study_id: Optional[str] = None,
        sample_id: Optional[str] = None,
        table_id: Optional[str] = None,
        **_,
    ):
        if data_id is not None:
            ext_study_id, ext_sample_id, ext_table_id = self._extract_id(data_id, table_id=table_id)
            study_id = study_id if study_id is not None else ext_study_id
            sample_id = sample_id if sample_id is not None else ext_sample_id
            table_id = table_id if table_id is not None else ext_table_id

        analysis_result = self.post_openapi_request(
            url=constants.CREATE_ANALYSIS_URL,
            json={
                constants.ConnectorKeys.DATA.value: {
                    constants.ConnectorKeys.TITLE.value: title,
                    constants.ConnectorKeys.PARAMS.value: json.dumps(params),
                    constants.ConnectorKeys.DISPLAY_PARAMS.value: json.dumps({}),
                    constants.ConnectorKeys.SUB_TYPE.value: sub_type,
                    constants.ConnectorKeys.GROUP_TYPE.value: group_type,
                    constants.ConnectorKeys.DESCRIPTION.value: title,
                },
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.SAMPLE_ID.value: sample_id,
                constants.ConnectorKeys.DATA_ID.value: data_id,
                constants.ConnectorKeys.TABLE_ID.value: table_id,
            }
        )
        analysis_id = analysis_result[constants.ConnectorKeys.ANALYSIS_ID.value]
        log_path = os.path.join(
            self.get_study_detail(study_id)[constants.ConnectorKeys.STUDY.value][
                constants.ConnectorKeys.DATA_PATH.value
            ],
            f"analysis/{analysis_id}/analysis.log"
        )
        self.tracking_log(log_path)


class Embeddings(BaseAnalysis):
    def pca(
        self,
        normalize_method: Optional[
            Literal[
                constants.NormalizeMethod.RAW,
                constants.NormalizeMethod.LOG1P_NORMALIZE,
                constants.NormalizeMethod.SQRT_NORMALIZE,
            ]
        ] = constants.NormalizeMethod.LOG1P_NORMALIZE,
        title: Optional[str] = None,
        batch_key: Optional[str] = None,
        n_top_genes: Optional[int] = None,
        info_args: dict = None,
        **kwargs,
    ):
        """
        Principal Component Analysis

        Parameters
        ----------
        normalize_method: `Literal["raw", "log1p-normalized", "sqrt-normalized"]`, Default: "log1p-normalized"
            Using raw expression or scaling (log1p, square root) to normalize when running PCA.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        batch_key: `Optional[str]`, Default: None
            Metadata which defines batch effect.
            If provided, using Harmony to remove batch effect.
        n_top_genes: `Optional[int]`, Default: None
            Number of top highly variable genes.
            If provided, running highly variable genes to select genes for PCA.
        """
        if isinstance(normalize_method, Enum):
            normalize_method = normalize_method.value

        if info_args is None:
            info_args = {}

        return self._post_analysis(
            title=title if title is not None else "PCA",
            params={
                "normalize_method": normalize_method,
                "name": title,
                "batch_key": batch_key,
                "n_top_genes": n_top_genes,
                **kwargs,
            },
            sub_type="PCA",
            group_type="embedding",
            **info_args,
            **kwargs,
        )

    def scvi(
        self,
        n_latents: int = 20,
        title: Optional[str] = None,
        batch_key: Optional[str] = None,
        n_top_genes: Optional[int] = 2000,
        info_args: dict = None,
        **kwargs,
    ):
        """
        Reducing dimensions with scVI

        Parameters
        ----------
        n_latents: `int`, Default: 20
            Number of latents.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        batch_key: `Optional[str]`, Default: None
            Metadata which defines batch effect.
            If provided, using Harmony to remove batch effect.
        n_top_genes: `Optional[int]`, Default: 2000
            Number of top highly variable genes.
            If provided, running highly variable genes to select genes for PCA.
        """
        if info_args is None:
            info_args = {}

        return self._post_analysis(
            title=title if title is not None else "scVI",
            params={
                "n_latents": n_latents,
                "name": title,
                "batch_key": batch_key,
                "n_top_genes": n_top_genes,
                **kwargs,
            },
            sub_type="scVI",
            group_type="embedding",
            **info_args,
            **kwargs,
        )

    def umap(
        self,
        embedding_key: str,
        n_neighbors: int = 15,
        local_connectivity: float = 1,
        init: Literal["pca", "spectral", "random"] = "pca",
        deterministic: bool = True,
        title: Optional[str] = None,
        info_args: dict = None,
        **kwargs,
    ):
        """
        Uniform Manifold Approximation and Projection for Dimension Reduction.

        Parameters
        ----------
        embedding_key: `str`
            Embedding to run UMAP, should be result of PCA or scVI.
        n_neighbors : Optional[`int`], Default: None
            The number of nearest neighbors.
        local_connectivity : `float`, Default: 1.0
            The local connectivity required -- i.e. the number of nearest
            neighbors that should be assumed to be connected at a local level.
            The higher this value the more connected the manifold becomes
            locally. In practice this should be not more than the local intrinsic
            dimension of the manifold.
        init : `str`, Default: "pca"
            How to initialize the low dimensional embedding. Options are:
            * `"spectral"` : use a spectral embedding of the fuzzy 1-skeleton (non-deterministic).
            * `"random"` : assign initial embedding positions at random.
            * `"pca"` : pca low dimensions of input matrix.
        deterministic : `bool`, Default: True
            Making sure with same initialization, results will remains the same across runs on the same device.
            Deterministic version will converge a lot slower on big datasets (hence lower quality on same setting).
            If you prefer quality/performance, disable `deterministic`
            Note: `"spectral"` initialization is non-deterministic across runs.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        """
        if info_args is None:
            info_args = {}

        return self._post_analysis(
            title=title if title is not None else "UMAP",
            params={
                "embedding_key": embedding_key,
                "n_neighbors": n_neighbors,
                "local_connectivity": local_connectivity,
                "init": init,
                "deterministic": deterministic,
                "name": title,
                **kwargs,
            },
            sub_type="UMAP",
            group_type="embedding",
            **info_args,
            **kwargs,
        )

    def tsne(
        self,
        embedding_key: str,
        n_neighbors: int = 90,
        perplexity: float = 30,
        local_connectivity: float = 1,
        init: Literal["pca", "gaussian", "input"] = "pca",
        title: Optional[str] = None,
        info_args: dict = None,
        **kwargs,
    ):
        """
        FFT-accelerated Interpolation-based t-SNE implementation.

        Parameters
        ----------
        embedding_key: `str`
            Embedding to run UMAP, should be result of PCA or scVI.
        n_neighbors : Optional[`int`], Default: None
            The number of nearest neighbors.
        perplexity : ``float``, default = ``30``
            The perplexity is related to the number of nearest neighbors that is used in
            other manifold learning algorithms.
            Larger datasets usually require a larger perplexity.
            Consider selecting a value between ``5`` and ``50``.
            Different values can result in significantly different results.
        local_connectivity : `float`, Default: 1.0
            The local connectivity required -- i.e. the number of nearest
            neighbors that should be assumed to be connected at a local level.
            The higher this value the more connected the manifold becomes
            locally. In practice this should be not more than the local intrinsic
            dimension of the manifold.
        init : `str`, Default: "pca"
            How to initialize the low dimensional embedding. Options are:
            * ``"gaussian"`` : init using gaussian noise.
            * ``"input"`` : 2 first row input matrix.
            * ``"pca"`` : pca 2 first row input matrix.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        """
        if info_args is None:
            info_args = {}

        return self._post_analysis(
            title=title if title is not None else "t-SNE",
            params={
                "embedding_key": embedding_key,
                "n_neighbors": n_neighbors,
                "local_connectivity": local_connectivity,
                "init": init,
                "perplexity": perplexity,
                "name": title,
                **kwargs,
            },
            sub_type="t-SNE",
            group_type="embedding",
            **info_args,
            **kwargs,
        )

    def upload_embeddings(
        self,
        csv_path: str,
        info_args: dict = None,
        **kwargs,
    ):
        if info_args is None:
            info_args = {}

        return self._post_analysis(
            title="Import Embeddings",
            params={"csv_path": csv_path, **kwargs},
            sub_type="import_embeddings",
            group_type="embedding",
            **info_args,
            **kwargs,
        )


class Clustering(BaseAnalysis):
    def louvain(
        self,
        embedding_key: str,
        resolution: float,
        n_neighbors: int = 90,
        local_connectivity: float = 1,
        title: Optional[str] = None,
        info_args: dict = None,
        **kwargs,
    ):
        """
        Louvain clustering implementation.

        Parameters
        ----------
        embedding_key: `str`
            Embedding to run UMAP, should be result of PCA or scVI.
        resolution : ``float``
            Resolution parameter, higher lead to more communities.
        n_neighbors : Optional[`int`], Default: None
            The number of nearest neighbors.
        local_connectivity : `float`, Default: 1.0
            The local connectivity required -- i.e. the number of nearest
            neighbors that should be assumed to be connected at a local level.
            The higher this value the more connected the manifold becomes
            locally. In practice this should be not more than the local intrinsic
            dimension of the manifold.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        """
        if info_args is None:
            info_args = {}

        return self._post_analysis(
            title=title if title is not None else "Louvain",
            params={
                "embedding_key": embedding_key,
                "resolution": resolution,
                "n_neighbors": n_neighbors,
                "local_connectivity": local_connectivity,
                "name": title,
                **kwargs,
            },
            sub_type="Louvain",
            group_type="clustering",
            **info_args,
            **kwargs,
        )

    def leiden(
        self,
        embedding_key: str,
        resolution: float,
        n_neighbors: int = 90,
        local_connectivity: float = 1,
        title: Optional[str] = None,
        info_args: dict = None,
        **kwargs,
    ):
        """
        Leiden clustering implementation.

        Parameters
        ----------
        embedding_key: `str`
            Embedding to run UMAP, should be result of PCA or scVI.
        resolution : ``float``
            Resolution parameter, higher lead to more communities.
        n_neighbors : Optional[`int`], Default: None
            The number of nearest neighbors.
        local_connectivity : `float`, Default: 1.0
            The local connectivity required -- i.e. the number of nearest
            neighbors that should be assumed to be connected at a local level.
            The higher this value the more connected the manifold becomes
            locally. In practice this should be not more than the local intrinsic
            dimension of the manifold.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        """
        if info_args is None:
            info_args = {}

        return self._post_analysis(
            title=title if title is not None else "Leiden",
            params={
                "embedding_key": embedding_key,
                "resolution": resolution,
                "n_neighbors": n_neighbors,
                "local_connectivity": local_connectivity,
                "name": title,
                **kwargs,
            },
            sub_type="Leiden",
            group_type="clustering",
            **info_args,
            **kwargs,
        )

    def kmeans(
        self,
        embedding_key: str,
        n_clusters: int,
        title: Optional[str] = None,
        info_args: dict = None,
        **kwargs,
    ):
        """
        k-means clustering implementation.

        Parameters
        ----------
        embedding_key: `str`
            Embedding to run UMAP, should be result of PCA or scVI.
        n_clusters: ``int``
            Number of clusters.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        """
        if info_args is None:
            info_args = {}

        return self._post_analysis(
            title=title if title is not None else "k-means",
            params={
                "embedding_key": embedding_key,
                "n_clusters": n_clusters,
                "name": title,
                **kwargs,
            },
            sub_type="k-means",
            group_type="clustering",
            **info_args,
            **kwargs,
        )


class DE(BaseAnalysis):
    def differential_expression_genes(
        self,
        data_id_1: str,
        data_id_2: str,
        group_1_indices: List[int],
        group_2_indices: List[int],
        group_1_name: str = "Group 1",
        group_2_name: str = "Group 2",
        method: Literal["venice", "t-test", "wilcoxon"] = "venice",
        normalize_method: Optional[
            Literal[
                constants.NormalizeMethod.RAW,
                constants.NormalizeMethod.LOG1P_NORMALIZE,
                constants.NormalizeMethod.SQRT_NORMALIZE,
            ]
        ] = constants.NormalizeMethod.LOG1P_NORMALIZE,
        title: Optional[str] = None,
        info_args: dict = None,
        **kwargs,
    ):
        """
        Spatial Region Segmentation.

        Parameters
        ----------
        data_id_1: `str`
            ID of the first data to run differential expression genes.
        data_id_2: `str`
            ID of the second data to run differential expression genes.
        group_1_indices: `List[int]`
            Cell indices to compare in the first group.
        group_2_indices: `List[int]`
            Cell indices to compare in the second group.
        group_1_name: `str`, Default: "Group 1"
            Name of the first group.
        group_2_name: `str`, Default: "Group 2"
            Name of the second group.
        method: `Literal["venice", "t-test", "wilcoxon"]`, Default: "venice"
            Test statistic method.
        normalize_method: `Literal["raw", "log1p-normalized", "sqrt-normalized"]`, Default: "log1p-normalized"
            Using raw expression or scaling (log1p, square root) for test statistic.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        """
        if info_args is None:
            info_args = {}

        _, sample_id_1, table_id_1 = self._extract_id(data_id_1)
        _, sample_id_2, table_id_2 = self._extract_id(data_id_2)
        if isinstance(normalize_method, Enum):
            normalize_method = normalize_method.value

        return self._post_analysis(
            title=title if title is not None else "DE genes",
            params={
                "group_1_indices": group_1_indices,
                "group_2_indices": group_2_indices,
                "group_1_name": group_1_name,
                "group_2_name": group_2_name,
                "method": method,
                "normalize_method": normalize_method,
                "sample_id_1": sample_id_1,
                "sample_id_2": sample_id_2,
                "table_id_1": table_id_1,
                "table_id_2": table_id_2,
                "name": title,
                **kwargs,
            },
            sub_type="de_genes",
            group_type="deg",
            **info_args,
            **kwargs,
        )


class Prediction(BaseAnalysis):
    def metadata_reference(
        self,
        cluster_key: str,
        species: str,
        anno_type: Literal["sub", "major"] = "sub",
        title: Optional[str] = None,
        info_args: dict = None,
        **kwargs,
    ):
        """
        Spatial Region Segmentation.

        Parameters
        ----------
        cluster_key: `str`
            Cluster to predict cell types.
        species: `str`
            Species of data.
        anno_type: `Literal["sub", "major"]`, Default: "sub"
            Type of annotation: Major or sub cell types.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        """
        if info_args is None:
            info_args = {}

        return self._post_analysis(
            title=title if title is not None else "Metadata Reference",
            params={
                "cluster_key": cluster_key,
                "anno_type": anno_type,
                "species": species,
                "name": title,
                **kwargs,
            },
            sub_type="celltype_prediction",
            group_type="prediction",
            **info_args,
            **kwargs,
        )

    def list_deconvolution_models(self):
        return self.self_init(PyAPI).list_deconvolution_models()

    def deconvolution(
        self,
        model_id: str,
        title: Optional[str] = None,
        n_cells_per_location: int = 30,
        detection_alpha: int = 20,
        info_args: dict = None,
        **kwargs,
    ):
        """
        Spatial Region Segmentation.

        Parameters
        ----------
        model_id: `str`
            Deconvolution model id.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        """
        if info_args is None:
            info_args = {}

        return self._post_analysis(
            title=title if title is not None else "Deconvolution",
            params=dict(
                model_id=model_id,
                name=title,
                n_cells_per_location=n_cells_per_location,
                detection_alpha=detection_alpha,
            ),
            sub_type="deconvolution",
            group_type="prediction",
            **info_args,
            **kwargs,
        )


class SpatialAnalysis(BaseAnalysis):
    def region_segmentation(
        self,
        radius: float,
        mpp: float,
        species: str,
        resolution: float = 0.5,
        title: Optional[str] = None,
        info_args: dict = None,
        **kwargs,
    ):
        """
        Spatial Region Segmentation.

        Parameters
        ----------
        radius: `float`
            Radius (micrometer) to build spatial graph
        mpp: `float`
            Micrometers per pixel.
        species: `str`
            Species of data.
        resolution : ``float``, Default: 0.5
            Resolution parameter, higher lead to more communities.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        """
        if info_args is None:
            info_args = {}

        data_id = info_args.get("data_id", None)
        transcripts_id = None
        spots_id = None
        if data_id is not None:
            data_details = self.get_sample_data_detail(data_id)
            transcripts = []
            spots = []
            submitted_results: Dict[str, Dict[str, dict]] = \
                data_details[constants.ConnectorKeys.MAP_SUBMIT_RESULT.value]
            for _, res in submitted_results.items():
                transcripts.extend(res.get(constants.ConnectorKeys.TRANSCRIPTS.value, {}).keys())
                spots.extend(res.get(constants.ConnectorKeys.SPOT.value, {}).keys())
            transcripts_id = transcripts[0] if len(transcripts) > 0 else None
            spots_id = spots[0] if len(spots) > 0 else None

        return self._post_analysis(
            title=title if title is not None else "Region Segmentation",
            params={
                "radius": radius,
                "mpp": mpp,
                "resolution": resolution,
                "species": species,
                "transcripts_id": transcripts_id,
                "spots_id": spots_id,
                "name": title,
                **kwargs,
            },
            sub_type="segmentation_by_spatial_correlation",
            group_type="svg",
            **info_args,
            **kwargs,
        )

    def neighborhood_analysis(
        self,
        radius: float,
        mpp: float,
        annotation_key: str = "",
        deconvolution_key: str = "",
        tau: Optional[float] = None,
        n_centroids: int = 30,
        title: Optional[str] = None,
        info_args: dict = None,
        **kwargs,
    ):
        """
        Spatial Neighborhood Analysis.

        Parameters
        ----------
        radius: `float`
            Radius (micrometer) to build spatial graph
        mpp: `float`
            Micrometers per pixel.
        annotation_key: `str`
            Metadata of cell-type to perform cell-type neighborhood analysis
        deconvolution_key: `str`
            Metadata of deconvolution_key cell-type to perform cell-type neighborhood analysis
        tau : `Optional[float]`
            Facilitating fine-tuned modulation of the impact of neighboring cells.
        n_centroids: `int`
            Number of centroids to run hierarchical clustering.
        title: `Optional[str]`, Default: None
            Title of analysis, it will be used as name of embeddings.
            If not provided, a default name will be used.
        """
        if info_args is None:
            info_args = {}

        if (len(annotation_key) == 0 and len(deconvolution_key) == 0) or \
                (len(annotation_key) > 0 and len(deconvolution_key) > 0):
            raise ValueError("Request exactly one of `annotation_key` or `deconvolution_key`")
        if len(annotation_key) > 0:
            sub_type = "neighborhood_proportions_analysis"
        else:
            sub_type = "deconvolution_neighborhood_analysis"

        return self._post_analysis(
            title=title if title is not None else "Neighborhood Analysis",
            params=dict(
                radius=radius,
                mpp=mpp,
                annotation_key=annotation_key,
                deconvolution_key=deconvolution_key,
                tau=tau,
                n_centroids=n_centroids,
                name=title,
            ),
            sub_type=sub_type,
            group_type="neighborhood",
            **info_args,
            **kwargs,
        )


class Analysis(BaseAnalysis):
    def __init__(
        self,
        domain: str,
        token: str,
        verify_ssl: bool = False,
        authentication: Optional[HTTPBasicAuth] = None,
        **_,
    ):
        super().__init__(domain, token, verify_ssl=verify_ssl, authentication=authentication)
        self.embeddings = self.self_init(Embeddings)
        self.clustering = self.self_init(Clustering)
        self.de = self.self_init(DE)
        self.prediction = self.self_init(Prediction)
        self.spatial_analysis = self.self_init(SpatialAnalysis)

    def list_metadata(self, data_id: str):
        study_id, sample_id, table_id = self._extract_id(data_id)
        return self.post_pyapi_request(
            url=constants.GET_ANNOTATED_ELEMENTS,
            json={
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.SAMPLE_ID.value: sample_id,
                constants.ConnectorKeys.TABLE_ID.value: table_id,
                constants.ConnectorKeys.ELEMENT.value: constants.ConnectorKeys.OBS.value,
            },
        )

    def list_embedding(self, data_id: str):
        study_id, sample_id, table_id = self._extract_id(data_id)
        return self.post_pyapi_request(
            url=constants.GET_ANNOTATED_ELEMENTS,
            json={
                constants.ConnectorKeys.STUDY_ID.value: study_id,
                constants.ConnectorKeys.SAMPLE_ID.value: sample_id,
                constants.ConnectorKeys.TABLE_ID.value: table_id,
                constants.ConnectorKeys.ELEMENT.value: constants.ConnectorKeys.OBSM.value,
            },
        )
