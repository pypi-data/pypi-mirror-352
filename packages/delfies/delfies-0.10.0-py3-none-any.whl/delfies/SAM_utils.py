from dataclasses import dataclass
from functools import reduce
from typing import Optional

from pysam import CSOFT_CLIP, AlignedSegment

from delfies import Orientation


@dataclass
class SoftclippedRead:
    """
    `sc`: position of softclip start, located at read extremity
    """

    sequence: str
    name: str
    sc_ref: int
    sc_query: int
    sc_length: int


_ordered_flags = [
    "PAIRED",
    "PROPER_PAIR",
    "UNMAP",
    "MUNMAP",
    "REVERSE",
    "MREVERSE",
    "READ1",
    "READ2",
    "SECONDARY",
    "QCFAIL",
    "DUP",
    "SUPPLEMENTARY",
]
FLAGS = {key: 2**x for x, key in enumerate(_ordered_flags)}
DEFAULT_READ_FILTER_NAMES = ["UNMAP", "SECONDARY", "DUP", "SUPPLEMENTARY"]
DEFAULT_READ_FILTER_FLAG = reduce(
    lambda x1, x2: x1 | x2, map(lambda el: FLAGS[el], DEFAULT_READ_FILTER_NAMES)
)
DEFAULT_MIN_MAPQ = 20


def read_flag_matches(read: AlignedSegment, filtering_SAM_flag: int) -> bool:
    return (read.flag & filtering_SAM_flag) != 0


def find_softclip_at_extremity(
    read: AlignedSegment, orientation: Orientation
) -> Optional[SoftclippedRead]:
    """
    In pysam (version 0.20.0), attributes `(reference|query_alignment)_start` and
    `(reference|query_alignment)_end` refer to positions of consumed alignment positions,
    i.e. excluding alignment softclips. `_start` refer to 0-based inclusive
    alignment-consuming positions on reference and query, and `_end` to 0-based
    exclusive alignment positions (i.e., 1 past the last alignment-consuming position).

    In the returned object, we return the position of the first softclipped position in
    both reference and read (query). If in forward orientation in the read,
    no adjustment is needed, and if in reverse orientation, we subtract one.
    """
    result = SoftclippedRead(read.query_sequence, read.query_name, None, None, None)
    if orientation is Orientation.forward:
        if read.cigartuples[-1][0] == CSOFT_CLIP:
            result.sc_ref = read.reference_end
            result.sc_query = read.query_alignment_end
            result.sc_length = len(result.sequence) - result.sc_query
    else:
        if read.cigartuples[0][0] == CSOFT_CLIP:
            result.sc_ref = read.reference_start - 1
            result.sc_query = read.query_alignment_start - 1
            result.sc_length = result.sc_query + 1
    if result.sc_ref is None:
        return None
    else:
        return result
