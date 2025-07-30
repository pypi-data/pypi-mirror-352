import ete4.ncbi_taxonomy.ncbiquery as nt
from Bio.Phylo import BaseTree
from nbitk.Taxon import Taxon
import sys
import logging
from io import StringIO
from contextlib import contextmanager


def _recurse_tree(bp_parent, ete4_parent):

    # iterate over children in ete3 node
    for ete4_child in ete4_parent.children:

        # create a Taxon object for each child
        # Taxon(name=tree.props['taxname'], taxonomic_rank=tree.props['rank'], guids={"taxon": tree.props['name']})
        bp_child = Taxon(
            name=ete4_child.props['taxname'],
            taxonomic_rank=ete4_child.props['rank'],
            guids={"taxon": ete4_child.props['name']},
        )
        bp_parent.clades.append(bp_child)
        _recurse_tree(bp_child, ete4_child)


class LoggerWriter:
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level
        self.buffer = StringIO()

    def write(self, message):
        self.buffer.write(message)
        if message.endswith("\n"):
            self.flush()

    def flush(self):
        self.logger.log(self.level, self.buffer.getvalue().strip())
        self.buffer.truncate(0)
        self.buffer.seek(0)


@contextmanager
def stdout_to_logger(logger, level=logging.INFO):
    original_stdout = sys.stdout
    try:
        sys.stdout = LoggerWriter(logger, level)
        yield
    finally:
        sys.stdout = original_stdout


class Parser:
    def __init__(self, file):
        self.file = file

    def parse(self):

        # Load nodes.dmp and names.dmp via ETE3, capture output to logger
        logger = logging.getLogger(__name__)
        with stdout_to_logger(logger):
            tree, synonyms = nt.load_ncbi_tree_from_dump(self.file)

        # Create a new base tree and root node
        root = Taxon(name=tree.props['taxname'], taxonomic_rank=tree.props['rank'], guids={"taxon": tree.props['name']})
        bt = BaseTree.Tree(root)

        # Recursively traverse the tree and create Taxon objects
        _recurse_tree(root, tree)

        # Done.
        return bt
