from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from typing import Optional
from argparse import ArgumentParser, Namespace

from dark.sam import SAMFilter, PaddedSAM

from midtools.offsets import analyzeOffets, findSignificantOffsets
from midtools.read import AlignedRead


def addCommonOptions(parser: ArgumentParser) -> None:
    """
    Add standard command-line options to an argument parser.

    @param parser: An C{ArgumentParser} instance.
    """
    parser.add_argument(
        "--minReads",
        type=int,
        default=5,
        help=(
            "The minimum number of reads that must cover a location for it "
            "to be considered significant."
        ),
    )

    parser.add_argument(
        "--homogeneousCutoff",
        type=float,
        default=0.9,
        help=(
            "If the most common nucleotide at a location occurs more than "
            "this fraction of the time (i.e., amongst all reads that cover "
            "the location) then the location will be considered homogeneous "
            "and therefore uninteresting."
        ),
    )


def addCommandLineOptions(
    parser: ArgumentParser, outfileDefaultName: Optional[str] = None
):
    """
    Add standard command-line options to an argument parser.

    @param parser: An C{ArgumentParser} instance.
    @param outfileDefaultName: The C{str} output file to use as a default
        in case the user does not give one on the command line.
    """

    addCommonOptions(parser)
    SAMFilter.addFilteringOptions(parser)

    parser.add_argument(
        "--outfile",
        default=outfileDefaultName,
        help="The filename to store the resulting HTML.",
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="If specified, show the figure interactively.",
    )


def constructRead(query):
    return AlignedRead(query.id, query.sequence)


def parseCommandLineOptions(
    args: Namespace, returnSignificantOffsets: bool = True
) -> tuple[
    int,
    list[AlignedRead],
    PaddedSAM,
    list[int],
    list[Counter],
    list[set[AlignedRead]],
    Optional[list[int]],
]:
    """
    Deal with the various command-line options added to the ArgumentParser
    instance by addCommandLineOptions.

    @param args: The result of calling C{parse_args} on an C{ArgumentParser}
        instance (the one that was passed to C{addCommandLineOptions}, unless
        we're testing).
    @param returnSignificantOffsets: If C{True} also return a list of the
        significant offsets (else that element of the return value will be
        C{None}).
    @return: A C{tuple}: (genomeLength, alignedReads, padddedSAM,
        readCountAtOffset, baseCountAtOffset, readsAtOffset,
        significantOffsets).
    """
    genomeLength = -1
    alignedReads = []
    samFilter = SAMFilter.parseFilteringOptions(args)

    if samFilter.referenceIds and len(samFilter.referenceIds) > 1:
        raise ValueError("Only one reference id can be given.")

    referenceLengths = samFilter.referenceLengths()

    if len(referenceLengths) == 1:
        referenceId, genomeLength = referenceLengths.popitem()
    else:
        raise ValueError(
            "If you do not specify a reference sequence with "
            "--referenceId, the SAM/BAM file must contain exactly one "
            "reference. But %s contains %d." % (args.samfile, len(referenceLengths))
        )

    paddedSAM = PaddedSAM(samFilter)

    queries = paddedSAM.queries()

    with ProcessPoolExecutor() as executor:
        for alignedRead in executor.map(constructRead, queries):
            alignedReads.append(alignedRead)

    readCountAtOffset, baseCountAtOffset, readsAtOffset = analyzeOffets(
        genomeLength, alignedReads
    )

    if returnSignificantOffsets:
        significantOffsets = list(
            findSignificantOffsets(
                baseCountAtOffset,
                readCountAtOffset,
                args.minReads,
                args.homogeneousCutoff,
            )
        )
        for read in alignedReads:
            read.setSignificantOffsets(significantOffsets)
    else:
        significantOffsets = None

    return (
        genomeLength,
        alignedReads,
        paddedSAM,
        readCountAtOffset,
        baseCountAtOffset,
        readsAtOffset,
        significantOffsets,
    )


def addAnalysisCommandLineOptions(parser: ArgumentParser) -> None:
    """
    Add command-line options used in a read analysis.
    """

    addCommonOptions(parser)

    parser.add_argument(
        "--sampleName",
        metavar="NAME",
        required=True,
        help="The name of the sample whose reads are being analysed.",
    )

    parser.add_argument(
        "--referenceGenome",
        metavar="FILENAME",
        action="append",
        nargs="+",
        required=True,
        help=(
            "The name of a FASTA file containing reference genomes that "
            "were used to create the alignment files (may be repeated)."
        ),
    )

    parser.add_argument(
        "--alignmentFile",
        metavar="FILENAME",
        action="append",
        nargs="+",
        required=True,
        help=(
            "The name of a SAM/BAM alignment file with mappings of reads to all "
            "references (as produced using the --all option when running bowtie2). "
            "May be repeated."
        ),
    )

    parser.add_argument(
        "--referenceId",
        metavar="NAME",
        action="append",
        nargs="*",
        help=(
            "The sequence id whose alignment should be analyzed (may "
            "be repeated). All ids must be present in the --referenceGenome "
            "file. One of the SAM/BAM files given using --alignmentFile "
            "should have an alignment against the given argument. If "
            "omitted, all references that are aligned to in the given "
            "BAM/SAM files will be analyzed."
        ),
    )

    parser.add_argument("--outputDir", help="The directory to save result files to.")

    parser.add_argument(
        "--saveReducedFASTA",
        action="store_true",
        help=(
            "If given, write out a FASTA file of the original input but "
            "with just the signifcant locations."
        ),
    )

    parser.add_argument(
        "--plotSAM",
        action="store_true",
        help=(
            "If given, save plots showing where reads are aligned to on "
            "the genome along with their alignment scores."
        ),
    )

    parser.add_argument(
        "--verbose",
        type=int,
        default=0,
        help=("The integer verbosity level (0 = no output, 1 = some output, etc)."),
    )
