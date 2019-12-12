#!/usr/bin/env python

import os
import sys
import argparse
import csv
import pickle
from decimal import *
import json
from datetime import datetime
from scipy.stats import hypergeom


class Formatter(argparse.ArgumentDefaultsHelpFormatter,
                argparse.RawDescriptionHelpFormatter):
    pass


def _parse_arguments(desc, args):
    """
    Parses command line arguments
    :param desc:
    :param args:
    :return:
    """
    parser = argparse.ArgumentParser(description=desc,
                                     formatter_class=Formatter)
    parser.add_argument('input',
                        help='comma delimited list of genes in file')
    parser.add_argument('--savedb',
                        help='If set, this tool assumes input'
                             'is the gmt file and proceeds to load'
                             'it and save the processed database as'
                             'a pickle file that can be used'
                             'via --db flag ')
    parser.add_argument('--db', default='/tmp/cdsimplegenestoterm.pickle',
                        help='pickle db file, created by '
                             'previous call with --savedb flag')
    parser.add_argument('--maxpval', type=float, default=0.00001,
                        help='Max p value')
    return parser.parse_args(args)


def read_inputfile(inputfile):
    """

    :param inputfile:
    :return:
    """
    with open(inputfile, 'r') as f:
        return f.read()


def create_db(dbfile):
    """
    Creates two dictionary objects containing mapping
    of terms to genes that is returned in a tuple.

    The FIRST element of the tuple is a dict
    where keys are integers and the value is a 3 element
    tuple of dbfile with content set as
    (SOURCE/col 0 val, TERM NAME/ col 1 val,
    # GENES/count of remaining columns in row)

    The SECOND element of the tuple is also a dict
    where keys are GENES obtained in column 2+ of input file
    and value is a list of SOURCE ids corresponding
    to the FIRST element keys denoting what terms those
    genes link to

    :param dbfile:
    :return: two element tuple
    :rtype tuple

    """
    genedb = {}
    termdb = {}
    counter = 0
    with open(dbfile, 'r') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            termdb[counter] = (row[0], row[1], len(row[2:]))
            for g in row[2:]:
                if g not in genedb:
                    genedb[g] = []
                genedb[g].append(counter)
            counter = counter + 1
    return genedb, termdb


def save_db_as_pickle(dbfile, outfile):
    """

    :param dbfile:
    :param outfile:
    :return:
    """
    genedb, termdb = create_db(dbfile)
    db = {}
    db['genedb'] = genedb
    db['termdb'] = termdb
    with open(outfile, 'wb') as f:
        pickle.dump(db, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_db(dbfile):
    """

    :param dbfile:
    :return:
    """
    with open(dbfile, 'rb') as f:
        db = pickle.load(f)
        return db['genedb'], db['termdb']


def remap_terms_to_genes(genedb, genelist):
    term_map = {}
    for gene in genelist:
        if gene not in genedb:
            continue
        for termid in genedb[gene]:
            if termid not in term_map:
                term_map[termid] = set()
            term_map[termid].add(gene)
    return term_map


def run_simple(inputfile, theargs):
    """
    todo

    :param inputfile:
    :param theargs:
    :param gprofwrapper:
    :return:
    """
    if theargs.savedb is not None:
        sys.stderr.write('Creating database and saving to: ' +
                         str(theargs.savedb) + '\n')
        save_db_as_pickle(inputfile, theargs.savedb)
        return None

    raw = read_inputfile(inputfile)
    rlist = raw.strip(',').strip('\n').split(',')
    if rlist is None or (len(rlist) == 1 and len(rlist[0].strip()) == 0):
        sys.stderr.write('No genes found in input')
        return None
    glist = set()
    for entry in rlist:
        glist.add(entry.upper())

    start_time = datetime.now()
    genedb, termdb = load_db(theargs.db)
    sys.stderr.write('Db load took: ' + str(datetime.now() - start_time) + '\n')

    querysize = len(glist)
    start_time = datetime.now()
    term_map = remap_terms_to_genes(genedb, list(glist))
    sys.stderr.write('remap terms to genes took: ' + str(datetime.now() - start_time) + '\n')

    genes_in_universe = len(genedb.keys())
    besthit = None

    start_time = datetime.now()
    for key in list(term_map.keys()):
        thegenes = term_map[key]
        numgenes = len(thegenes)
        val = Decimal(hypergeom.cdf(numgenes,
                                    genes_in_universe,
                                    termdb[key][2],
                                    querysize))
        if val > theargs.maxpval:
            continue
        if besthit is None or val <= besthit[3]:
            besthit = (termdb[key][0], termdb[key][1], thegenes, val)

    sys.stderr.write('Search for best hit took: ' + str(datetime.now() - start_time) + '\n')

    if besthit is None:
        return None
    return {'name': besthit[1],
            'source': besthit[0],
            'p_value': float(besthit[3]),
            'description': '',
            'intersections': list(besthit[2])}


def main(args):
    """
    Main entry point for program

    :param args: command line arguments usually :py:const:`sys.argv`
    :return: 0 for success otherwise failure
    :rtype: int
    """
    desc = """
        Running gene enrichment using gmt term file

        Takes file with comma delimited list of genes as input and
        outputs matching term if any
    """

    theargs = _parse_arguments(desc, args[1:])

    try:
        inputfile = os.path.abspath(theargs.input)
        theres = run_simple(inputfile, theargs)
        if theargs.savedb is not None:
            return 0
        if theres is None:
            sys.stderr.write('No terms found\n')
        else:
            json.dump(theres, sys.stdout)
        sys.stdout.flush()
        return 0
    except Exception as e:
        sys.stderr.write('Caught exception: ' + str(e))
        return 2


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main(sys.argv))
