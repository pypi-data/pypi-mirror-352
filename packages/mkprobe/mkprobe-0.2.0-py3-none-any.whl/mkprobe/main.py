#!/usr/bin/env python3


"""
Build contigs from contiguous kmers stored as fasta files

Contact: bio2m-team@bio2m.fr
"""


import sys
import os
import argparse

import info


def main():
    """ Function doc """
    args=usage()

    contigs = []
    ### compute
    for file in args.files:
        contigs += compute(args, file)
    ### output
    output(args, contigs)


def compute(args, file):
    """ Function doc """
    ### get base name file
    basename = os.path.basename(file.name)

    ### compute
    contigs = []
    contig_id = handle_contig_id(args, file.readline(), basename)
    contig_seq = file.readline().rstrip('\n')
    contig_id_last = None
    for raw in file:
        if raw.startswith('>'):
            contig_id_last = raw
            continue
        nb = len(raw[:-2])
        if raw[:-2] == contig_seq[-nb:]:
            contig_seq += raw[-2:-1]
        else:
            contigs.append((contig_id, contig_seq))
            contig_id = handle_contig_id(args, contig_id_last, basename)
            contig_seq = raw.rstrip('\n')
    ### last contig
    contigs.append((contig_id, contig_seq))

    return contigs


def handle_contig_id(args, contig_id, basename):
    items = contig_id.rstrip('\n').split(' ')

    ### keep only ID part of the header (if not keep-all argument) 
    if not args.keep_all:
        items = [items[0]]

    ### add file name if add-filename argument
    if args.add_filename:
        items.append(basename)

    return ' '.join(items)


def output(args, contigs):
    """
    wwithout --output option, print on stdin
    """
    if not args.output:
        print(*[f"{id}\n{seq}\n" for id, seq in contigs], sep='')
    elif args.output.name.endswith('.tsv'):
        for id, seq in contigs:
            args.output.write(f"{id.lstrip('>')}\t{seq}\n")
    else:
        for id, seq in contigs:
            args.output.write(f"{id}\n{seq}\n")


def usage():
    doc_sep = '=' * min(57, os.get_terminal_size(2)[0])
    parser = argparse.ArgumentParser(description= f'{doc_sep}{__doc__}{doc_sep}',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument("files",
                        help="fasta files",
                        type=argparse.FileType('r'),
                        nargs='*',
                       )
    parser.add_argument("-o", "--output",
                        help=("output file name, by default at fasta. If extension is 'tsv', "
                              "output will be a tabuled file"),
                        type=argparse.FileType('w'),
                       )
    parser.add_argument("-a", "--add-filename",
                        action="store_true",
                        help="add file name to the headers, useful for multiple files",
                       )
    parser.add_argument("-k", "--keep-all",
                        action="store_true",
                        help="keep all fasta headers, not just the first space-separated string",
                       )
    parser.add_argument('-v', '--version',
                        action='version',
                        version=f"{parser.prog} v{info.VERSION}",
                       )
    ### Go to "usage()" without arguments
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit()
    return parser.parse_args()


if __name__ == "__main__":
    main()
