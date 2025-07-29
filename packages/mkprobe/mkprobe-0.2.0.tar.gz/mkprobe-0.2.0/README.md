# mkprobe

## Description

Build contigs from a suite of contiguous kmers as fasta format

kmers of input fasta file : 
```
ATCG                 kmer 1
 TCGC                kmer 2
  CGCT               kmer 3
   GCTA              kmer 4
      CTAT           kmer 5
       TATG          kmer 6
        ATGG         kmer 7
```
contigs of output
```
ATCGCTA              contig 1
      CTATGG         contig 2
```

## Installation

No dependency required.

```
# with pip (recommended)
pip install mkprobe

# or github
git clone https://github.com/Transipedia/mkprobe.git
```



## Examples


```
# All in a single output fasta file
mkprobe path/to/fasta/* -o result.fa

# All in a single output TSV file
mkprobe path/to/fasta/* -o result.tsv

# in separated files
for file in path/to/fasta/files/*
do
  mkprobe $file -o  output/$(basename $file}
done
```


## Usage

```
usage: main.py [-h] [-o OUTPUT] [-v] [files ...]

positional arguments:
  files                 fasta files

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        output file name, by default at fasta. If extension is 'tsv', 
                        output will be a tabuled file
  -a, --add-filename    add file name to the headers, useful for multiple files
  -k, --keep-all        keep all fasta headers, not just the first space-separated string
  -v, --version         show program's version number and exit
```
