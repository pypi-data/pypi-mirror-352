import colorlover as cl
from collections import Counter
from typing import Optional, TextIO, Iterable, Any, Union
from pathlib import Path
from pysam import AlignedSegment

from dark.process import Executor

from midtools.offsets import OffsetBases


def baseCountsToStr(counts: OffsetBases | Counter[str]) -> str:
    """
    Convert base counts to a string.

    @param counts: A C{Counter} instance.
    @return: A C{str} representation of nucleotide counts at an offset.
    """
    if isinstance(counts, OffsetBases):
        counts = counts._counts

    return " ".join([("%s:%d" % (base, counts[base])) for base in sorted(counts)])


def nucleotidesToStr(
    nucleotides: dict[int, Union[Counter, OffsetBases]], prefix: str = ""
) -> str:
    """
    Convert offsets and base counts to a string.

    @param nucleotides: A C{dict} keyed by C{int} offset, with either
        C{collections.Counter} or C{OffsetBases} instances as values.
    @param prefix: A C{str} to put at the start of each line.
    @return: A C{str} representation of the offsets and nucleotide
        counts for each.
    """
    result = []
    for offset in sorted(nucleotides):
        if isinstance(nucleotides[offset], Counter):
            baseCounts = baseCountsToStr(nucleotides[offset])
        else:
            baseCounts = nucleotides[offset].baseCountsToStr()
        result.append("%s%d: %s" % (prefix, offset, baseCounts))
    return "\n".join(result)


def commonest(
    counts: Union[Counter, OffsetBases],
    drawBreaker: str,
    drawFp: Optional[TextIO] = None,
    drawMessage: Optional[str] = None,
) -> str:
    """
    Return the key of the Counter instance that is the most common.

    @param counts: Either a C{Counter} or an C{OffsetBases} instance.
    @param drawBreaker: The nucleotide base to use if there is a draw (and
        the C{drawBreaker} nucleotide is one of the nucleotides involved in the draw.
    @param drawFp: A file pointer to write information about draws (if any) to.
    @param drawMessage: A C{str} message to write to C{drawFp}. If the string
        contains '%(baseCounts)s' that will be replaced by a string
        representation of the base counts (in C{counts}) obtained from
        C{baseCountsToStr}. If not, the base count info will be printed after
        the message.
    @return: The C{str} nucleotide that is most common in the passed C{counts}
        if there is a draw and the most common nucleotides includes
        C{drawBreaker}, return C{drawBreaker}.
    """
    if isinstance(counts, Counter):
        orderedCounts = counts.most_common()
    else:
        # An OffsetBases instance. Ugh...
        orderedCounts = counts._counts.most_common()

    maxCount = orderedCounts[0][1]
    best = set(x[0] for x in orderedCounts if x[1] == maxCount)

    if len(best) > 1:
        # There's a draw. Return the drawbreaker nucleotide if it's among
        # the best, else just return the first one given by most_common.
        base = drawBreaker if drawBreaker in best else orderedCounts[0][0]

        if drawFp:
            # Check we also have a draw-break message.
            assert drawMessage
            bases = baseCountsToStr(counts)
            if drawMessage.find("%(baseCounts)s") > -1:
                print(drawMessage % {"baseCounts": bases}, file=drawFp)
            else:
                print("%s\n%s" % (drawMessage, bases), file=drawFp)

        return base
    else:
        return orderedCounts[0][0]


def fastaIdentityTable(
    filename: Path,
    outputFilename: Path,
    verbose: bool,
    filename2: Optional[Path] = None,
) -> None:
    """
    Call fasta-identity-table.py to produce an HTML identity table
    for one or two FASTA files.

    @param filename: A C{str} file name containing FASTA.
    @param outputFilename: A C{str} file name to store the HTML output into.
    @param verbose: The C{int} verbosity level.
    @param filename2: An optional second C{str} file name containing FASTA.
    """
    colors = cl.scales["9"]["seq"]["GnBu"]
    colorArgs = []
    for i in range(7):
        colorArgs.append('--color "%.2f %s"' % (0.65 + 0.05 * i, colors[i]))

    file2arg = ('--fastaFile2 "%s"' % filename2) if filename2 else ""

    e = Executor()
    e.execute(
        "fasta-identity-table.py --showGaps --showLengths --footer "
        "--removeDescriptions %s %s < %s > %s"
        % (" ".join(colorArgs), file2arg, filename, outputFilename)
    )
    if verbose > 1:
        for line in e.log:
            print("       ", line)


def s(count: int, suffix: str = "s") -> str:
    """
    Return a suffix unless a count is singular (i.e., one).

    @param count: The C{int} count.
    @param suffix: The C{str} suffix.
    @return: A C{str}, either '' or the passed suffix depending on whether the count is
        singular.
    """
    return "" if count == 1 else suffix


def quoted(filename: Path) -> str:
    """
    Return a single-quoted string for a filename.

    @param filename: A C{Path} instance (actually this can be anything).
    @return: A quoted C{str} of the path to the file.
    """
    return f"{str(filename)!r}"


def commas(iterable: Iterable[Any]) -> str:
    """
    Turn an iterable into a sorted comma-separated string.

    @param iterable: An iterable of things to be put into the return string.
    @return: A sorted comma-separated C{str} of the things in C{iterable}.
    """
    return ", ".join(map(str, sorted(iterable)))


def alignmentQuality(alignment: AlignedSegment) -> str:
    """
    Produce an alignment quality string from a pysam alignment.

    @param alignment: A C{pysam.AlignedSegment} instance.
    @return: A C{str} quality string.
    """
    if alignment.query_qualities is None:
        raise ValueError(f"Aligned segment {alignment} with None query qualities.")

    return "".join(map(lambda x: chr(x + 33), alignment.query_qualities))
