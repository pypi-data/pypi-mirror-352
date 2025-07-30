from .batchdim_removal import remove_batchdim
from .dimtag_removal import remove_named_dims
from .kernelize_lstm import kernelize_lstm
from .kernelize_temporal_unfold import kernelize_temporal_unfold, add_conv2d_buffer
from .cleanup import (
    uniquify_names,
    limit_biases,
    remove_unused_params,
    remove_null_shifts,
    correct_subgraph_outputs,
)
from .kernelize_red_broad import kernelize_sum, kernelize_broadcast
from .kernelize_lut import kernelize_pwlin
from .fold_reused_params import fold_reused_params
from .stride_optimization import perform_stride_optimization
from .repeat_assign import dereference_repeated_assigns
from .statically_transpose import static_transposes
from ..graph_proto import GraphProto
from .virtualize_high_precisions import virtualize_high_precisions
from .conv1d_weight_pass import conv1d_weights_pass
from .output_naming import rename_outputs
import logging

logger = logging.getLogger("FQIR PASSES")


PASS_ORDER = [
    # remove_batchdim,
    kernelize_pwlin,
    # correct_subgraph_outputs,
    kernelize_lstm,
    remove_null_shifts,
    virtualize_high_precisions,
    perform_stride_optimization,
    dereference_repeated_assigns,
    kernelize_temporal_unfold,
    conv1d_weights_pass,
    add_conv2d_buffer,
    kernelize_sum,
    kernelize_broadcast,
    uniquify_names,
    limit_biases,
    static_transposes,
    remove_unused_params,
    fold_reused_params,
    rename_outputs,
    uniquify_names,
]


def run_passes(graph):
    objs = {"graph": graph, "io_spec": None}
    logger.debug("Running FQIR optimization passes")
    for p in PASS_ORDER:
        logger.debug(f"{p}:")
        ret = p(objs["graph"])
        if isinstance(ret, GraphProto):
            objs["graph"] = ret
        elif isinstance(ret, dict):
            objs.update(ret)
        logger.debug(objs["graph"])

    graph = objs["graph"]
    return graph, objs
