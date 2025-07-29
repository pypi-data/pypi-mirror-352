from typing import Optional, Literal

from ..._analysis import Analysis
from ..._anndata import ConnectorAnnData
from ... import _constants as constants


def pca(
    adata: ConnectorAnnData,
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
    analysis = adata.self_init(Analysis)
    analysis.embeddings.pca(
        normalize_method=normalize_method,
        title=title,
        batch_key=batch_key,
        n_top_genes=n_top_genes,
        info_args=adata._extend_information,
        **kwargs,
    )
    adata.update()


def scvi(
    adata: ConnectorAnnData,
    n_latents: int = 20,
    title: Optional[str] = None,
    batch_key: Optional[str] = None,
    n_top_genes: Optional[int] = 2000,
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
    analysis = adata.self_init(Analysis)
    analysis.embeddings.scvi(
        n_latents=n_latents,
        title=title,
        batch_key=batch_key,
        n_top_genes=n_top_genes,
        info_args=adata._extend_information,
        **kwargs,
    )
    adata.update()
