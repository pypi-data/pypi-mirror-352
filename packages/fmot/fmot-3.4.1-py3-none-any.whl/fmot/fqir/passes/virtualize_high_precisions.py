"""This FQIR pass will convert high-precision variables (e.g. int24) into int16,
and modify any GMAC operators accordingly. Will also raise errors if an int24 variable
is passed into a non-supporting operator."""
from fmot.fqir import GraphProto, TensorProto, NodeProto, registry_v1
import logging
from typing import Union, Literal, Optional
from collections import defaultdict
from enum import Enum
from ordered_set import OrderedSet
from fmot.fqir.nodes.optypes import split_to_subprecisions
import numpy as np

logger = logging.getLogger(__name__)

# helpers:


def predecessors(graph: GraphProto, node: Union[TensorProto, NodeProto]):
    if isinstance(node, TensorProto):
        for maybe_pred in graph.nodes:
            if node in maybe_pred.outputs:
                yield maybe_pred

    elif isinstance(node, NodeProto):
        for x in node.inputs.values():
            yield x


def successors(graph: GraphProto, node: Union[TensorProto, NodeProto]):
    if isinstance(node, TensorProto):
        for maybe_succ in graph.nodes:
            if node in maybe_succ.inputs.values():
                yield maybe_succ

    elif isinstance(node, NodeProto):
        for x in node.outputs:
            yield x


def create_lo_hi_from_i24(x: TensorProto):
    """Create low/high-bit subvectors from an initial int24 vector.

    The low vector stores the bottom 12 bits (with an unused sign bit, hence i13)
    The high vector stores the top 12 bits (including sign)

    Quantas are derived from the original tensor's quanta
    """
    if x.value is not None:
        v_lo, v_hi = split_to_subprecisions(x.value, [13, 12])
    else:
        v_lo, v_hi = None, None

    hi = TensorProto(
        name=f"{x.name}_hi",
        dtype="fqint16",
        shape=x.shape,
        quanta=x.quanta + 4,  ### TODO: double check quanta values
        value=v_hi,
    )
    lo = TensorProto(
        name=f"{x.name}_lo",
        dtype="fqint16",
        shape=x.shape,
        quanta=x.quanta - 12,  ### TODO: double check quanta values
        value=v_lo,
    )
    return lo, hi


RuleType = Enum(
    "RuleType",
    [
        # A PRODUCE RuleType annotates that a PropagatorRule should be applied to a node if it produces an
        #   int24 output
        # PRODUCE rules are applied when we detect that a node has an int24 output, and
        #   are independent of input precisions.
        # Example: if a GMACv2 produces an int24, we can precision-split its output into two i16 outputs
        #   without any consideration of the input precisions.
        "PRODUCE",
        # A CONSUME_ANY RuleType annotates that a PropagatorRule should be applied to a node if any of its inputs
        #   are int24 AND we have a mapping from the original int24 input to two int16 subvectors
        # We wait to apply a CONSUME_ANY rule until the mapping from int24 to (int16, int16) has been added
        #   to the bank
        # Example: if a GMACv2 consumes an int24 operand, and we have mapped this int24 operand to x_lo, x_hi,
        #   then we can replace the int24 operand with the x_lo and x_hi precision-split versions.
        "CONSUME_ANY",
        # A CONSUME_ALL RuleType annotates that a PropagatorRule should be applied to a node if ALL of its
        #   int24 inputs have been mapped to int16 subvectors
        # We wait to apply a CONSUME_ALL rule until the mapping from int24 to (int16, int16) has been added
        #   to the bank for EVERY one of the int24 inputs. Note that it is legal in some cases for the node to
        #   have a mix of int16 and int24 inputs -- we may just do nothing to the int16 inputs.
        # Example: z = CAT([x, y]) where x and y are int24. We will wait until we have mappings x -> (x_lo, x_hi)
        #   and y -> (y_lo, y_hi). Once these mappings exist, we will replace the original CAT node with two CAT nodes:
        #        z_hi = CAT([x_hi, y_hi])
        #        z_lo = CAT([x_lo, y_lo])
        #   note that we could not have performed this re-write intil ALL of the inputs had mappings to i16x2.
        "CONSUME_ALL",
    ],
)


# Propagator Rules:


class PropagatorRule:
    """Base Class for an int24 Propagator.

    Arguments:
        opname (str): the FQIR optype name (e.g. "gmac_v2", "cat", "vvadd", ...)
        rule_type (RuleType): configures the conditions that need to be satisifed when we will call this rule.
            See above comments to see how the different RuleTypes configure this behavior
    """

    opname: str
    rule_type: RuleType

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        input_origs: Optional[dict[str, TensorProto]] = None,
    ):
        """
        Arguments:
            node (NodeProto): the node to be modified / replaced in the graph
            arith (GraphProto): the arithmetic graph to be edited
            bank (dict[Tensor, [Tensor, Tensor]]): a dictionary containing all of the active mapping from
                int24 tensors to pairs of int16 vectors (x_orig: i24 -> (x_hi: i16, x_lo: i16))
            input_origs (optional): a dictionary containing the original int24 input tensors to the node, keyed by the
                argument-names. For example, for a node that takes in "x" and "y" arguements,
                this could be {"x": <original_int24_input>, "y": <original_int24_input>}. This is only used in CONSUME rules
                (CONSUME_ANY, CONSUME_ALL)
        """
        raise NotImplementedError()


class GMACv2ProduceRule(PropagatorRule):
    """Split the int24 output into two int16 subvectors, using GMACv2's "bits_out" field."""

    opname = "gmac_v2"
    rule_type = RuleType.PRODUCE

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        assert node.opname == "gmac_v2"

        bws_out = node.constants["bits_out"]

        if len(bws_out) == 1 and sum(bws_out) == 24:
            # modify the node in-place and create new hi/lo output tensors

            node.constants["bits_out"] = [13, 12]
            out24 = node.outputs[0]
            assert out24.dtype == "fqint24"

            out_lo, out_hi = create_lo_hi_from_i24(out24)

            node.outputs = [out_lo, out_hi]

            logger.debug(f"gmac_v2 int24 output has been split {node}")

            # add to the bank
            bank[out24] = (out_lo, out_hi)


class GMACv2ConsumeRule(PropagatorRule):
    """
    Replace reference to original int24 input with the split int16 subvectors.

    Examples:
        1) Propagating split precisions into vector-vector terms:
                gmac_v2(x_vv_0=XORIG, y_vv_0=y, ..., shifts_vv=[S, ...])
            Where XORIG is int24 and has been split to (XLO, XHI) int16 subvectors.
            We break this into two terms, both multiplying the same y, and use new shift-amounts:
                gmac_v2(
                    x_vv_0=XLO, y_vv_0=y,
                    x_vv_1=XHI, y_vv_1=y,
                    ...
                    shifts_vv=[S, S+12, ...])
        2) Propagating split precisions into vector-immediate terms:
                gmac_v2(..., x_vi_0=XORIG, ..., immediates_vi=[I, ...], shamts_vi=[S, ...])
            Where XORIG is int24 and has been split to (XLO, XHI) int16 subvectors.
            We break this into two terms, both multiplying the same immediate, and use new shift-amounts:
                gmac_v2(
                    ...
                    x_vi_0=XLO,
                    x_vi_1=XHI,
                    ...,
                    immediate_vi=[I, I, ...]
                    shifts_vi=[S, S+12, ...])
    """

    opname = "gmac_v2"
    rule_type = RuleType.CONSUME_ANY

    def __init__(self):
        self.arith: GraphProto = None
        self.bank: dict[TensorProto, tuple[TensorProto, TensorProto]] = None
        self.num_vv = 0
        self.num_vi = 0
        self.node: NodeProto = None

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        """Modifies a gmac_v2 consumer of an int24 tensor based on upstream splitting"""
        assert node.opname == "gmac_v2"

        self.num_vv = 0
        self.num_vi = 0
        self.bank = bank
        self.node = node

        for key in node.inputs.keys():
            if key.startswith("x_vv_"):
                self.num_vv += 1
            elif key.startswith("x_vi_"):
                self.num_vi += 1

        for key, input_orig in inputs_orig.items():
            if key.startswith("x_vv"):
                self.prop_vv(key, input_orig)
            elif key.startswith("y_vv"):
                self.prop_vv(key, input_orig)
            elif key.startswith("x_vi"):
                self.prop_vi(key, input_orig)

    def prop_vv(self, key: str, input_orig: TensorProto):
        id = key.split("_vv_")[0]  # "x" or "y"
        other_id = {"x": "y", "y": "x"}[id]
        idx = int(key.split("_vv_")[1])  # integer index

        shamt = self.node.constants["shamts_vv"][idx]

        lo, hi = self.bank[input_orig]

        # we had a single term:
        #  (x24 * other) << shamt
        # we will transform it to:
        #  (x_lo * other) << shamt_lo + (x_hi * other) << shamt_hi
        # where x24 = x_lo + 2**12 * x_hi
        # therefore, shamt_lo = shamt, shamt_hi = shamt + 12

        # update current product to use x_lo (no change to shamt)
        self.node.inputs[key] = lo

        # create new partial product for x_hi * other >> shamt + 12
        self.node.inputs[f"{id}_vv_{self.num_vv}"] = hi
        self.node.inputs[f"{other_id}_vv_{self.num_vv}"] = self.node.inputs[
            f"{other_id}_vv_{idx}"
        ]
        self.node.constants["shamts_vv"].append(shamt + 12)

        self.num_vv += 1

        logger.debug(
            f" propagated int24 input splitting {input_orig} into gmac_v2 through key {key}"
        )

    def prop_vi(self, key: str, input_orig: TensorProto):
        idx = int(key.split("x_vi_")[1])
        imm = self.node.constants["immediates_vi"][idx]
        shamt = self.node.constants["shamts_vi"][idx]

        # we had a single term:
        #  (x24 * imm) << shamt
        # we will transform it to:
        #  (x_lo * im) << shamt_lo + (x_hi * imm) << shamt_hi
        # where x24 = x_lo + 2**12 * x_hi
        # therefore, shamt_lo = shamt, shamt_hi = shamt + 12

        if shamt + 12 <= 0:
            self.node.constants["immediates_vi"].append(imm)
            self.node.constants["shamts_vi"].append(shamt + 12)
        else:
            new_imm = imm << (shamt + 12)
            if new_imm >= -(2**23) and new_imm < 2**23:
                self.node.constants["immediates_vi"].append(new_imm)
                self.node.constants["shamts_vi"].append(0)
            else:
                raise ValueError(
                    f"Infeasible shift-amount and immediate combination: shamt: {shamt+12} imm: {imm}"
                )

        lo, hi = self.bank[input_orig]

        self.node.inputs[key] = lo
        self.node.inputs[f"x_vi_{self.num_vi}"] = hi

        self.num_vi += 1

        logger.debug(
            f" propagated int24 input splitting {input_orig} into gmac_v2 through key {key}"
        )


class CatConsumeRule(PropagatorRule):
    """Break a CAT node into two parallel CAT nodes, for the _lo and _hi subvectors.

    CONSUME_ALL --> all int24 inputs must be mapped before we can apply this rule."""

    opname = "cat"
    rule_type = RuleType.CONSUME_ALL

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        """Create two parallel concatenation nodes, each focused on the lo and hi parts of the
        vector."""

        assert node.opname == "cat"

        logger.debug(f"Arith before:\n{arith}")

        output_orig = node.outputs[0]
        new_lo, new_hi = create_lo_hi_from_i24(output_orig)

        inputs_lo = {}
        inputs_hi = {}
        for key, input_orig in inputs_orig.items():
            lo, hi = bank[input_orig]
            inputs_lo[key] = lo
            inputs_hi[key] = hi

        cat_lo = NodeProto(
            name=node.name + "_lo",
            optype=registry_v1["cat"],
            inputs=inputs_lo,
            outputs=[new_lo],
            constants=node.constants.copy(),
        )

        cat_hi = NodeProto(
            name=node.name + "_lo",
            optype=registry_v1["cat"],
            inputs=inputs_hi,
            outputs=[new_hi],
            constants=node.constants.copy(),
        )

        # insert these new cat nodes before the original cat node
        # and then remove it
        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, cat_lo)
        arith.nodes.insert(idx, cat_hi)
        arith.nodes.remove(node)

        # add new lo/hi tensors to the bank
        bank[output_orig] = (new_lo, new_hi)

        logger.debug(f"Arith after:\n{arith}")


class AssignConsumeRule(PropagatorRule):
    """Break an ASSIGN node into two parallel ASSIGN nodes, for the _lo and _hi subvectors

    CONSUME_ALL --> all int24 inputs must be mapped before we can apply this rule."""

    opname = "assign"
    rule_type = RuleType.CONSUME_ALL

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        x_orig = node.inputs["x"]
        y_orig = node.inputs["y"]

        x_lo, x_hi = bank[x_orig]
        y_lo, y_hi = bank[y_orig]

        assign_lo = NodeProto(
            name=f"{node.name}_lo",
            optype=registry_v1["assign"],
            inputs={"x": x_lo, "y": y_lo},
            outputs=[],
            constants={},
        )

        assign_hi = NodeProto(
            name=f"{node.name}_hi",
            optype=registry_v1["assign"],
            inputs={"x": x_hi, "y": y_hi},
            outputs=[],
            constants={},
        )

        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, assign_lo)
        arith.nodes.insert(idx, assign_hi)
        arith.nodes.remove(node)

        logger.debug(f"Virtualized assign {node} to i24")


class ConvertShiftToGMACv2(PropagatorRule):
    """If a SHIFT consumes int24, we will convert it to an equivalent GMACv2.
    The GMACv2 rules will be applied on the next step of propagation.
    """

    opname = "shift"
    rule_type = RuleType.CONSUME_ANY

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        assert node.opname == "shift"

        # convert shift to gmac_v2, then let the gmac_v2 rules take care of the rest
        shamt = node.constants["shamt"]
        bw = node.constants["bw"]
        rounded = node.constants["rounded"]

        if shamt <= 0:
            new_shamt = shamt
            imm = 1
        else:
            new_shamt = 0
            imm = 2**shamt
            if shamt > 24:
                raise ValueError("Extreme shamt of > 24 cannot be converted to gmac_v2")

        if rounded:
            raise NotImplementedError(
                "Rounded shift to gmac_v2 conversion not yet supported."
            )

        gmac_equiv = NodeProto(
            name=node.name + "_as_gmac_v2",
            optype=registry_v1["gmac_v2"],
            inputs={"x_vi_0": node.inputs["x"]},
            outputs=node.outputs,
            constants={
                "shamts_vv": [],
                "shamts_vi": [new_shamt],
                "immediates_vi": [imm],
                "bits_out": [bw],
            },
        )

        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, gmac_equiv)
        arith.nodes.remove(node)

        logger.debug(f"Replaced {node} with gmac_v2 equivalent {gmac_equiv}")


class ChunkConsumeRule(PropagatorRule):
    """Break an CHUNK node into two parallel CHUNK nodes, for the _lo and _hi subvectors

    Same logic is reused for SplitConsumeRule (identical signature/approach)"""

    opname = "chunk"
    rule_type = RuleType.CONSUME_ANY

    def apply(
        self,
        node: NodeProto,
        arith: GraphProto,
        bank: dict[TensorProto, tuple[TensorProto, TensorProto]],
        inputs_orig: Optional[dict[str, TensorProto]] = None,
    ):
        """Create two parallel concatenation nodes, each focused on the lo and hi parts of the
        vector."""

        assert node.opname == self.opname

        outs_hi = []
        outs_lo = []

        if "x" not in inputs_orig:
            raise ValueError(f"{inputs_orig=}")

        lo, hi = bank[inputs_orig["x"]]

        for output in node.outputs:
            new_lo, new_hi = create_lo_hi_from_i24(output)
            outs_hi.append(new_hi)
            outs_lo.append(new_lo)

            bank[output] = (new_lo, new_hi)

        chunk_lo = NodeProto(
            name=node.name + "_lo",
            optype=registry_v1[self.opname],
            inputs={"x": lo},
            outputs=outs_lo,
            constants=node.constants.copy(),
        )
        chunk_hi = NodeProto(
            name=node.name + "_hi",
            optype=registry_v1[self.opname],
            inputs={"x": hi},
            outputs=outs_hi,
            constants=node.constants.copy(),
        )

        # insert these new chunk nodes before the original cat node
        # and then remove it
        idx = arith.nodes.index(node)
        arith.nodes.insert(idx, chunk_lo)
        arith.nodes.insert(idx, chunk_hi)
        arith.nodes.remove(node)

        logger.debug(f"Replaced chunk {node} with\n{chunk_lo}\n{chunk_hi}")


class SplitConsumeRule(ChunkConsumeRule):
    """Very simple subclass of ChunkConsumeRule, just need to change opname to 'split'"""

    opname = "split"


class LegalizationRule:
    """Base class for a node legalization rule. This will not change add nodes to the graph, only
    change the internal constants within a node. May also add new input connections to the node (but these
    will be repeated connections to inputs that already exist.)

    An example is for GMACv2, if an immediate is int24, this should be broken into two int16 immediates.
    """

    opname: str

    @staticmethod
    def apply(node: NodeProto):
        raise NotImplementedError()


class GMACv2Legalizer(LegalizationRule):
    """Fixes any"""

    opname = "gmac_v2"

    @staticmethod
    def apply(node: NodeProto):
        imms = node.constants["immediates_vi"]
        shamts = node.constants["shamts_vi"]

        vmin, vmax = -(2**15), 2**15 - 1

        for i, (imm, shamt) in enumerate(zip(imms, shamts)):
            # check if the immediate is int16 or not
            if imm < vmin or imm > vmax:
                b_lo = min(1 - shamt, 13)
                b_lo = max(b_lo, 9)
                b_hi = 25 - b_lo

                assert b_hi <= 16, f"{b_hi=}, needs to be <= 16"

                imm_lo, imm_hi = split_to_subprecisions(np.array([imm]), [b_lo, b_hi])
                imm_lo = imm_lo[0].item()
                imm_hi = imm_hi[0].item()

                shamt_lo = shamt
                shamt_hi = shamt + b_lo - 1

                # if shamt_hi > 0:
                #     raise RuntimeError(
                #         f"Want to use a positive shamt on gmac_v2 after fragmenting an immediate with shamt_hi {shamt_hi} > 0,"
                #         f"illegal.\n{node}\n{node.constants=}"
                #     )

                x = node.inputs[f"x_vi_{i}"]

                if imm_lo != 0:
                    node.constants["shamts_vi"][i] = shamt_lo
                    node.constants["immediates_vi"][i] = imm_lo

                    # add an additional connection to multiply with "imm_hi"
                    n_vi = len(node.constants["shamts_vi"])
                    node.inputs[f"x_vi_{n_vi}"] = x
                    node.constants["shamts_vi"].append(shamt_hi)
                    node.constants["immediates_vi"].append(imm_hi)

                    logger.debug(
                        f"splitting gmac_v2 vi partial:\n original:\t{x} * {imm} >> {-shamt} "
                        f"\n new:\t{x} * {imm_lo} >> {-shamt_lo} + {x} * {imm_hi} >> {-shamt_hi}"
                    )

                else:
                    node.constants["shamts_vi"][i] = shamt_hi
                    node.constants["immediates_vi"][i] = imm_hi

                    logger.debug(
                        f"converting gmac_v2 vi partial:\n original:\t{x} * {imm} >> {-shamt} "
                        f"\n new:\t{x} * {imm_hi} >> {-shamt_hi}"
                    )


class VirtualI24Propagator:
    """Converts int24 tensors into two int16 tensors, based on an i13/i12 split.

    Iteratively converts int24 tensors to int13/int12 and propagates these changes
    through the rest of the graph.

    The algorithm to propagate precision-splitting maintains a *bank*, a dictionary mapping from the
    original int24 variable to the (lo, hi) precision-split variables. At each iteration of the algo we:
        1. Split any gmac_v2 int24 outputs and add these to the bank
        2. Visit all children of tensors in the bank. For each of these:
            - Raise an exception if there is no known method of propagating int24 precision
            given the node's optype
            - If the node is satisfied by the bank's contents, call the appropriate propagation
                function on this node, which may add new split vectors to the bank.
                A node is satisfied if we have enough of its inputs in the bank that we can propagate
                int24 precision-splitting through it. Concatenation is an important example, where we
                will want to wait until all of the cat node's inputs have been split before attempting to
                split the cat.
        3. Clear out any tensors from the bank which no longer are being consumed in the graph

    We repeat this process until the bank is empty (or we hit an error). To avoid infinite-spinning,
    if the bank has not changed between two iterations, we will also throw an error.
    """

    def __init__(self, arith: GraphProto, init: Optional[GraphProto] = None):
        self.arith = arith
        self.init = init
        self.bank: dict[TensorProto, tuple[TensorProto, TensorProto]] = {}

        # maintain this list as we define new rules
        self.rules: list[type[PropagatorRule]] = [
            GMACv2ConsumeRule,
            GMACv2ProduceRule,
            CatConsumeRule,
            ChunkConsumeRule,
            SplitConsumeRule,
            ConvertShiftToGMACv2,
            AssignConsumeRule,
        ]

        self.legalizers: list[type[LegalizationRule]] = [GMACv2Legalizer]

        # automatically create a mapping of opnames to rules
        self.opname_to_rules = defaultdict(list[type[PropagatorRule]])
        for rule in self.rules:
            self.opname_to_rules[rule.opname].append(rule)

        # raise an error if there is more than one rule of a given type for a given operator
        for opname, rules in self.opname_to_rules.items():
            ruletypes = set()
            for rule in rules:
                if rule.rule_type in ruletypes:
                    raise ValueError(
                        f"More than one rule of type {rule.rule_type} has been defined for {opname}"
                    )
                ruletypes.add(rule.rule_type)

        # automatically create a mapping of opnames to legalizers
        self.opname_to_legalizers = defaultdict(list[type[LegalizationRule]])
        for legalizer in self.legalizers:
            self.opname_to_legalizers[legalizer.opname].append(legalizer)

    def get_rule_of_type_for_opname(self, opname: str, rule_type: RuleType):
        for rule in self.opname_to_rules[opname]:
            if rule.rule_type == rule_type:
                return rule
        return None

    def step(self):
        any_change = False
        for node in self.arith.nodes:
            # PRODUCE
            if any(x.dtype == "fqint24" for x in node.outputs):
                maybe_rule = self.get_rule_of_type_for_opname(
                    node.opname, RuleType.PRODUCE
                )
                if maybe_rule is not None:
                    maybe_rule().apply(node, self.arith, self.bank)
                    any_change = True

            # CONSUME
            if len(node.inputs) != 0:
                banked_inputs = {}
                missing_keys = set()
                num_banked_24_inputs = 0
                for key, value in node.inputs.items():
                    if value.dtype == "fqint24":
                        if value in self.bank:
                            banked_inputs[key] = value
                            num_banked_24_inputs += 1
                        else:
                            missing_keys.add(key)

                consume_all_rule = self.get_rule_of_type_for_opname(
                    node.opname, RuleType.CONSUME_ALL
                )
                consume_any_rule = self.get_rule_of_type_for_opname(
                    node.opname, RuleType.CONSUME_ANY
                )

                if num_banked_24_inputs > 0:
                    if (consume_all_rule is None) and (consume_any_rule is None):
                        raise RuntimeError(
                            f"No propagation rule for node {node} to consume an int24 variable."
                        )
                    if len(missing_keys) == 0 and consume_all_rule is not None:
                        consume_all_rule().apply(
                            node, self.arith, self.bank, banked_inputs
                        )
                        any_change = True
                    elif consume_any_rule is not None:
                        consume_any_rule().apply(
                            node, self.arith, self.bank, banked_inputs
                        )
                        any_change = True
                    elif consume_all_rule is None:
                        raise RuntimeError(
                            f"No propagation rule for node {node} to consume an int24 variable."
                        )

        # cleanup
        to_remove = set()
        for tensor in self.bank.keys():
            if len(list(successors(self.arith, tensor))) == 0:
                to_remove.add(tensor)
        for x in to_remove:
            self.bank.pop(x)

        return any_change

    def fragment_i24_params(self):
        i24_params = OrderedSet()
        for p in self.arith.parameters:
            if p.dtype == "fqint24":
                assert (
                    len(p.shape) == 1
                ), f"Found illegal multidimensional int24 parameter {p}"
                i24_params.add(p)

        for p_orig in i24_params:
            p_lo, p_hi = create_lo_hi_from_i24(p_orig)
            self.arith.add_parameter(p_lo)
            self.arith.add_parameter(p_hi)
            logger.debug(f"Replacing int24 parameter {p_orig} with {p_lo} and {p_hi}")
            self.arith.parameters.remove(p_orig)

            self.bank[p_orig] = (p_lo, p_hi)

    def fragment_i24_zeros_init(self):
        if self.init is None:
            return
        for node in self.init.nodes.copy():
            if node.opname == "zeros" and node.outputs[0].dtype == "fqint24":
                y_orig = node.outputs[0]
                y_lo, y_hi = create_lo_hi_from_i24(y_orig)
                self.bank[y_orig] = (y_lo, y_hi)

                node_lo = NodeProto(
                    name=f"{node.name}_lo",
                    optype=registry_v1["zeros"],
                    inputs={},
                    outputs=[y_lo],
                    constants=node.constants.copy(),
                )
                node_hi = NodeProto(
                    name=f"{node.name}_hi",
                    optype=registry_v1["zeros"],
                    inputs={},
                    outputs=[y_hi],
                    constants=node.constants.copy(),
                )
                self.init.add_node(node_lo)
                self.init.add_node(node_hi)
                self.init.nodes.remove(node)

                logger.debug(f"replacing {node} with {node_lo}, {node_hi} in INIT")

    def legalize(self):
        for node in self.arith.nodes:
            for legalizer in self.opname_to_legalizers[node.opname]:
                legalizer.apply(node)

    def do(self):
        # before: fragment any int24 parameters and zeros-init
        self.fragment_i24_params()
        self.fragment_i24_zeros_init()

        logger.debug("Step 0")
        any_change = self.step()

        i = 1
        while len(self.bank) != 0 and any_change:
            logger.debug(f"Step {i}, bank: {self.bank}, graph: {self.arith}")
            any_change = self.step()
            logger.debug(f"{any_change=} at step {i}")
            i += 1
            if i == 10:
                assert False, f"{self.arith=}\n{self.init=}"

        if len(self.bank) != 0:
            raise RuntimeError("Virtual int24 propagation failed.")

        # after: run legalizers
        self.legalize()


def virtualize_high_precisions(graph: GraphProto):
    arith = graph.subgraphs["ARITH"]
    init = graph.subgraphs.get("INIT", None)

    propagator = VirtualI24Propagator(arith, init=init)
    propagator.do()
