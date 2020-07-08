from ete3 import Tree
from pastml.tree import read_tree

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--in_tree', required=True, type=str)
    parser.add_argument('--out_tree', required=True, type=str)
    parser.add_argument('--outgroup', required=False, type=str, default=None)
    parser.add_argument('--duplicates', required=True, type=str)
    params = parser.parse_args()

    tree = Tree(params.in_tree)
    tree.unroot()

    with open(params.outgroup, 'r') as f:
        core_ids = set(f.read().strip().strip('\n').split('\n'))
    og_pos = 0

    # Get duplicate sequences of the outgroup
    with open(params.duplicates, 'r') as f:
        for line in f:
            line = line.strip('\n').strip()
            if line:
                seq_ids = set(line.split(','))
                if seq_ids & core_ids:
                    core_ids |= seq_ids

    # Make sure that our unrooted tree is "rooted" on a tip that has nothing to do with the core tree
    parents = set(_.up for _ in tree)
    parent = next(_ for _ in parents if not {t.name for t in _} & core_ids)
    tree.set_outgroup(next(t for t in parent))
    tree.unroot()

    og = {_ for _ in tree if _.name in core_ids}
    min_dist = min(_.dist for _ in og)
    mrca = tree.get_common_ancestor(*og) if len(og) > 1 else next(iter(og))
    zero_children = []
    need_extra_branch = False
    for c in mrca.children:
        if not (set(c.iter_leaves()) & og) and c.dist > min_dist:
            need_extra_branch = True
        else:
            zero_children.append(c)
    if need_extra_branch:
        for c in zero_children:
            mrca.remove_child(c)
        mrca = mrca.add_child(dist=0, support=0)
        for c in zero_children:
            mrca.add_child(c)

    print("Rooted a tree, setting the MRCA of {} as an outgroup.".format(', '.join(_.name for _ in mrca.iter_leaves())))

    tree.set_outgroup(mrca)
    total_branch = sum(_.dist for _ in tree.children)
    for child in tree.children:
        child.dist = og_pos * total_branch if child == og else (1 - og_pos) * total_branch

    tree.write(outfile=params.out_tree, format=2)
