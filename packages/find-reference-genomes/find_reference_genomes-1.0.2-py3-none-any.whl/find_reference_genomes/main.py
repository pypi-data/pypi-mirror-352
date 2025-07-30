import glob
import json
import os
import subprocess
import shutil
import sys
import time
from typing import Dict, List

from find_reference_genomes.genome import Genome
from find_reference_genomes.lineage import Lineage


def download_genomes(genomes_str: str, output_dir: str):
    genomes_list = genomes_str.split(",")
    for genome in genomes_list:
        run_ncbi_dataset_download(genome, output_dir)


def run_ncbi_dataset_download(accession: str, output_prefix: str, retries: int = 3) -> Dict[str, List[str]] | None:
    output_zip = f"{output_prefix}.zip"

    attempt = 0
    while attempt < retries:
        try:
            # Dehydrated download
            subprocess.run(
                [
                    "datasets",
                    "download",
                    "genome",
                    "accession",
                    accession,
                    "--assembly-level",
                    "chromosome,complete,scaffold",
                    "--dehydrated",
                    "--include",
                    "genome",
                    "--filename",
                    output_zip,
                ],
                check=True,
            )

            # Unpack and rehydrate
            shutil.unpack_archive(output_zip, output_prefix)
            subprocess.run(["datasets", "rehydrate", "--directory", output_prefix], check=True)

        except subprocess.CalledProcessError as e:
            print(e)
            if attempt > retries:
                raise RuntimeError(f"Download failed after {retries} retries") from e
            print(f"Attempt {attempt} failed, retrying in 5 seconds...")
            time.sleep(5)
            attempt += 1
            
        except FileNotFoundError as e:
            print(e)
            sys.exit(1)

        finally:   
            fna_files = glob.glob(f"{output_prefix}/ncbi_dataset/data/*/*.fna")
            for f in fna_files:
                shutil.move(f, output_prefix)
                
            shutil.rmtree(f"{output_prefix}/ncbi_dataset")
            os.remove(f"{output_prefix}/md5sum.txt")
            os.remove(f"{output_prefix}/README.md")
            os.remove(output_zip)
            
            break


def find_reference_genomes(name: str, level: str, max_rank: str = None, allow_clade: bool = False):
    taxo = Lineage(*get_lineage(name))

    rank_hierarchy = [
        "strain",
        "subspecies",
        "species",
        "genus",
        "subfamily",
        "family",
        "suborder",
        "order",
        "subclass",
        "class",
        "phylum",
        "kingdom",
        "superkingdom",
        "domain",
    ]

    max_rank_index = len(rank_hierarchy) if max_rank is None else rank_hierarchy.index(max_rank) + 1

    genomes = []
    for i, (node, rank) in enumerate(taxo):
        if rank not in rank_hierarchy or (rank == "clade" and not allow_clade):
            continue

        if rank != "clade" and rank_hierarchy.index(rank) >= max_rank_index:
            break

        new_genomes = get_genomes(node, rank, level)
        for genome in new_genomes:
            if not is_already_in_set(genomes, genome):
                genomes.append(genome)

        if rank != "clade" and rank == max_rank:
            break

    print("Organism,Taxid,Rank,Accession,Bioproject,Assembly_level,Cumul_size,scaffold_n50,Chromosome_number")
    for genome in genomes:
        print(genome)


def get_lineage(name: str) -> str:
    _, _, lineage, ranks = run_taxonkit(name).rstrip("\n").split("\t")
    if len(lineage) == 0:
        raise ValueError(f"Lineage not found for organism: '{name}'. Please check the spelling.")
    return (lineage, ranks)


def run_taxonkit(name: str) -> str:
    echo_name = subprocess.Popen(["echo", name], stdout=subprocess.PIPE)
    taxonkit_name2taxid = subprocess.Popen(
        ["taxonkit", "name2taxid"],
        stdin=echo_name.stdout,
        stdout=subprocess.PIPE,
    )
    taxonkit_lineage = subprocess.Popen(
        ["taxonkit", "lineage", "-i", "2", "-R"],
        stdin=taxonkit_name2taxid.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    echo_name.wait()
    taxonkit_name2taxid.wait()
    out, err = taxonkit_lineage.communicate()

    if taxonkit_lineage.returncode != 0:
        print(f"Taxonkit exited with return code '{taxonkit_lineage.returncode}': {err}", file=sys.stderr)
        sys.exit(taxonkit_lineage.returncode)

    echo_name.stdout.close()
    taxonkit_name2taxid.stdout.close()
    taxonkit_lineage.stdout.close()

    return out.decode("utf-8")


def get_genomes(node, rank, level):
    genomes = []

    ncbi_datasets = run_ncbi_dataset(node, level)
    if ncbi_datasets["total_count"] > 0:
        for report in ncbi_datasets["reports"]:
            try:
                name = report["assembly_info"]["biosample"]["description"]["organism"]["organism_name"]
                taxid = report["assembly_info"]["biosample"]["description"]["organism"]["tax_id"]
                accession = report["current_accession"]
                bioproject = report["assembly_info"]["bioproject_accession"]
                assembly_level = report["assembly_info"]["assembly_level"]
                sequence_length = report["assembly_stats"]["total_sequence_length"]
                scaffold_n50 = report["assembly_stats"]["scaffold_n50"]
                chromosome_number = "-1" if "total_number_of_chromosomes" not in report["assembly_stats"] else report["assembly_stats"]["total_number_of_chromosomes"]
                genomes.append(Genome(name, taxid, rank, accession, bioproject, assembly_level, sequence_length, scaffold_n50, chromosome_number))
            except:
                pass

    return genomes


def run_ncbi_dataset(node, level):
    ncbi_datasets = subprocess.Popen(
        [
            "datasets",
            "summary",
            "genome",
            "taxon",
            "--assembly-level",
            level,
            "--reference",
            node,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    out, err = ncbi_datasets.communicate()

    try:
        out_json = json.loads(out.decode("utf-8"))
        # dump_json = json.dumps(out_json, indent=2)
        # print(dump_json)
        return out_json
    except:
        return {"total_count": 0}


def is_already_in_set(genomes: list[Genome], genome: Genome):
    for g in genomes:
        if g.bioproject == genome.bioproject:
            return True
    return False
