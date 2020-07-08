import logging
from ete3.parser.newick import write_newick
from ete3 import Tree
from pastml.tree import read_tree

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_tree', required=True, type=str)
    parser.add_argument('--output_tree', required=True, type=str)
    parser.add_argument('--threshold', required=True, type=str)
    parser.add_argument('--feature', required=True, type=str)
    parser.add_argument('--strict', action='store_true', default=False)
    params = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")

    tr = read_tree(params.input_tree)

    try:
        threshold = float(params.threshold)
    except:
        # may be it's a string threshold then
        threshold = params.threshold

    num_collapsed, num_set_zero_tip, num_set_zero_root = 0, 0, 0
    for n in list(tr.traverse('postorder')):
        children = list(n.children)
        for child in children:
            if getattr(child, params.feature) < threshold \
                    or not params.strict and getattr(child, params.feature) == threshold:
                if child.is_leaf():
                    child.dist = 0
                    num_set_zero_tip += 1
                elif n.is_root() and len(n.children) == 2:
                    child.dist = 0
                    num_set_zero_root += 1
                else:
                    n.remove_child(child)
                    for grandchild in child.children:
                        n.add_child(grandchild)
                    num_collapsed += 1

    msg = ''
    if num_collapsed:
        msg = 'Collapsed {} internal branch{}'.format(num_collapsed, 'es' if num_collapsed > 1 else '')
    if num_set_zero_tip:
        if msg:
            msg += ', set {} external branch{} to zero'.format(num_set_zero_tip, 'es' if num_set_zero_tip > 1 else '')
        else:
            msg += 'Set {} external branch{} to zero'.format(num_set_zero_tip, 'es' if num_set_zero_tip > 1 else '')
    if num_set_zero_root:
        if msg:
            msg += ', set {} root child branch{} to zero'.format(num_set_zero_root, 'es' if num_set_zero_root > 1 else '')
        else:
            msg += 'Set {} root child branch{} to zero'.format(num_set_zero_root, 'es' if num_set_zero_root > 1 else '')
    if not msg:
        msg = 'Did not find any branches to modify'
    logging.info('{} (criterion: {} <{} {}).'
                 .format(msg, params.feature, '' if params.strict else '=', threshold))
    nwk = write_newick(tr, format_root_node=True, format=1)
    with open(params.output_tree, 'w+') as f:
        f.write('%s\n' % nwk)
