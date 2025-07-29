from typing import Optional, Literal

from ..._api import PyAPI
from ..._analysis import Analysis
from ..._anndata import ConnectorAnnData
from ..._constants import Species


def metadata_reference(
    adata: ConnectorAnnData,
    cluster_key: str,
    species: Literal[Species.HUMAN, Species.MOUSE],
    annotation_type: Literal["sub", "major"] = "sub",
    title: Optional[str] = None,
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
    annotation_type: `Literal["sub", "major"]`, Default: "sub"
        Type of annotation: Major or sub cell types.
    title: `Optional[str]`, Default: None
        Title of analysis, it will be used as name of embeddings.
        If not provided, a default name will be used.
    """
    analysis = adata.self_init(Analysis)
    analysis.prediction.metadata_reference(
        cluster_key=cluster_key,
        species=species,
        anno_type=annotation_type,
        title=title,
        info_args=adata._extend_information,
        **kwargs,
    )
    adata.update()


def list_deconvolution_models(adata: ConnectorAnnData):
    return adata.self_init(PyAPI).list_deconvolution_models()


def deconvolution(
    adata: ConnectorAnnData,
    model_id: str,
    title: Optional[str] = None,
    n_cells_per_location: int = 30,
    detection_alpha: int = 20,
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
    n_cells_per_location:  `int`
        Estimation of absolute cell abundance is guided using informed prior on the number of cells
    """
    analysis = adata.self_init(Analysis)
    analysis.prediction.deconvolution(
        model_id=model_id,
        title=title,
        n_cells_per_location=n_cells_per_location,
        detection_alpha=detection_alpha,
        info_args=adata._extend_information,
        **kwargs,
    )
    adata.update()
