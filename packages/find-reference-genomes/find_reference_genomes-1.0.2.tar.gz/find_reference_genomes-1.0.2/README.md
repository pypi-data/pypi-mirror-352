# find_reference_genomes

Easily find and download reference genomes stored at NCBI

```
find_reference_genomes -h
usage: find_reference_genomes [-h] [-n NAME] [-d DOWNLOAD] [-o OUTPUT_DIR] [-l {chromosome,complete,scaffold,contig}]
                              [--max-rank {strain,subspecies,species,genus,subfamily,family,suborder,order,subclass,class,phylum,kingdom,superkingdom}] [--allow-clade]

Find and download reference genomes from the NCBI

options:
  -h, --help            show this help message and exit
  -n NAME, --name NAME  Scientific name of the species of interest
  -d DOWNLOAD, --download DOWNLOAD
                        Comma-separated list of PRJNAs to download (example: '-d PRJNA0001,PRJNA0002')
  -o OUTPUT_DIR, --output OUTPUT_DIR
                        If using --download, path to the output directory to store the downloaded genomes
  -l {chromosome,complete,scaffold,contig}, --level {chromosome,complete,scaffold,contig}
                        Limits the results to at least this level of assembly
  --max-rank {strain,subspecies,species,genus,subfamily,family,suborder,order,subclass,class,phylum,kingdom,superkingdom}
                        Limits the search to taxonomic ranks up to the specified level (e.g., '--max-rank genus' will only search up to genus level)
  --allow-clade         Allow the search to include clade level (default: False)
```
