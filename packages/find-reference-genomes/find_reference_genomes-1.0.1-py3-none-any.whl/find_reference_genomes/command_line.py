import argparse
import os
import sys

import find_reference_genomes


def main():
    parser = argparse.ArgumentParser(
        description="Find and download reference genomes from the NCBI")
    parser.add_argument(
        "-n", "--name",
        dest="name",
        type=str,
        required=False,
        default=None,
        help="Scientific name of the species of interest")
    parser.add_argument(
        "-d", "--download",
        dest="download",
        type=str,
        required=False,
        default=None,
        help="Comma-separated list of PRJNAs to download (example: '-d PRJNA0001,PRJNA0002')")
    parser.add_argument(
        "-o", "--output",
        dest="output_dir",
        type=str,
        required=False,
        default=os.getcwd(),
        help="If using --download, path to the output directory to store the downloaded genomes")
    parser.add_argument(
        "-l", "--level",
        dest="level",
        type=str,
        required=False,
        default="scaffold",
        choices=["chromosome", "complete", "scaffold", "contig"],
        help="Limits the results to at least this level of assembly")
    parser.add_argument(
        "--max-rank",
        dest="max_rank",
        type=str,
        required=False,
        default="family",
        choices=["strain", "subspecies", "species", "genus", "subfamily", "family", "suborder", "order", "subclass", "class", "phylum", "kingdom", "superkingdom"],
        help="Limits the search to taxonomic ranks up to the specified level (e.g., '--max-rank genus' will only search up to genus level)")
    parser.add_argument(
        "--allow-clade",
        dest="allow_clade",
        action="store_true",
        help="Allow the search to include clade level (default: False)",
        default=False
    )
    
    args = parser.parse_args()

    if args.name is None and args.download is None:
        print("Either --name or --download have to be used!", file=sys.stderr)
        sys.exit(1)

    if args.level == "contig":
        args.level = "chromosome,complete,scaffold,contig"
    elif args.level == "scaffold":
        args.level = "chromosome,complete,scaffold"
    elif args.level == "complete":
        args.level = "chromosome,complete"

    if args.name:
        find_reference_genomes.find_reference_genomes(args.name, args.level, args.max_rank, args.allow_clade)
    elif args.download:
        find_reference_genomes.download_genomes(args.download, args.output_dir)
