"""
Mscene is a Python library for creating science animations with Manim in Google Colab.

Home: https://mscene.curiouswalk.com
Repo: https://github.com/curiouswalk/mscene
"""

try:
    from IPython import get_ipython

except ImportError:
    pass

else:
    ipy = get_ipython()

    if ipy is not None:

        from .__main__ import main

        ipy.register_magic_function(main, "line", "mscene")


__about__ = """Mscene
--------
Version   0.1.4
Summary   Science animation with Manim in Colab
Homepage  https://mscene.curiouswalk.com
Author    CuriousWalk
License   MIT"""

__version__ = "0.1.4"
__author__ = "CuriousWalk"
__license__ = "MIT"
