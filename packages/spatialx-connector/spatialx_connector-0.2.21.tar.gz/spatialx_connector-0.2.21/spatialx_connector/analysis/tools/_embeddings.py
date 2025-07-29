from typing import Literal, Optional

from ..._analysis import Analysis
from ..._anndata import ConnectorAnnData


def umap(
    adata: ConnectorAnnData,
    embedding_key: str,
    n_neighbors: int = 15,
    local_connectivity: float = 1,
    init: Literal["pca", "spectral", "random"] = "pca",
    deterministic: bool = True,
    title: Optional[str] = None,
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
    analysis = adata.self_init(Analysis)
    analysis.embeddings.umap(
        embedding_key=embedding_key,
        title=title,
        n_neighbors=n_neighbors,
        local_connectivity=local_connectivity,
        init=init,
        deterministic=deterministic,
        info_args=adata._extend_information,
        **kwargs,
    )
    adata.update()


def tsne(
    adata: ConnectorAnnData,
    embedding_key: str,
    n_neighbors: int = 90,
    perplexity: float = 30,
    local_connectivity: float = 1,
    init: Literal["pca", "gaussian", "input"] = "pca",
    title: Optional[str] = None,
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
    analysis = adata.self_init(Analysis)
    analysis.embeddings.tsne(
        embedding_key=embedding_key,
        n_neighbors=n_neighbors,
        perplexity=perplexity,
        local_connectivity=local_connectivity,
        init=init,
        title=title,
        info_args=adata._extend_information,
        **kwargs,
    )
    adata.update()
