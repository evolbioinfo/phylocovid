import logging
from collections import defaultdict

from Bio import SeqIO
from Bio.Alphabet import generic_dna
from ete3 import Tree

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--in_aln', required=True, type=str)
    parser.add_argument('--out_aln', required=True, type=str)
    parser.add_argument('--tree', required=False, default=None, type=str)
    parser.add_argument('--ids', required=False, default=None, type=str)
    parser.add_argument('--in_duplicates', required=True, type=str)
    parser.add_argument('--out_duplicates', required=True, type=str)
    params = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S",
                        filename=None)

    if params.tree:
        tree = Tree(params.tree)
        interesting_ids = {_.name for _ in tree}
    elif params.ids:
        with open(params.ids, 'r') as f:
            interesting_ids = set(f.read().strip().strip('\n').split('\n'))
    else:
        raise ValueError('Either ids or tree must be specified')

    id2seq = {rec.id: rec.seq for rec in SeqIO.parse(params.in_aln, 'fasta', alphabet=generic_dna)}
    aln_ids = set(id2seq.keys())

    # Process duplicate sequences: add duplicates at zero branches in the tree
    id2id = {}
    with open(params.in_duplicates, 'r') as f:
        for line in f:
            line = line.strip('\n').strip()
            if line:
                seq_ids = set(line.split(','))
                ref = next(iter(seq_ids & aln_ids), None)
                if not ref:
                    continue
                for _ in seq_ids & interesting_ids:
                    id2id[_] = ref

    duplicates = defaultdict(list)
    for id, ref in id2id.items():
        duplicates[ref].append(id)

    with open(params.out_duplicates, 'w+') as f:
        for ids in duplicates.values():
            f.write(','.join(ids) + '\n')
            interesting_ids -= set(ids[1:])

    with open(params.out_aln, 'w+') as f:
        for _ in interesting_ids:
            f.write('>{}\n{}\n'.format(_, id2seq[id2id[_] if _ in id2id else _]))
