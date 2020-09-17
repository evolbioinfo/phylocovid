from pastml.tree import DATE_CI, DATE, read_forest


def get_node_name(n, ids):
    return tuple(sorted([_.name for _ in n if _.name in ids])) if not n.is_leaf() else n.name


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--from_tree', required=True, type=str)
    parser.add_argument('--to_tree', required=True, type=str)
    parser.add_argument('--out_tree', required=True, type=str)
    parser.add_argument('--column', required=True, type=str)
    params = parser.parse_args()

    from_tree = read_forest(params.from_tree)[0]
    to_tree = read_forest(params.to_tree)[0]
    common_tips = set.intersection(*[{_.name for _ in t} for t in (from_tree, to_tree)])

    name2n = {get_node_name(n, common_tips): n for n in from_tree.traverse()}
    n_copied = 0
    for n in to_tree.traverse():
        name = get_node_name(n, common_tips)
        if name in name2n:
            n.add_feature(params.column, getattr(name2n[name], params.column))
            n_copied += 1
    print('Copied states for {} nodes.'.format(n_copied))
    features = [DATE, DATE_CI, params.column]
    to_tree.write(outfile=params.out_tree, format_root_node=True, format=3, features=features)
