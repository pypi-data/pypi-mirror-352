from fmot import fqir


def conv1d_weights_pass(graph: fqir.GraphProto):
    """
    adds a singleton dimension to conv1d weights
    """

    arith = graph.subgraphs["ARITH"]

    weights3d = set()

    for node in arith.nodes:
        if node.opname == "temporal_conv2d":
            weight = node.inputs["weight"]
            if len(weight.shape) == 3:
                weights3d.add(weight)

    # check that weights3d entries only used inside of conv2d nodes
    for node in arith.nodes:
        for x in node.inputs:
            if x in weights3d:
                assert node.opname == "temporal_conv2d"

    # reshape the weights in weights3d
    for weight in weights3d:
        cout, cin, k = weight.shape
        weight.shape = [cout, cin, 1, k]
        weight.value = weight.value.reshape(cout, cin, 1, k)

    return graph
