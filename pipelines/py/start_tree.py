import logging

from Bio import SeqIO
from Bio.Alphabet import generic_dna
from ete3 import Tree
from pastml.tree import remove_certain_leaves

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--in_tree', required=True, type=str)
    parser.add_argument('--out_tree', required=True, type=str)
    parser.add_argument('--aln', required=False, default=None, type=str)
    parser.add_argument('--duplicates', required=True, type=str)
    params = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S",
                        filename=None)
    interesting_ids = {rec.id for rec in SeqIO.parse(params.aln, 'fasta', alphabet=generic_dna)}
    id2id = {}
    with open(params.duplicates, 'r') as f:
        for line in f:
            line = line.strip('\n').strip()
            if line:
                seq_ids = set(line.split(','))
                ref = next(iter(seq_ids & interesting_ids), None)
                if not ref:
                    continue
                for _ in seq_ids:
                    id2id[_] = ref

    tree = Tree(params.in_tree)
    for _ in tree:
        if _.name in id2id:
            _.name = id2id[_.name]
    remove_certain_leaves(tree, lambda _: _.name not in interesting_ids).write(outfile=params.out_tree)
