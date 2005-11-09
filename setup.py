from distutils.core import setup
setup(name="FSA",
      version="1.0",
      description="FSA utilities",
      long_description=
      """This package contains functions for manipulating Finite-State Automata (FSAs).  It includes functions for minimizing and determinizing FSAs, computing FSA intersections and unions, compiling a (non-POSIX) regular expression into an FSA, and compiling a set of regular expression productions into a chart parser.""",
      author="Oliver Steele",
      author_email="steele@osteele.com",
      url="http://osteele.com/software/pyfsa/",
      py_modules=["FSA", "NumFSAUtils", "FSChartParser", "reCompiler"],
      data_files=["README.txt", "LICENSE.txt"]
      )

