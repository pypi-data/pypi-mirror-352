"GP and SP modeling package"

__version__ = "0.1.2"

from .build import build
from .constraints.gp import GeometricProgram
from .constraints.model import Model
from .constraints.set import ConstraintSet
from .constraints.sgp import SequentialGeometricProgram
from .constraints.sigeq import SignomialEquality
from .globals import NamedVariables, SignomialsEnabled, Vectorize, settings

# NOTE above: the Variable the user sees is not the Variable used internally
from .nomials import ArrayVariable, Monomial, NomialArray, Posynomial, Signomial
from .nomials import VectorizableVariable as Variable
from .nomials import VectorVariable
from .solution_array import SolutionArray
from .tools.docstring import parse_variables
from .units import DimensionalityError, units, ureg
from .varkey import VarKey

GPCOLORS = ["#59ade4", "#FA3333"]
GPBLU, GPRED = GPCOLORS

if "just built!" in settings:  # pragma: no cover
    print(
        f"""
GPkit is now installed with solver(s) {settings['installed_solvers']}
To incorporate new solvers at a later date, run `gpkit.build()`.

If you encounter any bugs or issues using GPkit, please open a new issue at
https://github.com/beautifulmachines/gpkit-core/issues/new.

Finally, we hope you find our documentation (https://gpkit.readthedocs.io/) and
engineering-design models (https://github.com/beautifulmachines/gpkit-models/)
useful for your own applications.

Enjoy!
"""
    )
