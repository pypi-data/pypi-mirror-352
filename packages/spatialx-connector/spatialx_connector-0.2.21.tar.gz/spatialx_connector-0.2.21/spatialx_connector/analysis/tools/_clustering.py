from typing import Optional

from ..._analysis import Analysis
from ..._anndata import ConnectorAnnData


def louvain(
    adata: ConnectorAnnData,
    embedding_key: str,
    resolution: float,
    n_neighbors: int = 90,
    local_connectivity: float = 1,
    title: Optional[str] = None,
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
    analysis = adata.self_init(Analysis)
    analysis.clustering.louvain(
        embedding_key=embedding_key,
        resolution=resolution,
        n_neighbors=n_neighbors,
        local_connectivity=local_connectivity,
        title=title,
        info_args=adata._extend_information,
        **kwargs,
    )
    adata.update()


def leiden(
    adata: ConnectorAnnData,
    embedding_key: str,
    resolution: float,
    n_neighbors: int = 90,
    local_connectivity: float = 1,
    title: Optional[str] = None,
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
    analysis = adata.self_init(Analysis)
    analysis.clustering.leiden(
        embedding_key=embedding_key,
        resolution=resolution,
        n_neighbors=n_neighbors,
        local_connectivity=local_connectivity,
        title=title,
        info_args=adata._extend_information,
        **kwargs,
    )
    adata.update()


def kmeans(
    adata: ConnectorAnnData,
    embedding_key: str,
    n_clusters: int,
    title: Optional[str] = None,
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
    analysis = adata.self_init(Analysis)
    analysis.clustering.kmeans(
        embedding_key=embedding_key,
        n_clusters=n_clusters,
        title=title,
        info_args=adata._extend_information,
        **kwargs,
    )
    adata.update()
