#!/bin/env python

from distutils.core import setup, Extension

_suffix_tree = Extension('_suffix_tree',['python_bindings.c',
                                         'suffix_tree.c'])

setup(name="suffix_tree",
      version="2.1",
      description="""
      A python suffix tree, for easy algorithmic prototyping.
      """,

      author="Thomas Mailund",     author_email="mailund@birc.dk",
      maintainer="Thomas Mailund", maintainer_email="mailund@birc.dk",
      contact="Thomas Mailund",    contact_email="mailund@birc.dk",
      url='http://www.daimi.au.dk/~mailund/suffix_tree.html',

      scripts=[],
      py_modules=["suffix_tree"],
      ext_modules=[_suffix_tree],
      )
