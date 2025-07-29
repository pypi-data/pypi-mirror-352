import math
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
import subprocess
import pandas as pd
import os
import itertools
import numpy as np
import regex as re
import click


def validate_simulator_options(simulator, params_source):
    """
    Raise click.UsageError if options not valid for the given simulator.

    Arguments:
    - simulator: str ('wgsim' or 'mason')
    - params_source: dict mapping param name to whether it was passed on CLI
    """

    def was_provided(opt):
        return params_source.get(opt, False)

    if simulator == "wgsim":
        if was_provided("mean_quality_begin") or \
            was_provided("mean_quality_end") or \
                was_provided("indel_fraction"):
            raise click.UsageError("--mean_quality_begin,"
                                   "--mean_quality_end and"
                                   "--indel_fraction are only"
                                   "valid with simulator='mason'")
    elif simulator == "mason":
        for opt in ["standard_deviation",
                    "haplotype", "mutation_rate", "indel_extend_probability"]:
            if was_provided(opt):
                raise click.UsageError(f"--{opt.replace('_', '-')} is only"
                                       "valid with simulator='wgsim'")


def extract_sequence(reference, chrom, start, end):
    """Extracts sequence from reference based on coordinates and strand."""
    reference = next(SeqIO.parse(reference, "fasta"))
    if reference.id not in chrom:
        raise ValueError(f"Chromosome {chrom} not found in reference.")
    seq = reference.seq[start:end]  # Extract sequence
    return str(seq)


def validate_primer_bed(df):
    """
    Validates a DataFrame representing a primer BED file.

    Args:
        df (pd.DataFrame): DataFrame to validate.

    Returns:
        pd.DataFrame: The original DataFrame if valid.

    Raises:
        ValueError: If the DataFrame does not conform to expected format.
    """

    # Check column count
    if df.shape[1] < 6 or df.shape[1] > 7:
        raise ValueError(
            "DataFrame must have 6 or 7"
            " columns. Please refer to example primer file."
        )

    # Check column types
    if not all(isinstance(df.iloc[i, 0], str) for i in range(len(df))):
        raise ValueError(
            "First column must contain only strings.(Chromosome name)")

    if not pd.api.types.is_numeric_dtype(df.iloc[:, 1]):
        raise ValueError("Second column must be numeric.(Primer start)")

    if not pd.api.types.is_numeric_dtype(df.iloc[:, 2]):
        raise ValueError("Third column must be numeric.(Primer end)")
    # Check that third column is greater than second column
    if not (df.iloc[:, 2] > df.iloc[:, 1]).all():
        raise ValueError(
            "Third column values must be greater than second column values."
            "Primer start coordinates cannot be greater than primer end."
        )

    # Check fourth column format
    pattern = re.compile(r"^[\w-]+_\d+_(LEFT|RIGHT)(?:_.*)?$")

    # Strip any leading/trailing spaces and ensure the values are strings
    if not all(
        isinstance(val, str) and
            pattern.match(val.strip()) for val in df.iloc[:, 3]
    ):
        raise ValueError(
            "Fourth column format is incorrect."
            " Expected 'string_number_LEFT/RIGHT'"
            " with possible extra characters"
            " at the end indicating whether the primer is alternative."
        )

    if not pd.api.types.is_numeric_dtype(df.iloc[:, 4]):
        raise ValueError("Fifth column must be numeric.(strand +/-)")

    if not all(isinstance(df.iloc[i, 5], str) for i in range(len(df))):
        raise ValueError(
            "Sixth column must contain only strings.(Primer sequence)")
    return df


def generate_random_values(N):
    # Generate N random values
    random_values = np.random.rand(N)

    # Normalize the values so that they sum to 1
    normalized_values = random_values / np.sum(random_values)

    # Convert the numpy array to a list
    return normalized_values.tolist()


def merge_fastq_files(fastq_file, output_file):
    """
    Merges a FASTQ file into an output FASTQ file using subprocess.call.

    Parameters:
    fastq_file (str): Path to the input FASTQ file.
    output_file (str): Path to the output FASTQ file.
    """
    command = f'cat "{fastq_file}" >> "{output_file}"'
    subprocess.call(command, shell=True)


def create_valid_primer_combinations(df):
    # Ensure the column exists before assignment
    if "valid_combinations" not in df.columns:
        df["valid_combinations"] = None

    valid_primers = []  # Use a list instead of concatenating DataFrames

    for i in range(len(df)):
        # Pair coordinates with their mismatch maps
        left_coords = list(zip(df.at[i, "left_primer_loc"],
                               df.at[i, "left_mismatch_map"]))
        right_coords = list(zip(df.at[i, "right_primer_loc"],
                                df.at[i, "right_mismatch_map"]))

        # Safe assignment using .at[]
        df.at[i, "valid_combinations"] = evaluate_matches(left_coords,
                                                          right_coords)
        for (
            primer_start,
            primer_end,
            left_mismatch_map,
            right_mismatch_map
        ) in df.at[i, "valid_combinations"]:
            valid_primers.append(
                {
                    "amplicon_number": df.at[i, "amplicon_number"],
                    "primer_start": primer_start,
                    "primer_end": primer_end,
                    "left_mismatch_map": left_mismatch_map,
                    "right_mismatch_map": right_mismatch_map
                }
            )

    # Check if we found any valid primers
    if not valid_primers:
        raise ValueError(
            "No primer matches found, please check your primer file.")

    # Convert collected data to DataFrame efficiently
    valid_primers_df = pd.DataFrame.from_records(valid_primers)

    # Merge with original DataFrame to include additional columns
    all_amplicons = valid_primers_df.merge(
        df[["amplicon_number", "primer_seq_x", "primer_seq_y", "strand"]],
        how="left",
        on="amplicon_number",
    )

    return all_amplicons


def preprocess_primers(primer_file, reference):
    # define column names to read primers bed file
    col_names = [
        "ref",
        "start",
        "end",
        "left_right",
        "primer_pool",
        "strand",
        "primer_seq",
    ]
    # read the primer bed file
    primer_bed = pd.read_csv(primer_file, sep="\t", names=col_names)
    primer_bed = validate_primer_bed(primer_bed)
    primer_bed["primer_seq"] = primer_bed.apply(
        lambda row: extract_sequence(
            reference, row["ref"], row["start"], row["end"]),
        axis=1,
    )
    # split the amplicon name into number and left/right
    primer_bed["amplicon_number"] = primer_bed["left_right"].str.split(
        "_").str[1]
    # merge the df with itself to have right and left primer on one row
    df = pd.merge(
        primer_bed.loc[primer_bed["left_right"].str.contains("LEFT")],
        primer_bed.loc[primer_bed["left_right"].str.contains("RIGHT")],
        on=["amplicon_number", "primer_pool"],
    )
    # select needed columns
    df = df[["amplicon_number", "primer_seq_x", "primer_seq_y"]]
    mask = df.duplicated(subset=["amplicon_number"], keep=False)
    # Apply a function to append an index for duplicated amplicon_number values
    df.loc[mask, "amplicon_number"] = (
        df.loc[mask, "amplicon_number"].astype(str)
        + "_"
        + df.loc[mask].groupby("amplicon_number").cumcount().astype(str)
    )
    return df


def count_contigs(fasta_file):
    """Counts the number of contigs in the FASTA file."""
    contig_count = 0
    with open(fasta_file, "r") as f:
        for line in f:
            if line.startswith(">"):
                contig_count += 1
    return contig_count


def run_simulation_on_fasta(
    fasta_file,
    output_dir,
    read_length,
    error_rate,
    mutation_rate,
    outer_distance,
    read_cnt,
    indel_fraction,
    indel_extend_probability,
    haplotype,
    simulator,
    mean_quality_begin,
    mean_quality_end,
    seed,
    sd
):
    """Runs simulator on a single FASTA file with the given parameters."""
    # Count the number of contigs in the FASTA file
    num_contigs = count_contigs(fasta_file)

    if num_contigs == 0:
        raise ValueError("No contigs found in the FASTA file.")

    # Calculate the number of reads per contig
    reads_per_contig = read_cnt // num_contigs  # Integer division

    # Prepare output filenames
    output_prefix = os.path.splitext(os.path.basename(fasta_file))[0]
    merged_output1 = os.path.join(output_dir, "merged_reads_1.fastq")
    merged_output2 = os.path.join(output_dir, "merged_reads_2.fastq")

    # Initialize merged output files (if not already created)
    open(merged_output1, "a").close()  # Create or append empty file
    open(merged_output2, "a").close()  # Create or append empty file

    # Loop through the contigs and run wgsim for each
    for contig_idx in range(num_contigs):
        # Temporary output files for each contig
        output1 = os.path.join(
            output_dir, f"{output_prefix}_contig{contig_idx + 1}_1.fastq"
        )
        output2 = os.path.join(
            output_dir, f"{output_prefix}_contig{contig_idx + 1}_2.fastq"
        )

        if simulator == "wgsim":
            command = [
                "wgsim",
                "-e",
                str(error_rate),
                "-r",
                str(mutation_rate),
                "-d",
                str(outer_distance),
                "-s",
                str(sd),
                "-N",
                str(reads_per_contig),
                "-R",
                str(indel_fraction),
                "-X",
                str(indel_extend_probability),
                "-1",
                str(read_length),
                "-2",
                str(read_length),
                fasta_file,
                output1,
                output2,
            ]
            if seed is not None:
                command.extend(["-S", str(seed)])
            # Add the "-h" flag if haplotype is True
            if haplotype:
                command.append("-h")
        else:
            # Adjust Mason command
            command = [
                "mason_simulator",
                "-ir",
                fasta_file,
                "-n",
                str(int(reads_per_contig)),
                "-o",
                output1,
                "-or",
                output2,
                "--illumina-read-length",
                str(read_length),
                "--illumina-prob-insert",
                str(indel_fraction),
                "--illumina-prob-deletion",
                str(indel_fraction),
                "--illumina-prob-mismatch",
                str(error_rate),
                "--illumina-prob-mismatch-begin",
                str(error_rate),
                "--illumina-prob-mismatch-end",
                str(error_rate),
                "--illumina-quality-mean-begin",
                str(mean_quality_begin),
                "--illumina-quality-mean-end",
                str(mean_quality_end),
                "--illumina-mismatch-quality-mean-begin",
                str(error_rate),
                "--illumina-mismatch-quality-mean-end",
                str(error_rate),
            ]
            if seed is not None:
                command.extend(["--seed", str(seed)])

        # Run the simulator command and capture any errors
        try:
            subprocess.run(
                command, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the command: {e}")
        # Merge the contig-specific output into the final merged output files
        command_merge = f'cat "{output1}" >> "{merged_output1}" \
            && cat "{output2}" >> "{merged_output2}"'
        subprocess.call(command_merge, shell=True)


def find_closest_primer_match(df, reference_seq, maxmismatch):
    """
    For each row in df, find all left/right primer match positions (as lists),
    allowing up to `maxmismatch` mismatches. Ensures both primers are found
    on the same strand. Returns original df columns + matches, mismatch maps,
    and strand.
    """

    def mismatch_alignment(primer, matched_seq):
        """
        Returns matched sequence with mismatches shown in parentheses.
        Example:
            Primer : AGCT
            Match  : AGTT
            Output : AG(T)T
        """
        aligned = []
        for p, m in zip(primer.upper(), matched_seq.upper()):
            aligned.append(m if p == m else f"({m})")
        return "".join(aligned)

    results = []

    for _, row in df.iterrows():
        primer_left = row["primer_seq_x"]
        primer_right = row["primer_seq_y"]

        pattern_left = f"({primer_left}){{s<={maxmismatch}}}"
        pattern_right = f"({primer_right}){{s<={maxmismatch}}}"

        # Forward strand
        left_fwd = [m.start() for m in re.finditer(pattern_left,
                                                   reference_seq,
                                                   flags=re.IGNORECASE,
                                                   overlapped=True)]
        right_fwd = [m.start() for m in re.finditer(pattern_right,
                                                    reference_seq,
                                                    flags=re.IGNORECASE,
                                                    overlapped=True)]

        left_fwd_actual = [reference_seq[pos:pos+len(primer_left)]
                           for pos in left_fwd]
        right_fwd_actual = [reference_seq[pos:pos+len(primer_right)]
                            for pos in right_fwd]

        left_fwd_mismatch_map = [mismatch_alignment(primer_left, seq)
                                 for seq in left_fwd_actual]
        right_fwd_mismatch_map = [mismatch_alignment(primer_right, seq)
                                  for seq in right_fwd_actual]

        # Reverse strand
        ref_rev = str(Seq(reference_seq).reverse_complement())
        left_rev = [m.start() for m in re.finditer(pattern_left,
                                                   ref_rev,
                                                   flags=re.IGNORECASE,
                                                   overlapped=True)]
        right_rev = [m.start() for m in re.finditer(pattern_right,
                                                    ref_rev,
                                                    flags=re.IGNORECASE,
                                                    overlapped=True)]

        left_rev_actual = [ref_rev[pos:pos+len(primer_left)]
                           for pos in left_rev]
        right_rev_actual = [ref_rev[pos:pos+len(primer_right)]
                            for pos in right_rev]

        left_rev_mismatch_map = [mismatch_alignment(primer_left, seq)
                                 for seq in left_rev_actual]
        right_rev_mismatch_map = [mismatch_alignment(primer_right, seq)
                                  for seq in right_rev_actual]

        result_row = row.to_dict()  # Preserve original row data

        if left_fwd and right_fwd:
            result_row.update({
                "left_primer_loc": left_fwd,
                "right_primer_loc": right_fwd,
                "left_seq_actual": left_fwd_actual,
                "right_seq_actual": right_fwd_actual,
                "left_mismatch_map": left_fwd_mismatch_map,
                "right_mismatch_map": right_fwd_mismatch_map,
                "strand": "forward"
            })
        elif left_rev and right_rev:
            result_row.update({
                "left_primer_loc": left_rev,
                "right_primer_loc": right_rev,
                "left_seq_actual": left_rev_actual,
                "right_seq_actual": right_rev_actual,
                "left_mismatch_map": left_rev_mismatch_map,
                "right_mismatch_map": right_rev_mismatch_map,
                "strand": "reverse"
            })
        else:
            result_row.update({
                "left_primer_loc": [],
                "right_primer_loc": [],
                "left_seq_actual": "none",
                "right_seq_actual": "none",
                "left_mismatch_map": "none",
                "right_mismatch_map": "none",
                "strand": "none"
            })

        results.append(result_row)

    return pd.DataFrame(results)


def make_amplicon(left_primer_loc, right_primer_loc, primer_seq_y, reference):
    """function to create amplicons based on the string match location"""
    if math.isnan(left_primer_loc) or math.isnan(right_primer_loc):
        # if there is either no left and right primer match
        amplicon = ""
        # length of the right primer is added to include the
        # right primer in the amplicon
    else:
        amplicon = str(
            reference[
                int(left_primer_loc - 1):
                int(right_primer_loc + len(primer_seq_y))
            ]
        )
    return amplicon


def evaluate_matches(left_primer_coordinates, right_primer_coordinates):
    """Find valid primer pairs that can produce an amplicon with mismatches."""
    if left_primer_coordinates and right_primer_coordinates:
        valid_combinations = []
        combinations = list(itertools.product(left_primer_coordinates,
                                              right_primer_coordinates))
        for left, right in combinations:
            left_pos, left_mismatch_map = left
            right_pos, right_mismatch_map = right
            amplicon_length = right_pos - left_pos

            if 0 < amplicon_length <= 2000:
                valid_combinations.append(
                    (left_pos, right_pos,
                     left_mismatch_map,
                     right_mismatch_map)
                )

        return valid_combinations
    else:
        return []


def write_fasta_group(group, amplicon_number, output_dir):
    fasta_filename = os.path.join(
        output_dir, f"amplicon_{amplicon_number}.fasta")

    filtered_records = [
        SeqRecord(Seq(seq), id=f"{amplicon_number}_{i}", description="")
        for i, seq in enumerate(group["amplicon_sequence"])
        if 1 < len(seq) < 10000
    ]

    if filtered_records:
        SeqIO.write(filtered_records, fasta_filename, "fasta")
    else:
        print(
            f"No valid sequences for amplicon {amplicon_number},"
            "no file written.please checkout the amplicon_stats.csv "
            "file for more information."
        )
