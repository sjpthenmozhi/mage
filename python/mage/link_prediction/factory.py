from typing import List, Tuple
import torch
from mage.link_prediction.models.GraphSAGE import GraphSAGE
from mage.link_prediction.models.GAT import GAT
from mage.link_prediction.predictors.DotPredictor import DotPredictor
from mage.link_prediction.predictors.MLPPredictor import MLPPredictor
from mage.link_prediction.constants import (
    ADAM_OPT,
    SGD_OPT,
    GRAPH_ATTN,
    GRAPH_SAGE,
    DOT_PREDICTOR,
    MLP_PREDICTOR,
)
import itertools


def create_optimizer(
    optimizer_type: str,
    learning_rate: float,
    model: torch.nn.Module,
    predictor: torch.nn.Module,
) -> torch.optim.Optimizer:
    """Creates optimizer with given optimizer type and learning rate.

    Args:
        optimizer_type (str): Type of the optimizer.
        learning_rate (float): Learning rate of the optimizer.
        model (torch.nn.Module): A reference to the already created model. Needed to chain the parameters.
        predictor: (torch.nn.Module): A reference to the already created predictor. Needed to chain the parameters.
    Returns:
        torch.nn.Optimizer: Optimizer used in the training.
    """
    if optimizer_type.upper() == ADAM_OPT:
        return torch.optim.Adam(
            itertools.chain(model.parameters(), predictor.parameters()),
            lr=learning_rate,
        )
    elif optimizer_type.upper() == SGD_OPT:
        return torch.optim.SGD(
            itertools.chain(model.parameters(), predictor.parameters()),
            lr=learning_rate,
        )
    else:
        raise Exception(f"Optimizer {optimizer_type} not supported. ")

def create_model(
    layer_type: str,
    in_feats: int,
    hidden_features_size: List[int],
    aggregator: str,
    attn_num_heads: List[int],
    feat_drops: List[float],
    attn_drops: List[float],
    alphas: List[float],
    residuals: List[bool],
    edge_types: List[str],
) -> torch.nn.Module:
    """Creates a model given a layer type and sizes of the hidden layers.

    Args:
        layer_type (str): Layer type.
        in_feats (int): Defines the size of the input features.
        hidden_features_size (List[int]): Defines the size of each hidden layer in the architecture.
        aggregator str: Type of the aggregator that will be used in GraphSage. Ignored for GAT.
        attn_num_heads List[int] : Number of heads for each layer used in the graph attention network. Ignored for GraphSage.
        feat_drops List[float]: Dropout rate on feature for each layer.
        attn_drops List[float]: Dropout rate on attention weights for each layer. Used only in GAT.
        alphas List[float]: LeakyReLU angle of negative slope for each layer. Used only in GAT.
        residuals List[bool]: Use residual connection for each layer or not. Used only in GAT.
        edge_types (List[str]): All edge types that are occurring in the heterogeneous network.

    Returns:
        torch.nn.Module: Model used in the link prediction task.
    """
    if layer_type.lower() == GRAPH_SAGE:
        return GraphSAGE(in_feats=in_feats, hidden_features_size=hidden_features_size, aggregator=aggregator, feat_drops=feat_drops, edge_types=edge_types)
    elif layer_type.lower() == GRAPH_ATTN:
        return GAT(in_feats=in_feats, hidden_features_size=hidden_features_size, attn_num_heads=attn_num_heads, feat_drops=feat_drops, attn_drops=attn_drops,
            alphas=alphas, residuals=residuals, edge_types=edge_types)
    else:
        raise Exception(f"Layer type {layer_type} not supported. ")


def create_predictor(predictor_type: str, predictor_hidden_size: int) -> torch.nn.Module:
    """Create a predictor based on a given predictor type.

    Args:
        predictor_type (str): Name of the predictor.
        predictor_hidden_size (int): Size of the hidden layer in MLP predictor. It will only be used for the MLPPredictor.
    Returns:
        torch.nn.Module: Predictor implemented in predictors module.
    """
    if predictor_type.lower() == DOT_PREDICTOR:
        return DotPredictor()
    elif predictor_type.lower() == MLP_PREDICTOR:
        return MLPPredictor(h_feats=predictor_hidden_size)
    else:
        raise Exception(f"Predictor type {predictor_type} not supported. ")
