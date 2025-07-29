from typing import Optional, Literal, List, Union
import numpy as np

from ..._analysis import Analysis
from ..._anndata import ConnectorAnnData
from ... import _constants as constants


def rank_genes_groups(
    adata: ConnectorAnnData,
    groupby: str,
    groups: Union[List[str], str],
    reference: Union[List[str], str] = "rest",
    method: Literal["venice", "t-test", "wilcoxon"] = "venice",
    normalize_method: Optional[
        Literal[
            constants.NormalizeMethod.RAW,
            constants.NormalizeMethod.LOG1P_NORMALIZE,
            constants.NormalizeMethod.SQRT_NORMALIZE,
        ]
    ] = constants.NormalizeMethod.LOG1P_NORMALIZE,
    title: Optional[str] = None,
    **kwargs,
):
    """
    Spatial Region Segmentation.

    Parameters
    ----------
    method: `Literal["venice", "t-test", "wilcoxon"]`, Default: "venice"
        Test statistic method.
    normalize_method: `Literal["raw", "log1p-normalized", "sqrt-normalized"]`, Default: "log1p-normalized"
        Using raw expression or scaling (log1p, square root) for test statistic.
    title: `Optional[str]`, Default: None
        Title of analysis, it will be used as name of embeddings.
        If not provided, a default name will be used.
    """
    metadata = adata.obs[groupby].values

    if isinstance(groups, str):
        groups = [groups]
    group_1_indices = np.where(np.isin(metadata, groups))[0]
    if len(group_1_indices) == 0:
        raise ValueError(f"Not found any cells in {groups}.")
    group_1_name = str(groups)

    if reference == "rest":
        group_2_indices = np.where(~np.isin(metadata, groups))[0]
        group_2_name = "rest"
    else:
        if isinstance(reference, str):
            reference = [reference]
        group_2_indices = np.where(np.isin(metadata, reference))[0]
        group_2_name = str(reference)

    data_id_1 = data_id_2 = adata._extend_information[constants.ConnectorKeys.DATA_ID.value]

    analysis = adata.self_init(Analysis)
    analysis.de.differential_expression_genes(
        data_id_1=data_id_1,
        data_id_2=data_id_2,
        group_1_indices=group_1_indices.tolist(),
        group_2_indices=group_2_indices.tolist(),
        group_1_name=group_1_name,
        group_2_name=group_2_name,
        method=method,
        normalize_method=normalize_method,
        title=title,
        info_args=adata._extend_information,
        **kwargs,
    )
