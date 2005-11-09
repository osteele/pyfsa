classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
Intended Audience :: Science/Research
License :: OSI Approved :: Artistic License
Programming Language :: Python
Topic :: Scientific/Engineering :: Artificial Intelligence
Topic :: Scientific/Engineering :: Human Machine Interfaces
Topic :: Software Development :: Libraries :: Python Modules
Operating System :: OS Independent
"""

from distutils.core import setup
setup(name="FSA",
      version="1.0",
      description="Finite State Automaton library",
      long_description=
      """This package contains functions for manipulating Finite-State Automata (FSAs).  It includes functions for minimizing and determinizing FSAs, computing FSA intersections and unions, compiling a (non-POSIX) regular expression into an FSA, and compiling a set of regular expression productions into a chart parser.""",
      author="Oliver Steele",
      author_email="steele@osteele.com",
      url="http://osteele.com/software/pyfsa/",
      py_modules=["FSA", "NumFSAUtils", "FSChartParser", "reCompiler"],
      data_files=["README.txt", "LICENSE.txt"],
      classifiers=filter(None, classifiers.split('\n')),
      )
