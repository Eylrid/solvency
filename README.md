This is a bare bones implementation of Greg Maxwell's proof of liability algorithm that I threw together in a couple hours.

How To
======

Check a Proof
-------------

In a python console:

    >>> from solvency import *
    >>> path = 'proofs/ffc210c30a5fdaad6d4cac7fe391eb67c5fc70b3.txt'
    >>> id = 'ffc210c30a5fdaad6d4cac7fe391eb67c5fc70b3'
    >>> value = 249120000
    >>> roothash = '8b35ab57c05e90e7ce96100e550ff218b\
    ... b7b957a62908133b2b62aae1d7fa614'.decode('hex')
    >>> rootvalue = 407212690000
    >>> verify_file(path, id, value, roothash, rootvalue)
    True

Example proof
=============

solvency_20141119.txt is Coinfloor's [Provable Solvency Report #8](http://blog.coinfloor.co.uk/post/103058886916/provable-solvency-report-8-november-2014).

The files in the proofs directory are partial proofs based on solvency_20141119.txt.

The root hash is 8b35ab57c05e90e7ce96100e550ff218bb7b957a62908133b2b62aae1d7fa614. The root value is 407212690000 satoshis.
