"""Protobuf conversion for OMLE.

Requires the ``protobuf`` package and a generated ``omle_pb2`` module.
Generate with::

    scripts/gen_proto.sh
"""

from .convert import ir_to_bytes, ir_to_proto, proto_to_ir

__all__ = ["ir_to_proto", "ir_to_bytes", "proto_to_ir"]
