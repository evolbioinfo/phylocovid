from ete3 import Tree

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--in_tree', required=True, type=str)
    parser.add_argument('--out_tree', required=True, type=str)
    params = parser.parse_args()

    tree = Tree(params.in_tree)
    i = 0
    for n in tree.traverse():
        if n.is_leaf():
            continue
        if n.is_root():
            n.name = 'root'
        else:
            n.name = 'n{}'.format(i)
            i += 1

    tree.write(outfile=params.out_tree, format=3, format_root_node=True)
