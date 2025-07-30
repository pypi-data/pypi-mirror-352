
from typing import (
    Any,
    Callable,
    Iterable,
    Optional,
    Sequence,
    Type,
    TypeVar,
    Union
)

import numpy as np
from scipy import sparse as sp
from numbers import Number

_T = TypeVar('_T')
_U = TypeVar('_U')

__all__ = [
    "AttrConstClass",
    "ParamConstClass",
    "Column",
    "Constr",
    "Env",
    "GenConstr",
    "LinExpr",
    "MConstr",
    "MLinExpr",
    "MQConstr",
    "MQuadExpr",
    "MVar",
    "MindoptError",
    "Model",
    "PsdConstr",
    "PsdExpr",
    "PsdVar",
    "QConstr",
    "QuadExpr",
    "SOS",
    "TempConstr",
    "Var",
    "disposeDefaultEnv",
    "models",
    "multidict",
    "paramHelp",
    "quicksum",
    "read",
    "readParams",
    "resetParams",
    "setParam",
    "system",
    "tupledict",
    "tuplelist",
    "version",
    "writeParams",
    "CallbackClass",
    "StatusConstClass",
    "ErrorConstClass",
    "MDO",
]


class AttrConstClass:

    Activity: str = ...
    '''
    The primal activity
    '''

    ColBasis: str = ...
    '''
    The basis of a column
    '''

    ColName: str = ...
    '''
    The variable name
    '''

    ConstrName: str = ...
    '''
    Alias for RowName. The constraint name.
    '''

    Dim: str = ...
    '''
    The dimension of a PSD variable
    '''

    DualObjVal: str = ...
    '''
    The objective value of the dual solution
    '''

    DualSoln: str = ...
    '''
    The solution of dual variable
    '''

    GenConstrName: str = ...
    '''
    The name of this general constraint
    '''

    GenConstrType: str = ...
    '''
    The type of this general constraint
    '''

    HasDualRay: str = ...
    '''
    If the problem has dual ray
    '''

    HasPrimalRay: str = ...
    '''
    If the problem has primal ray
    '''

    HasSolution: str = ...
    '''
    If the problem has a solution
    '''

    IISCol: str = ...
    '''
    Alias for IISVar, to test if the upper and (or) lower bound(s) of this variable
    belong to IIS
    '''

    IISConstr: str = ...
    '''
    If the left-hand-side value and (or) right-hand-side value of this constraint
    belong to IIS
    '''

    IISRow: str = ...
    '''
    Alias for IISConstr, to test if the left-hand-side value and (or) right-hand-side
    value of this constraint belong to IIS
    '''

    IISVar: str = ...
    '''
    If the upper and/or lower bounds of this variable belong to IIS
    '''

    IPM_NumIters: str = ...
    '''
    The total number of iterations after an interior point method has completed.
    '''

    IsInteger: str = ...
    '''
    If a variable is of integral type
    '''

    LB: str = ...
    '''
    The lower bound of a variable
    '''

    LHS: str = ...
    '''
    The left-hand-side value of a constraint
    '''

    MIP_GapAbs: str = ...
    '''
    The absolute gap for a MIP solution. If the user wants to set the maximum tolerable
    gap before optimization, see parameter `MIP/GapAbs`.
    '''

    MIP_GapRel: str = ...
    '''
    The relative gap for a MIP solution. If the user wants to set the maximum tolerable
    gap before optimization, see parameter `MIP/GapRel`.
    '''

    MinSense: str = ...
    '''
    If the objective function is min sense
    '''

    ModelName: str = ...
    '''
    Alias for ProbName. The problem name
    '''

    ModelSense: str = ...
    '''
    The objective function sense, 1 for min and -1 for max
    '''

    NumConss: str = ...
    '''
    The total number of constraints
    '''

    NumConstrs: str = ...
    '''
    Alias for NumConss. The total number of constraints.
    '''

    NumEnts: str = ...
    '''
    The total number of constraint matrix non-zeros
    '''

    NumGenConstrs: str = ...
    '''
    The total number of general constraints.
    '''

    NumNZs: str = ...
    '''
    Alias for NumEnts. The total number of constraint matrix non-zeros
    '''

    NumPsdConstrs: str = ...
    '''
    The total number of PSD constraints
    '''

    NumPsdVars: str = ...
    '''
    The total number of PSD variables.
    '''

    NumQConstrs: str = ...
    '''
    The total number of quadratic constraints
    '''

    NumSOS: str = ...
    '''
    The total number of Special Ordered Set (SOS) constraints in the model
    '''

    NumVars: str = ...
    '''
    The total number of variables
    '''

    Obj: str = ...
    '''
    The objective coefficient of a variable
    '''

    ObjCon: str = ...
    '''
    Alias for ObjConst. The constant component of objective function
    '''

    ObjConst: str = ...
    '''
    The constant component of the objective function.
    '''

    ObjVal: str = ...
    '''
    Alias for PrimalObjVal. The objective value of primal solution
    '''

    PresolverTime: str = ...
    '''
    Presolver execution time in seconds
    '''

    PrimalObjVal: str = ...
    '''
    The objective value of the primal solution.
    '''

    PrimalSoln: str = ...
    '''
    The solution of the primal problem
    '''

    ProbName: str = ...
    '''
    The problem name
    '''

    PsdCLHS: str = ...
    '''
    psd constraint left-hand-side value
    '''

    PsdCName: str = ...
    '''
    The PSD constraint name
    '''

    PsdCRHS: str = ...
    '''
    PSD constraint right-hand-side value
    '''

    PsdObj: str = ...
    '''
    The objective coefficient of a PSD variable.
    '''

    PsdVarName: str = ...
    '''
    The PSD variable name
    '''

    PsdX: str = ...
    '''
    The solution of the PSD variable in the primal problem.
    '''

    QCDualSoln: str = ...
    '''
    The solution of the dual variable
    '''

    QCLHS: str = ...
    '''
    The left-hand-side value of a quadratic constraint
    '''

    QCName: str = ...
    '''
    The quadratic constraint name
    '''

    QCRHS: str = ...
    '''
    The right-hand-side value of a quadratic constraint
    '''

    RC: str = ...
    '''
    Alias for ReducedCost. The reduced cost
    '''

    RHS: str = ...
    '''
    The right-hand-side value of a constraint
    '''

    ReducedCost: str = ...
    '''
    The reduced cost
    '''

    RowBasis: str = ...
    '''
    The basis of a row
    '''

    RowName: str = ...
    '''
    The constraint name
    '''

    SPX_NumIters: str = ...
    '''
    The total number of iterations after a simplex method completed.
    '''

    SolCount: str = ...
    '''
    Total number of suboptimal solutions found.
    '''

    SolutionTime: str = ...
    '''
    Total execution time in seconds
    '''

    SolverTime: str = ...
    '''
    Solver execution time in seconds
    '''

    Start: str = ...
    '''
    The current MIP start vector
    '''

    Status: str = ...
    '''
    The optimization status after model optimized.
    '''

    UB: str = ...
    '''
    The upper bound of a variable
    '''

    VType: str = ...
    '''
    The variable type
    '''

    VarName: str = ...
    '''
    Alias for ColName, The variable name
    '''

    X: str = ...
    '''
    Alias for PrimalSoln. The solution of the primal problem.
    '''

    Xn: str = ...
    '''
    The suboptimal solution specified by parameter `MIP/SolutionNumber`.
    '''

class ParamConstClass:

    Dualization: str = ...
    '''
    Set whether to dualize the model.
    '''

    EnableNetworkFlow: str = ...
    '''
    Set whether to enable the network simplex method.
    '''

    EnableStochasticLP: str = ...
    '''
    Set whether to detect Stochastic Linear Programming problem structure.
    '''

    IPM_DualTolerance: str = ...
    '''
    Set the dual relative feasibility tolerance in the interior point method.
    '''

    IPM_GapTolerance: str = ...
    '''
    Set the dual relative gap tolerance in the interior point method.
    '''

    IPM_MaxIterations: str = ...
    '''
    Set the maximum number of iterations in the interior point method.
    '''

    IPM_NumericFocus: str = ...
    '''
    Set the efforts spent on detecting and handling numerical issues that may occur
    in IPM.
    '''

    IPM_PrimalTolerance: str = ...
    '''
    Set the primal relative feasibility tolerance in the interior point method.
    '''

    LogFile: str = ...
    '''
    Determines the name of the MindOpt log file. Modifying this parameter closes the
    current log file and opens the specified file. Use an empty string for no log
    file. Use OutputFlag to shut off all logging.
    '''

    LogToConsole: str = ...
    '''
    Enables or disables console logging. Use OutputFlag to shut off all logging.
    '''

    MIP_AllowDualPresolve: str = ...
    '''
    Specify whether to enable dual presolve methods in MIP.
    '''

    MIP_AutoConfiguration: str = ...
    '''
    Specify whether to enable automatic configuration for MIP.
    '''

    MIP_Cutoff: str = ...
    '''
    Set the objective cutoff to avoid finding solutions worse than this value in MIP
    '''

    MIP_DetectDisconnectedComponents: str = ...
    '''
    Specify whether to enable disconnected component strategy in MIP.
    '''

    MIP_EnableLazyConstr: str = ...
    '''
    Incorperating lazy constraints in the MILP solving process. If this option is
    activated, lazy constraint callbacks are invoked whenever a MILP solution is found.
    The generated lazy constraints are used by the solver to reduce the solution space.
    Note that some techniques, for instance, dual presolving reductions, are disabled
    under this option to avoid conflict with lazy constraints
    '''

    MIP_GapAbs: str = ...
    '''
    Set absolute gap allowed for a MIP model.
    '''

    MIP_GapRel: str = ...
    '''
    Set relative gap allowed for a MIP model.
    '''

    MIP_IntegerTolerance: str = ...
    '''
    Set the integer judgment precision in MIP solution.
    '''

    MIP_LevelCuts: str = ...
    '''
    Control the level of aggression of cut module, the larger the value, the more
    aggressive.
    '''

    MIP_LevelHeurs: str = ...
    '''
    Control the level of aggression of heuristic module, the larger the value, the
    more aggressive.
    '''

    MIP_LevelProbing: str = ...
    '''
    Control the level of aggression of probing module, the larger the value, the more
    aggressive.
    '''

    MIP_LevelStrong: str = ...
    '''
    Control the level of aggression of strong-branching module, the larger the value,
    the more aggressive.
    '''

    MIP_LevelSubmip: str = ...
    '''
    Control the level of aggression of submip module, the larger the value, the more
    aggressive.
    '''

    MIP_LinearizationBigM: str = ...
    '''
    Set the largest coefficient for reformulating the non-linear functions in MIP
    '''

    MIP_MaxNodes: str = ...
    '''
    Set maximum node limit in MIP
    '''

    MIP_MaxSols: str = ...
    '''
    Set the maximum solution limit in MIP.
    '''

    MIP_MaxStallingNodes: str = ...
    '''
    Set the maximum allowed stalling nodes.
    '''

    MIP_ObjectiveTolerance: str = ...
    '''
    Set the objective value comparison accuracy in MIP solution.
    '''

    MIP_RootParallelism: str = ...
    '''
    Set the maximum number of concurrent threads allowed by the root node in MIP.
    '''

    MIP_SolutionNumber: str = ...
    '''
    Set the index of suboptimal solution to get. After parameter set, access attribute
    Xn to retrieve corresponding suboptimal solution.
    '''

    MIP_SolutionPoolSize: str = ...
    '''
    Set the maximum number of solutions to be stored for obtaining in MIP.
    '''

    MaxTime: str = ...
    '''
    Set the maximum solve time.
    '''

    Method: str = ...
    '''
    Set the selected optimization method.
    '''

    NumThreads: str = ...
    '''
    Set the number of threads to be utilized.
    '''

    NumericFocus: str = ...
    '''
    Set the efforts spent on detecting and handling numerical issues that may occur
    in MIP.
    '''

    OutputFlag: str = ...
    '''
    Enables or disables solver output. Use LogFile and LogToConsole for finer-grain
    control.
    '''

    PostScaling: str = ...
    '''
    Set the method of post scaling used.
    '''

    Presolve: str = ...
    '''
    Set whether to enable the presolver method.
    '''

    PresolveTolerance: str = ...
    '''
    Set the numerical accuracy when presolving continuous problems(internal use, not
    revealed in doc)
    '''

    SPX_ColumnGeneration: str = ...
    '''
    Set whether to use column generation in the simplex method.
    '''

    SPX_CrashStart: str = ...
    '''
    Set whether to use the initial basis solution generation method in the simplex
    method.
    '''

    SPX_DualPricing: str = ...
    '''
    Setting the dual pricing strategy in the simplex method.
    '''

    SPX_DualTolerance: str = ...
    '''
    Set the dual feasibility tolerance for the simplex method
    '''

    SPX_MaxIterations: str = ...
    '''
    Set the maximum number of iterations in the simplex method
    '''

    SPX_PrimalPricing: str = ...
    '''
    Setting the primal pricing strategy in the simplex method.
    '''

    SPX_PrimalTolerance: str = ...
    '''
    Set the primal feasibility tolerance for the simplex method.
    '''

    SolutionTarget: str = ...
    '''
    Set the target of solution in LP problem.
    '''

class Column:

    def __init__(self, coeffs: Union[Number, list, tuple, np.ndarray] = None, constrs: Union[Constr, list[Constr]] = None) -> None:
        '''
        Construct a Column

        Parameters
        ----------
        coeffs: Union[Number, list, tuple, np.ndarray] = None
            The initial coefficient of the Column, which can be a number or an array.

        constrs: Union[Constr, list[Constr]] = None
            The initial constraint of the Column, which can be a constraint or an array.

        Examples
        --------
        >>> Column(1, c0)
        >>> Column([1, 2, 3], [c0, c1, c2])

        '''

    def addTerms(self, coeffs: Union[Number, list, tuple, np.ndarray], constrs: Union[Constr, list[Constr]] = None) -> None:
        '''
        Add one or more term(s)

        Parameters
        ----------
        coeffs: Union[Number, list, tuple, np.ndarray]
            The coefficient of the term(s) to be added, which can be a number or an array.

        constrs: Union[Constr, list[Constr]] = None
            The constraint of the term(s) to be added, which can be a single constraint or an
            array.

        Examples
        --------
        >>> column.addTerms([1, 2], [c0, c1])
        >>> column.addTerms(1, c0)

        '''

    def clear(self) -> None:
        '''
        Clear all included terms

        Examples
        --------
        >>> column = Column([1, 2], [c0, c1])
        >>> column.clear()
        >>> print(column.size() == 0)

        '''

    def copy(self) -> Column:
        '''
        Return a copy of a Column.

        Examples
        --------
        >>> another = column.copy()

        '''

    def getCoeff(self, index: int) -> float:
        '''
        Obtain the coefficient of a term in a Column.

        Parameters
        ----------
        index: int
            The index of the term to obtain the coefficient.

        Examples
        --------
        >>> column = Column([1, 2], [c0, c1])
        >>> print(column.getCoeff(1) == 2.0)

        '''

    def getConstr(self, index: int) -> Constr:
        '''
        Get the constraint of a term in a Column.

        Parameters
        ----------
        index: int
            The index of the term to obtain the constraint.

        Examples
        --------
        >>> column = Column([1, 2], [c0, c1])
        >>> print(column.getConstr(1).sameAs(c1))

        '''

    def remove(self, item: Union[int, Constr]) -> None:
        '''
        Delete some terms contained in Column.

        Parameters
        ----------
        item: Union[int, Constr]
            If `item` is a number, the term whose index is `item` is deleted. If `item` is a
            constraint, all terms that contain the constraint are deleted.

        Examples
        --------
        >>> column = Column([1, 2], [c0, c1])
        >>> column.remove(0)
        >>> column.remove(c1)
        >>> print(column.size() == 0)

        '''

    def size(self) -> int:
        '''
        Obtain the number of terms.

        Examples
        --------
        >>> column = Column([1, 2], [c0, c1])
        >>> print(column.size() == 2)

        '''

class Constr:

    def getAttr(self, attrname: str) -> Union[int, float, str]:
        '''
        Obtain the attribute value associated with the constraint.

        Parameters
        ----------
        attrname: str
            Attribute name

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVar()
        >>> c = m.addConstr(2 * x <= 1)
        >>> print(c.rhs)
        >>> print(c.getAttr(MDO.Attr.RHS))

        Notes
        -----
        Attributes can also be read and written directly through object attributes; in
        this case, the attribute name is case-insensitive
        '''

    index: int = ...
    '''
    The index of the constraint.
    '''

    def sameAs(self, constr: Constr) -> bool:
        '''
        Test whether the constraint is the same as another constraint.

        Parameters
        ----------
        constr: Constr
            Another constraint to be tested.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVar()
        >>> c = m.addConstr(2 * x <= 1)
        >>> assert (c.sameAs(m.getConstrs()[0]))

        '''

    def setAttr(self, attrname: str, attrvalue: Union[int, float, str]) -> None:
        '''
        Set the attribute value associated with the constraint.

        Parameters
        ----------
        attrname: str
            The name of the attribute.

        attrvalue: Union[int, float, str]
            The value of the attribute to be set.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVar()
        >>> c = m.addConstr(2 * x <= 1)
        >>> c.rhs = 2.0
        >>> c.setAttr(MDO.Attr.RHS, 2.0)

        Notes
        -----
        Attribute can also be read and written directly through object attributes; in this
        case, the attribute name is case-insensitive.
        '''

    RowName: str = ...
    '''
    The constraint name
    '''

    ConstrName: str = ...
    '''
    Alias for RowName. The constraint name.
    '''

    RowBasis: str = ...
    '''
    The basis of a row
    '''

    LHS: str = ...
    '''
    The left-hand-side value of a constraint
    '''

    RHS: str = ...
    '''
    The right-hand-side value of a constraint
    '''

    Activity: str = ...
    '''
    The primal activity
    '''

    DualSoln: str = ...
    '''
    The solution of dual variable
    '''

class Env:

    def __init__(self, logfilename: str = '', empty: bool = False) -> None:
        '''
        Construct an Environment,

        Parameters
        ----------
        logfilename: str = ''
            Set the log file name of the Environment.

        empty: bool = False
            Indicate whether to construct an empty Environment.

        Examples
        --------
        >>> Env("env1.log")
        >>> env = Env("env1.log", True)
        >>> env.start()

        '''

    def dispose(self) -> None:
        '''
        Release the resources associated with the Environment.

        Examples
        --------
        >>> env.dispose()

        '''

    def resetParam(self) -> None:
        '''
        Reset all parameters to default values.

        Examples
        --------
        >>> env.resetParam()

        '''

    def setParam(self, paramname: str, paramvalue: Union[int, float, str]) -> None:
        '''
        Set the value of a parameter.

        Parameters
        ----------
        paramname: str
            The name of the parameter to be set.

        paramvalue: Union[int, float, str]
            Parameter value.

        Examples
        --------
        >>> env.setParam("MaxTime", 10)
        >>> env.setParam("MaxTi*", 10)
        >>> env.setParam("MaxTi*", "default")

        Notes
        -----
        1. Parameter names can contain '*' and '?' wildcards. If more than one parameter name
           is matched, the parameter values are not modified.
        2. When the parameter value is 'default', you can reset the parameter to its default
           value.
        '''

    def start(self) -> None:
        '''
        start an Environment. When the Environment is empty, you must call start before
        you can use it. Environment starting, the parameter loading and license checking
        will be performed.

        Examples
        --------
        >>> env = Env("env1.log", True)
        >>> env.start()

        '''

    def writeParams(self, filename: str) -> None:
        '''
        Write parameter settings to a file.

        Parameters
        ----------
        filename: str
            The name of the file.

        Examples
        --------
        >>> env.writeParams("settings.prm")

        '''

class GenConstr:

    def getAttr(self, attrname: str) -> Union[int, float, str]:
        '''
        Obtain the attribute value of a general constraint.

        Parameters
        ----------
        attrname: str
            Attribute name

        Notes
        -----
        Attributes can also be read and written directly through object attributes, in
        this case, the attribute name is case-insensitive
        '''

    index: int = ...
    '''
    The index position of the general constraint.
    '''

    def sameAs(self, genconstr: GenConstr) -> bool:
        '''
        Test whether the general constraint is the same as another general constraint.

        Parameters
        ----------
        genconstr: GenConstr
            Another general constraint to be tested.

        Examples
        --------
        >>> m = Model()
        >>> b = m.addVar(vtype='B')
        >>> x = m.addVar()
        >>> y = m.addVar()
        >>> gc = m.addGenConstrIndicator(b, True, x + y <= 3)
        >>> print(gc.sameAs(m.getGenConstrs()[0]))

        '''

    def setAttr(self, attrname: str, attrvalue: Union[int, float, str]) -> None:
        '''
        Set the attribute value of general constraint.

        Parameters
        ----------
        attrname: str
            The name of the attribute.

        attrvalue: Union[int, float, str]
            The value of the attribute to be set.

        Notes
        -----
        Attribute can also be read and written directly through object attributes; in this
        case, the attribute name is case-insensitive.
        '''

class LinExpr:

    def __init__(self, arg1: Union[Number, Var, tuple, list, np.ndarray] = 0, arg2: Union[tuple, list, np.ndarray] = None) -> None:
        '''
        Construct a linear expression

        Parameters
        ----------
        arg1: Union[Number, Var, tuple, list, np.ndarray] = 0
            When two parameters are provided during a call, arg1 is usually a coefficient or
            a list of coefficients.

        arg2: Union[tuple, list, np.ndarray] = None
            When two parameters are provided during a call, arg2 is usually a variable or a
            list of variables.

        Examples
        --------
        >>> LinExpr((1, 2, 3), (x, y, z))
        >>> LinExpr(2, y)
        >>> LinExpr(x)
        >>> LinExpr(2 * x + 1)
        >>> LinExpr(1)

        '''

    def add(self, expr: LinExpr, mult: Number = 1.0) -> None:
        '''
        Add all terms of another linear expression to the current linear expression.

        Parameters
        ----------
        expr: LinExpr
            Another linear expression.

        mult: Number = 1.0
            Multiplier. Default value: 1.0.

        Examples
        --------
        >>> linExpr.add(expr, -1)

        '''

    def addConstant(self, c: Number) -> None:
        '''
        Add a value to the constant term of the linear expression.

        Parameters
        ----------
        c: Number
            The value to be added. A negative number indicates that the value should be
            subtracted.

        Examples
        --------
        >>> linExpr.addConstant(-linExpr.getConstant())

        '''

    def addTerms(self, coeffs: Union[Number, tuple, list, np.ndarray], vars: Union[Var, tuple, list, np.ndarray]) -> None:
        '''
        Add one or more term(s)

        Parameters
        ----------
        coeffs: Union[Number, tuple, list, np.ndarray]
            The coefficient of the term(s) to be added, which may be a number or an array.

        vars: Union[Var, tuple, list, np.ndarray]
            The variable of the term(s) to be added, which can be a single variable or an
            array.

        Examples
        --------
        >>> linExpr.addTerms([1, 2], [x, y])
        >>> linExpr.addTerms(1, x)

        '''

    def clear(self) -> None:
        '''
        Clear all included terms and set the constant to 0

        Examples
        --------
        >>> linExpr = 2 * x +3 * y +1
        >>> linExpr.clear()
        >>> print(linExpr.size() == 0)
        >>> print(linExpr.getConstant() == 0)

        '''

    def getCoeff(self, index: int) -> float:
        '''
        Obtain the coefficient of a term in a linear expression.

        Parameters
        ----------
        index: int
            The index of the term to obtain the coefficient.

        Examples
        --------
        >>> linExpr = 2 * x + 1 * y
        >>> print(linExpr.getCoeff(1) == 1.0)

        '''

    def getConstant(self) -> float:
        '''
        Obtain the constant term of a linear expression.

        Examples
        --------
        >>> linExpr.addConstant(-linExpr.getConstant())

        '''

    def getValue(self) -> float:
        '''
        After solving the problem, obtain the value of the linear expression

        Examples
        --------
        >>> m.optimize()
        >>> linExpr = 2 * x + y * 1
        >>> print(linExpr.getValue())

        '''

    def getVar(self, index: int) -> Var:
        '''
        Get the variable of a term in a linear expression

        Parameters
        ----------
        index: int
            The index of the term to obtain the variable from

        Examples
        --------
        >>> linExpr = 2 * x + 1 * y
        >>> print(linExpr.getVar(1).sameAs(y))

        '''

    def remove(self, item: Union[int, Var]) -> None:
        '''
        Delete terms from an expression based on specified criteria.

        Parameters
        ----------
        item: Union[int, Var]
            If `item` is a number, the term at the index `item` is deleted. If `item` is a
            variable, all terms containing this variable are deleted.

        Examples
        --------
        >>> linExpr = 2 * x + 3 * y + 4 * x
        >>> linExpr.remove(1)
        >>> linExpr.remove(x)
        >>> print(linExpr.size() == 0)

        '''

    def size(self) -> int:
        '''
        Obtain the number of terms, excluding constant terms.

        Examples
        --------
        >>> linExpr = 2 * x + 3 * y + 1
        >>> print(linExpr.size() == 2)

        '''

class MConstr:

    def getAttr(self, attrname: str) -> list[Union[int, float, str]]:
        '''
        Obtain the value of the associated attribute.

        Parameters
        ----------
        attrname: str
            The name of the attribute to obtain the value.

        Examples
        --------
        >>> m = Model()
        >>> mat = m.addMVar((2, 2))
        >>> c = m.addMConstr([[1, 2], [3, 4]], mat[0], '<', [1, 2])
        >>> c.constrname = ["c0", "c1"]
        >>> print(c.constrname)
        >>> print(c.getAttr(MDO.Attr.ConstrName))

        Notes
        -----
        Attribute can also be read and written directly through object attributes; in this
        case, the attribute name is case-insensitive.
        '''

    def item(self) -> Constr:
        '''
        Get the unique constraint contained in the current MConstr.

        Examples
        --------
        >>> mat = m.addMVar((2, 2))
        >>> c = m.addMConstr([[1, 2], [3, 4]], mat[0], '<', [1, 2])
        >>> first = c[0]
        >>> print(type(first))
        >>> print(type(first.item()))

        Notes
        -----
        An exception is thrown if the current MConstr contains more than one constraint.
        '''

    ndim: int = ...
    '''
    Number of MConstr dimensions
    '''

    def setAttr(self, attrname: str, attrvalues: list[Union[int, float, str]]) -> None:
        '''
        Set the value of the associated attribute.

        Parameters
        ----------
        attrname: str
            The name of the attribute to be set.

        attrvalues: list[Union[int, float, str]]
            The new value of the attribute to be set. Can be scalar or array.

        Examples
        --------
        >>> m = Model()
        >>> mat = m.addMVar((2, 2))
        >>> c = m.addMConstr([[1, 2], [3, 4]], mat[0], '<', [1, 2])
        >>> c.constrname = ["c0", "c1"]
        >>> c.setAttr(MDO.Attr.RHS, 5.0)

        Notes
        -----
        Attribute can also be read and written directly through object attributes; in this
        case, the attribute name is case-insensitive.
        '''

    shape: tuple = ...
    '''
    Shape of the MConstr.
    '''

    size: int = ...
    '''
    Number of constraints contained in the MConstr
    '''

    def tolist(self) -> list[Constr]:
        '''
        Return an array containing all constraints in the current MConstr.

        Examples
        --------
        >>> mat = m.addMVar((2, 2))
        >>> c = self.m.addMConstr([[1, 2], [3, 4]], mat[0], '<', [1, 2])
        >>> print(c.tolist())

        '''

class MLinExpr:

    def clear(self) -> None:
        '''
        Perform the clear operation on all contained linear expressions, that is, all
        contained linear expressions become empty expressions.

        Examples
        --------
        >>> mLinExpr.clear()
        >>> print(mLinExpr[0, 0].item().size() == 0)

        '''

    def copy(self) -> MLinExpr:
        '''
        Return a copy of the MLinExpr.

        Examples
        --------
        >>> another = mLinExpr.copy()

        '''

    def getValue(self) -> np.ndarray[np.float64]:
        '''
        After the problem is solved, the values of all linear expressions are returned.

        Examples
        --------
        >>> m.optimize()
        >>> print(mLinExpr.getValue()[0, 0])

        '''

    def item(self) -> LinExpr:
        '''
        Get the unique expression contained in the current MLinExpr.

        Examples
        --------
        >>> mat = m.addMVar((2, 2))
        >>> mLinExpr = mat + 1
        >>> first = mLinExpr[0, 0]
        >>> print(type(first))
        >>> print(type(first.item()))

        Notes
        -----
        An exception is thrown if the current MLinExpr contains more than one expression.
        '''

    ndim: int = ...
    '''
    Number of MLinExpr dimensions
    '''

    shape: tuple = ...
    '''
    Shape of the MLinExpr
    '''

    size: int = ...
    '''
    Number of expressions contained in the MLinExpr
    '''

    def sum(self, axis: int = None) -> MLinExpr:
        '''
        Sum all included expressions and return the summed result.

        Parameters
        ----------
        axis: int = None
            Sum along the axis

        Examples
        --------
        >>> mat = m.addMVar((2, 2))
        >>> mLinExpr = mat +1
        >>> print(mLinExpr.sum().getConstant() == 4)

        '''

    def zeros(self, shape) -> MLinExpr:
        '''
        Return a MLinExpr of the specified shape, which contains empty expressions.

        Parameters
        ----------
        shape
            The shape to be specified.

        Examples
        --------
        >>> mLinExpr = MLinExpr.zeros((2, 2))
        >>> mLinExpr += x
        >>> print(mLinExpr[0, 0].item().size() == 1)

        '''

class MQConstr:

    def getAttr(self, attrname: str) -> list[Union[int, float, str]]:
        '''
        Obtain the value of the associated attribute.

        Parameters
        ----------
        attrname: str
            The name of the attribute to obtain the value.

        Notes
        -----
        Attribute can also be read and written directly through object attributes, in this
        case, the attribute name is case-insensitive
        '''

    def item(self) -> QConstr:
        '''
        Get the unique quadratic constraint contained in this MQConstr.

        Notes
        -----
        An exception is thrown if this MQConstr contains more than one quadratic
        constraint.
        '''

    ndim: int = ...
    '''
    Number of MQConstr dimensions
    '''

    def setAttr(self, attrname: str, attrvalue: list[Union[int, float, str]]) -> None:
        '''
        Set the value of the associated attribute.

        Parameters
        ----------
        attrname: str
            The name of the attribute to be set.

        attrvalue: list[Union[int, float, str]]
            The new value of the attribute to be set. Can be scalar or array

        Notes
        -----
        Attribute can also be read and written directly through object attributes, in this
        case, the attribute name is case-insensitive.
        '''

    shape: tuple = ...
    '''
    Shape of the MQConstr
    '''

    size: int = ...
    '''
    Number of quadratic constraints contained in the MQConstr
    '''

    def tolist(self) -> list[QConstr]:
        '''
        Return an array containing all quadratic constraints in this MQConstr.

        '''

class MQuadExpr:

    def clear(self) -> None:
        '''
        Perform the clear operation on all contained quadratic expressions, that is, all
        contained quadratic expressions become empty expressions.

        Examples
        --------
        >>> mQuadExpr.clear()
        >>> print(mQuadExpr[0, 0].item().size() == 0)

        '''

    def copy(self) -> MQuadExpr:
        '''
        Return a copy of the MQuadExpr.

        Examples
        --------
        >>> another = mQuadExpr.copy()

        '''

    def getValue(self) -> np.ndarray[np.float64]:
        '''
        After the problem is solved, the values of all quadratic expressions are returned.

        Examples
        --------
        >>> m.optimize()
        >>> print(mQuadExpr.getValue()[0, 0])

        '''

    def item(self) -> QuadExpr:
        '''
        Get the unique expression contained in the current MQuadExpr.

        Examples
        --------
        >>> mat = m.addMVar((2, 2))
        >>> mQuadExpr = mat * mat[0, 0].item()
        >>> first = mQuadExpr[0, 0]
        >>> print(type(first))
        >>> print(type(first.item()))

        Notes
        -----
        An exception is thrown if the current MQuadExpr contains more than one expression.
        '''

    ndim: int = ...
    '''
    Number of MQuadExpr dimensions
    '''

    shape: tuple = ...
    '''
    Shape of the MQuadExpr
    '''

    size: int = ...
    '''
    Number of expressions contained in the QuadExpr
    '''

    def sum(self, axis: None) -> MQuadExpr:
        '''
        Sum all included expressions and return the summed result.

        Parameters
        ----------
        axis: None
            Sum along the axis

        Examples
        --------
        >>> mat = m.addMVar((2, 2))
        >>> mQuadExpr = mat * mat[0, 0].item()
        >>> print(mQuadExpr.sum().size == 1)

        '''

    def zeros(self, shape) -> MQuadExpr:
        '''
        Return a MQuadExpr of the specified shape containing empty expressions.

        Parameters
        ----------
        shape
            The shape to be specified.

        Examples
        --------
        >>> mQuadExpr = MQuadExpr.zeros((2, 2))
        >>> mQuadExpr += x * x
        >>> print(mQuadExpr[0, 0].item().size() == 1)

        '''

class MVar:

    T: MVar = ...
    '''
    Obtain the transpose of MVar
    '''

    def copy(self) -> MVar:
        '''
        Return a copy of the current MVar.

        Examples
        --------
        >>> mat1 = mat.copy()

        '''

    def diagonal(self) -> MVar:
        '''
        Obtain the diagonal elements of the matrix MVar.

        Examples
        --------
        >>> print(mat.diagonal())

        '''

    def fromlist(self, li) -> MVar:
        '''
        Wrap a set of variables as a MVar

        Parameters
        ----------
        li
            List of variables

        Examples
        --------
        >>> m = Model()
        >>> mat = MVar.fromlist([x0, x1, x2, x3]).reshape(2, 2)

        '''

    def fromvar(self, var) -> MVar:
        '''
        Wrap a variable as a MVar

        Parameters
        ----------
        var
            Variables to be packaged

        Examples
        --------
        >>> mat11 = MVar.fromvar(x)

        '''

    def getAttr(self, attrname: str) -> np.ndarray[Union[int, float, str]]:
        '''
        Obtain the attribute values associated with MVar.

        Parameters
        ----------
        attrname: str
            The name of the attribute.

        Examples
        --------
        >>> m = Model()
        >>> mat = m.addMVar((2, 2))
        >>> print(mat.lb)
        >>> print(mat.getAttr(MDO.Attr.LB))

        Notes
        -----
        Attribute can also be read and written directly through object attributes; in this
        case, the attribute name is case-insensitive.
        '''

    def item(self) -> Var:
        '''
        Obtain the unique variable contained in the current MVar.

        Examples
        --------
        >>> mat = m.addMVar((2, 2))
        >>> first = mat[0, 0]
        >>> print(type(first))
        >>> print(type(first.item()))

        Notes
        -----
        If the current MVar contains more than one variable, an exception is thrown.
        '''

    ndim: int = ...
    '''
    Number of MVar dimensions
    '''

    def reshape(self, *shape) -> MVar:
        '''
        Return a MVar with the same data but a new shape.

        Parameters
        ----------
        *shape
            New shape

        Examples
        --------
        >>> m = Model()
        >>> mat = m.addMVar((2, 2))
        >>> x = mat.reshape(1, 4)  # default to fold along rows
        >>> x_c = mat.reshape(-1, order='C')  # fold along rows
        >>> x_f = mat.reshape(-1, order='F')  # fold along columns

        '''

    def setAttr(self, attrname: str, attrvalues: list[Union[int, float, str]]) -> None:
        '''
        Set the attribute values associated with MVar.

        Parameters
        ----------
        attrname: str
            The name of the attribute to be set.

        attrvalues: list[Union[int, float, str]]
            The new value of the attribute to be set. Can be scalar or array.

        Examples
        --------
        >>> m = Model()
        >>> mat = m.addMVar((2, 2))
        >>> mat.lb = [1.0, 2.0, 3.0, 4.0]
        >>> mat.setAttr(MDO.Attr.LB, 5.0)

        Notes
        -----
        Attributes can also be read and written directly through object attributes; in
        this case, the attribute name is case-insensitive.
        '''

    shape: tuple = ...
    '''
    Shape of MVar
    '''

    size: int = ...
    '''
    Number of variables contained in MVar
    '''

    def sum(self, axis: None) -> LinExpr:
        '''
        Return a linear expression that sums all variables in MVar

        Parameters
        ----------
        axis: None
            Sum along the specified axis

        Examples
        --------
        >>> linExpr = mat.sum()

        '''

    def tolist(self) -> list[Var]:
        '''
        Return an array of all variables in the current MVar

        Examples
        --------
        >>> mat = m.addMVar((2,))
        >>> x = mat.tolist()
        >>> print(x[0] ** 2 + 2 * x[0] * x[1] + x[1] ** 2)

        '''

    def transpose(self) -> MVar:
        '''
        The transpose of a matrix variable (MVar)

        Examples
        --------
        >>> print(mat.transpose())

        '''

class MindoptError:

    errno: int = ...
    '''
    The error code corresponding to the current exception.
    '''

    message: str = ...
    '''
    Text description corresponding to the current exception
    '''

class Model:

    def __init__(self, name: str = '', env: Env = None) -> None:
        '''
        Construct a Model.

        Parameters
        ----------
        name: str = ''
            The name of the Model.

        env: Env = None
            The Environment corresponding to the Model. If `env` is None, the default Environment
            is used.

        Examples
        --------
        >>> Model()
        >>> Model("DietProblem")
        >>> env = Env("env.log")
        >>> Model("", env)

        '''

    def addConstr(self, tmpConstr: TempConstr, name: str = '') -> Union[Constr, QConstr, MConstr, PsdConstr]:
        '''
        Add a constraint. The return value may be a Constr or QConstr, PsdConstr, MConstr,
        or MQConstr, depending on the value of the TempConstr.

        Parameters
        ----------
        tmpConstr: TempConstr
            The TempConstr to be added. TempConstr objects are typically obtained by using
            comparison operators among the following types:
                * Var
                * MVar
                * LinExpr
                * MLinExpr
                * QuadExpr
                * MQuadExpr
                * PsdExpr

        name: str = ''
            The name of the constraint. If a MConstr or MQConstr is returned, a subscript is
            appended to the name of each constraint as a suffix.

        Examples
        --------
        >>> x = m.addVar()
        >>> mat = m.addMVar((2, 2))
        >>> m.addConstr(x + 1 <= 2, name="Constr")
        >>> m.addConstr(mat + 1 <= 2, name="MConstr")
        >>> coeff = numpy.array([[2, 1], [1, 2]])
        >>> px = m.addPsdVar(dim = 2)
        >>> m.addConstr(coeff * px == 2, name="PsdConstr")

        '''

    def addConstrs(self, generator: GenConstr, name: str = '') -> tupledict[Union[int, Iterable[int]], Union[Constr, QConstr, MConstr, PsdConstr]]:
        '''
        Add a set of constraints. Returns a tupledict where the key is the index of the
        constraint, generated by the generator, and the value is the constraint itself.

        Parameters
        ----------
        generator: GenConstr
            Constraint generator that yields constraints.

        name: str = ''
            The name of the constraint. If the name is not None or an empty string, a subscript
            is appended to the name of each constraint as a suffix.

        Examples
        --------
        >>> v = m.addMVar((2, 2))
        >>> c = m.addConstrs((v[i, j].item() <= 1 for i in range(2) for j in range(2)), name='c')

        Notes
        -----
        If the generator does not provide a subscript, an exception will be thrown.
        '''

    def addGenConstrIndicator(self, binvar: Var, binval: bool, lhs: Union[float, Var, LinExpr, TempConstr], sense: str = None, rhs: float = None, name: str = "") -> GenConstr:
        '''
        Add a new indicator constraint to model.

        Parameters
        ----------
        binvar: Var
            The binary variable of new indicator constraint.

        binval: bool
            The binary value when indicator constraint take effect.

        lhs: Union[float, Var, LinExpr, TempConstr]
            Can be one of the types `float`, `Var`, `LinExpr`, or `TempConstr`. It is the
            left-hand-side value of the new indicator constraint.

        sense: str = None
            The sense of new constraint. Possible values are:
                * MDO.LESS_EQUAL('<')
                * MDO.GREATER_EQUAL('>')
                * MDO.EQUAL('=')

        rhs: float = None
            The right-hand-side value of new constraint.

        name: str = ""
            The name of new constraint.

        Notes
        -----
        If `lhs` is of type `TempConstr`, argument `sense` and `rhs`  should be None.
        '''

    def addLConstr(self, lhs: Union[TempConstr, Number, Var, LinExpr], sense: str = None, rhs: Union[Number, Var, LinExpr] = None, name: str = '') -> Constr:
        '''
        Add a linear constraint

        Parameters
        ----------
        lhs: Union[TempConstr, Number, Var, LinExpr]
            The left part of the constraint. Can be TempConstr, in which case sense and rhs
            are ignored. It can also be a number, a variable, or a linear expression.

        sense: str = None
            The sense of the constraint. Possible values are:
                * MDO.LESS_EQUAL('<')
                * MDO.GREATER_EQUAL('>')
                * MDO.EQUAL('=')
            Default value is MDO.LESS_EQUAL

        rhs: Union[Number, Var, LinExpr] = None
            The right part of the constraint. Can be a number, a variable, or a linear
            expression

        name: str = ''
            The name of the constraint.

        Examples
        --------
        >>> m.addLConstr(linExpr, '>', 0)

        '''

    def addMConstr(self, A: Union[list, np.ndarray], x: Union[list, MVar, np.ndarray], sense: Union[str, list, np.ndarray], b: Union[list, np.ndarray], name: str = '') -> MConstr:
        '''
        Add a set of constraints in form Ax <= B. Return a MConstr object.

        Parameters
        ----------
        A: Union[list, np.ndarray]
            A two-dimensional array or numpy.ndarray. Coefficient matrix

        x: Union[list, MVar, np.ndarray]
            The variable vector, which can be a one-dimensional array or numpy.ndarray. All
            variables of the model are used when None is set.

        sense: Union[str, list, np.ndarray]
            It can be a character, a one-dimensional array, or a numpy.ndarray, indicating a
            comparison character in a constraint. A comparison charater can be one of:
                * MDO.LESS_EQUAL('<')
                * MDO.GREATER_EQUAL('>')
                * MDO.EQUAL('=')

        b: Union[list, np.ndarray]
            The right value of the constraint. It can be a one-dimensional array or
            numpy.ndarray.

        name: str = ''
            The name of the constraint. If the name is not None, a subscript is appended to
            the name of the constraint as the suffix.

        '''

    def addMVar(self, shape: tuple[int, ...], lb: Union[Number, list, np.ndarray] = 0.0, ub: Union[Number, list, np.ndarray] = float('inf'), obj: Union[Number, list, np.ndarray] = 0.0, vtype: Union[str, list, np.ndarray] = 'C', name: Union[str, list, np.ndarray] = '') -> MVar:
        '''
        Add a MVar

        Parameters
        ----------
        shape: tuple[int, ...]
            Specifies the shape of the MVar to be added.

        lb: Union[Number, list, np.ndarray] = 0.0
            The lower bound of all variables in MVar, It can be a single number, array, or
            numpy.ndarray. If it is numpy.ndarray, the corresponding shape is required.

        ub: Union[Number, list, np.ndarray] = float('inf')
            The upper bound of all variables in MVar. It can be a single number, array, or
            numpy.ndarray. If it is numpy.ndarray, the corresponding shape is required.

        obj: Union[Number, list, np.ndarray] = 0.0
            The coefficients of all variables in MVar in the objective function. It can be a
            single number, array, or numpy.ndarray. If it is numpy.ndarray, the corresponding
            shape is required.

        vtype: Union[str, list, np.ndarray] = 'C'
            The type of all variables in MVar, which can be a single character, array, or
            numpy.ndarray. If numpy.ndarray is set, the corresponding shape is required.
            The type of variable includes:
                * MDO.CONTINUOUS('C') for continuous variable
                * MDO.BINARY('B') for binary variable
                * MDO.INTEGER('I') for integral variable
                * MDO.SEMICONT('S') for semi-continuous variable
                * and MDO.SEMIINT('N') for semi-integral variable

        name: Union[str, list, np.ndarray] = ''
            The names of all variables in MVar. If it is not None, the variable name is name
            plus the corresponding subscript.

        Examples
        --------
        >>> m.addMVar((2, 2))
        >>> m.addMVar((2, 2), lb = 0)
        >>> m.addMVar((2, 2), lb = [1, 2, 3, 4])

        '''

    def addPsdVar(self, dim: int = 0, obj: Union[np.ndarray, sp.spmatrix] = None, name: str = '') -> PsdVar:
        '''
        Add a PsdVar.

        Parameters
        ----------
        dim: int = 0
            Matrix dimension of the PsdVar

        obj: Union[np.ndarray, sp.spmatrix] = None
            The objective coefficient of the PsdVar, it is a symmetric square matrix.

        name: str = ''
            The name of the PsdVar.

        Examples
        --------
        >>> m.addPsdVar(dim = 2, "X0")
        >>> m.addPsdVar(obj = mat)

        Notes
        -----
        Arguments `dim` and `obj`, you must specify exactly one.
        '''

    def addQConstr(self, lhs: Union[TempConstr, Number, Var, LinExpr, QuadExpr], sense: str = None, rhs: Union[Number, Var, LinExpr, QuadExpr] = None, name: str = '') -> QConstr:
        '''
        Add a quadratic constraint

        Parameters
        ----------
        lhs: Union[TempConstr, Number, Var, LinExpr, QuadExpr]
            The left-hand side of the constraint. Can be a TempConstr, in which case sense
            and rhs are ignored. It can also be a number, a variable, a linear expression, or
            a quadratic expression.

        sense: str = None
            The sense of the constraint. Possible values are:
                * MDO.LESS_EQUAL('<')
                * MDO.GREATER_EQUAL('>')
                * MDO.EQUAL('=')
            Default value is MDO.LESS_EQUAL

        rhs: Union[Number, Var, LinExpr, QuadExpr] = None
            The right-hand side of the constraint. Can be a number, a variable, a linear
            expression, or a quadratic expression.

        name: str = ''
            The name of the new constraint.

        Notes
        -----
        If the expressions contain no quadratic terms, the method will raise an error.
        '''

    def addRange(self, expr: Union[Number, Var, LinExpr ,PsdExpr], lower: Number = None, upper: Number = None, name: str = '') -> Union[Constr, PsdConstr]:
        '''
        Add a range constraint

        Parameters
        ----------
        expr: Union[Number, Var, LinExpr ,PsdExpr]
            The expression in the constraint. Can be a Var or a LinExpr, or a PsdExpr.

        lower: Number = None
            The lower bound for `expr`. It can only be a number or None. None indicates negative
            infinity.

        upper: Number = None
            The upper bound for `expr`. It can only be a number or None. None indicates positive
            infinity.

        name: str = ''
            The name of the constraint.

        Examples
        --------
        >>> m.addRange(x * 2 + y * 3, 1, 10)
        >>> m.addRange(mat1 * px1, 0, 1)

        '''

    def addSOS(self, type: int, vars: list, wts: list = None) -> SOS:
        '''
        Add a new SOS constraint to the model.

        Parameters
        ----------
        type: int
            Type for the new SOS constraint. Valid types include:
                * MDO.SOS_TYPE1
                * MDO.SOS_TYPE2

        vars: list
            The list of variables associated with the new SOS constraint.

        wts: list = None
            The list of weights for each participating variable. Default value: [1, 2, ...]

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVars(3)
        >>> m.addSOS(MDO.SOS_TYPE1, list(x.values()))

        '''

    def addVar(self, lb: float = 0, ub: float = float('inf'), obj: float = 0, vtype: str = 'C', name: str = '', column: Column = None) -> Var:
        '''
        Add a variable.

        Parameters
        ----------
        lb: float = 0
            Variable lower bound.

        ub: float = float('inf')
            Variable upper bound.

        obj: float = 0
            Coefficient of variable in objective function.

        vtype: str = 'C'
            The type of variable includes:
                * MDO.CONTINUOUS('C') for continuous variable
                * MDO.BINARY('B') for binary variable
                * MDO.INTEGER('I') for integral variable
                * MDO.SEMICONT('S') for semi-continuous variable
                * and MDO.SEMIINT('N') for semi-integral variable

        name: str = ''
            The name of the variable.

        column: Column = None
            Set the coefficient of a variable in an existing constraint.

        Examples
        --------
        >>> m.addVar()
        >>> m.addVar(vtype=MDO.INTEGER)
        >>> m.addVar(name='x')

        '''

    def addVars(self, *indices: Union[int, Iterable[int]], lb: Union[Number, list, np.ndarray] = 0.0, ub: Union[Number, list, np.ndarray] = float('inf'), obj: Union[Number, list, np.ndarray] = 0.0, vtype: Union[str, list, np.ndarray] = 'C', name: str = '') -> tupledict[Union[int, Iterable[int]], Var]:
        '''
        Add a set of variables. Return a tupledict with key as the index and value as the
        variable.

        Parameters
        ----------
        *indices: Union[int, Iterable[int]]
            Index of variables

        lb: Union[Number, list, np.ndarray] = 0.0
            The lower bound of all variables, which can be a single number, array, or
            numpy.ndarray. If it is numpy.ndarray, its shape must be equal to `indices`

        ub: Union[Number, list, np.ndarray] = float('inf')
            The upper bound of all variables, which can be a single number, array, or
            numpy.ndarray. If it is numpy.ndarray, its shape must be equal to `indices`

        obj: Union[Number, list, np.ndarray] = 0.0
            The coefficients of all variables in the objective function, which can be a single
            number, array, or numpy.ndarray. If it is numpy.ndarray, its shape must be equal
            to `indices`

        vtype: Union[str, list, np.ndarray] = 'C'
            The type of all variables, which can be a single character, array, or numpy.ndarray.
            If it is numpy.ndarray, its shape must be equal to `indices`
            The type of variable includes:
                * MDO.CONTINUOUS('C') for continuous variable
                * MDO.BINARY('B') for binary variable
                * MDO.INTEGER('I') for integral variable
                * MDO.SEMICONT('S') for semi-continuous variable
                * and MDO.SEMIINT('N') for semi-integral variable

        name: str = ''
            The names of all variables. If it is not None or '', the variable name is `name`,
            plus a subscript as its suffix.

        Examples
        --------
        >>> m.addVars(2, 2)
        >>> m.addVars(2, 2, lb=0)
        >>> m.addVars(2, 2, lb=[1, 2, 3, 4])
        >>> m.addVars(2, 2, lb=numpy.array([1, 2, 3, 4]).reshape(2,2))
        >>> td = m.addVars(2, 2)
        >>> linExpr = td.sum()

        '''

    def cbBranch(self, var: Union[int, Var], value: float, way: int) -> int:
        '''
        Indicate a new branching by specifying a variable and a split point between the
        lower and upper bounds of this variable.
        Method returns:
          * 0: Successful submission
          * 1: Submission is valid but incorrect (infeasible, etc)
          * 2: Submission is correct but not being accepted.

        Parameters
        ----------
        var: Union[int, Var]
            The variable.

        value: float
            The split point. It should be between the lower and upper bounds of the variable.

        way: int
            The branch to consider first. Valid options are:
                * <0: the down-way branch is considered first.
                * >0: the up-way branch is considered first.

        Notes
        -----
        Method can only be called within a callback function.
        '''

    def cbCut(self, lhs: Union[Var, LinExpr], sense: str, rhs: Union[Var, LinExpr]) -> int:
        '''
        Add a new cutting plane to the MIP model.
        Method returns:
          * 0: Successful submission
          * 1: Submission is valid but incorrect (infeasible, etc)
          * 2: Submission is correct but not being accepted.

        Parameters
        ----------
        lhs: Union[Var, LinExpr]
            Left-hand-side value for the new cutting plane. Can be `Var` or `LinExpr`.

        sense: str
            Sense for the new cutting plane (e.g., <=, >=, ==).

        rhs: Union[Var, LinExpr]
            Right-hand-side value for the new cutting plane. Can be `Var` or `LinExpr`.

        Notes
        -----
        This method can only be called within a callback function.
        '''

    def cbGet(self, what: int) -> Any:
        '''
        Retrieve additional data about the optimization progress.

        Parameters
        ----------
        what: int
            The data ID requested by the user callback.

        Notes
        -----
        Method can only be called within a callback function.
        '''

    def cbGetNodeRel(self, vars: Union[Var, list]) -> Any:
        '''
        Retrieve solution values of the current relaxed problem.

        Parameters
        ----------
        vars: Union[Var, list]
            Var object or a list of Var objects to indicate variables for which to retrieve
            solution values.

        Notes
        -----
        This method can only be called within a callback function.
        '''

    def cbGetSolution(self, vars: Union[Var, list]) -> Any:
        '''
        Retrieve values of the best solution so far.

        Parameters
        ----------
        vars: Union[Var, list]
            Var object or a list of Var objects to indicate variables to retrieve their solution
            values.

        Notes
        -----
        This method can only be called within a callback function.
        '''

    def cbSetSolution(self, vars: Union[Var, list], sol: Union[float, list]) -> None:
        '''
        Provide a new feasible solution for a MIP model. The objective value corresponding
        to the new solution will be returned if it is feasible.

        Parameters
        ----------
        vars: Union[Var, list]
            A Var or list of Var objects to indicate the variable(s) for which solution values
            are provided.

        sol: Union[float, list]
            A double value or list of double values to indicate the new feasible solution
            value(s) to be provided.

        Notes
        -----
        This method can only be called within a callback function.
        '''

    def cbUseSolution(self) -> tuple[int, float]:
        '''
        If you have already provided a solution using `cbSetSolution`, you can optionally
        call this method to immediately submit the solution to the MIP solver.
        The method returns a tuple of 2 elements: status and objective value.
        Status can be:
          * 0: Successful submission
          * 1: Submission is valid but incorrect (infeasible, etc)
          * 2: Submission is correct but not accepted.

        Notes
        -----
        This method can only be called within a callback function.
        '''

    def chgCoeff(self, constr: Constr, var: Var, newvalue: float) -> None:
        '''
        Modify a coefficient value in the constraint matrix.

        Parameters
        ----------
        constr: Constr
            The corresponding constraint.

        var: Var
            The corresponding variable.

        newvalue: float
            The new coefficient value.

        Examples
        --------
        >>> coeff = m.getCoeff(constr, var)
        >>> m.chgCoeff(constr, var, coeff + 1)

        '''

    def computeIIS(self, callback: Callable[..., Any] = None) -> None:
        '''
        Compute an IIS(Irreducible Inconsistent Subsystem). IIS is a subset of variable
        bounds and constraint bounds, this subset satisfies:
          1. The subproblem corresponding to the subset is still infeasible.
          2. After delete any bound in this subset, the subproblem becomes feasible.
        Check IIS related attributes for variable and constraint for more details.

        Parameters
        ----------
        callback: Callable[..., Any] = None
            Set up a user defined callback function.

        Notes
        -----
        The cardinality of the subsystem is supposed to be small. Note that the problem
        is expected to be infeasible.
        '''

    def copy(self) -> Model:
        '''
        Return a copy of a Model.

        Examples
        --------
        >>> another = model.copy()

        Notes
        -----
        Copying a Model will consume more memory resources.
        '''

    def dispose(self) -> None:
        '''
        Release the resources associated with the Model.

        Examples
        --------
        >>> model.dispose()

        '''

    def getA(self) -> sp._csr.csr_matrix:
        '''
        Obtain the constraint matrix. A sparse matrix in the `scipy.sparse` package is
        returned.

        Examples
        --------
        >>> m.getA()

        '''

    def getAttr(self, attrname: str, objs: list[Union[Var, Constr]] = None) -> list[Union[int, float, str]]:
        '''
        Obtain the value of an attribute.

        Parameters
        ----------
        attrname: str
            The name of the attribute.

        objs: list[Union[Var, Constr]] = None
            The list of variables or constraints, which indicates a variable attribute or
            constraint attribute should be retrieved. If the value is None, a Model attribute
            will be returned.

        Examples
        --------
        >>> v = m.addMVar((3,))
        >>> print(m.getAttr("ModelName"))
        >>> print(m.modelname)
        >>> print(m.getAttr("VarName", v.tolist()))
        >>> print(v.varname)

        Notes
        -----
        Attribute can also be read and written directly through object attributes, in this
        case, the attribute name is case-insensitive.
        '''

    def getCoeff(self, constr: Constr, var: Var) -> float:
        '''
        Obtain a coefficient value in the constraint matrix.

        Parameters
        ----------
        constr: Constr
            Corresponding constraint

        var: Var
            Corresponding variable

        Examples
        --------
        >>> coeff = m.getCoeff(constr, var)
        >>> m.chgCoeff(constr, var, coeff + 1)

        '''

    def getCol(self, var: Var) -> Column:
        '''
        Obtain the column corresponding to a variable.

        Parameters
        ----------
        var: Var
            Corresponding variable

        Examples
        --------
        >>> column = m.getCol(x)

        '''

    def getConstrByName(self, name: str) -> Constr:
        '''
        Obtain the constraint object by its name.

        Parameters
        ----------
        name: str
            The name of the constraint.

        Examples
        --------
        >>> c.constrname = 'myconstr'
        >>> print(c.sameAs(m.getConstrByName('myconstr')))

        '''

    def getConstrs(self) -> list[Constr]:
        '''
        Obtain a list of all constraints in the Model.

        Examples
        --------
        >>> m.getConstrs()

        '''

    def getGenConstrIndicator(self, genconstr: GenConstr) -> tuple[Var, bool, LinExpr, str, float]:
        '''
        Retrieve an indicator constraint from model by its object.
        A tuple with 5 elements will be returned:
          1. Binary variable of this indicator constraint.
          2. Binary value when indicator constraint takes effect.
          3. Linear expression of this indicator constraint.
          4. Constraint sense of this indicator constraint.
          5. Right-hand-side value of this indicator constraint.

        Parameters
        ----------
        genconstr: GenConstr
            The indicator constraint object.

        '''

    def getGenConstrs(self) -> list[GenConstr]:
        '''
        Retrieve all general constraints in this model.

        '''

    def getObjective(self) -> Union[LinExpr, QuadExpr, PsdExpr]:
        '''
        Get the expression of the objective function.

        Examples
        --------
        >>> expr = m.getObjective()

        '''

    def getParamInfo(self, paramname: str) -> tuple[str, Type, Union[int, float, str], Union[int, float, str], Union[int, float, str], Union[int, float, str]]:
        '''
        You can call this method to obtain information about a parameter. It returns a
        tuple containing six elements:
            1. The name of the parameter.
            2. Type of the parameter.
            3. The current value of the parameter.
            4. The minimum allowed value of the parameter. For string type parameters, this
               field is always an empty string ('').
            5. The maximum allowed value of the parameter. For string type parameters, this
               field is always an empty string ('').
            6. Default value of the parameter.

        Parameters
        ----------
        paramname: str
            The name of the parameter.

        Examples
        --------
        >>> pname, ptype, pval, pmin, pmax, pdef = m.getParamInfo('MaxTime')

        Notes
        -----
        Parameter names may contain '*' and '?' wildcard characters. When more than one
        parameter name is matched, all matching parameters are printed.
        '''

    def getPsdConstrs(self) -> list[PsdConstr]:
        '''
        Obtain a list of all PsdConstrs in the Model.

        Examples
        --------
        >>> m.getPsdConstrs()

        '''

    def getPsdVars(self) -> list[PsdVar]:
        '''
        Obtain a list of all PsdVars in the Model.

        Examples
        --------
        >>> m.getPsdVars()

        '''

    def getQCRow(self, qconstr: QConstr) -> QuadExpr:
        '''
        Get the expression of the quadratic constraint.

        Parameters
        ----------
        qconstr: QConstr
            Corresponding quadratic constraints.

        '''

    def getQConstrByName(self, name: str) -> QConstr:
        '''
        Obtain the quadratic constraint object by its name.

        Parameters
        ----------
        name: str
            The name of the quadratic constraint.

        '''

    def getQConstrs(self) -> list[QConstr]:
        '''
        Obtain a list of all quadratic constraints in the model.

        '''

    def getRow(self, constr: Constr) -> LinExpr:
        '''
        Get the expression of the constraint.

        Parameters
        ----------
        constr: Constr
            Corresponding constraint

        Examples
        --------
        >>> m.getRow(c)

        '''

    def getSOS(self, sos: SOS) -> tuple[int, list[Var], list[float]]:
        '''
        Retrieve information about an SOS constraint.
        This method returns a triple:
            1. An integer indicating the SOS type.
            2. A list of participating variables.
            3. A list of weights for each participating variable.

        Parameters
        ----------
        sos: SOS
            The SOS constraint to retrieve information about.

        Examples
        --------
        >>> m = Model()
        >>> m.addVars(3)
        >>> sos = m.addSOS(MDO.SOS_TYPE1, m.getVars())
        >>> type, vars, wts = m.getSOS(sos)

        '''

    def getSOSs(self) -> list[SOS]:
        '''
        Retrieve all SOS constraints in model.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVars()
        >>> m.addSOS(MDO.SOS_TYPE1, list(x.values()))
        >>> print(m.getSOSs())

        '''

    def getVarByName(self, name: str) -> Var:
        '''
        Obtain a variable object by its name.

        Parameters
        ----------
        name: str
            The name of the variable.

        Examples
        --------
        >>> v.varname = 'myvar'
        >>> print(v.sameAs(m.getVarByName('myvar')))

        '''

    def getVars(self) -> list[Var]:
        '''
        Obtain a list of all variables in the model.

        Examples
        --------
        >>> m.getVars()

        '''

    def message(self, message: str) -> None:
        '''
        Print a string into log

        Parameters
        ----------
        message: str
            The string to be printed.

        Examples
        --------
        >>> m.message("Start to optimize")
        >>> m.optimize()
        >>> m.message("OK")

        '''

    def optimize(self, callback: Callable[..., Any] = None) -> None:
        '''
        Start model optimization. It may take some time, depends on the complexity of the
        problem.

        Parameters
        ----------
        callback: Callable[..., Any] = None
            Set up a user-defined callback function.
            A user-defined function takes two arguments, `model` and `where`. The `model`
            argument can be used for context passing:
            def callback(model, where):
                model._calls += 1

            model = read("prob.mps")
            model._calls = 0
            model.optimize(callback)
            print(model._calls)

            Note only member variable with name prefix "_" can be added to `model` for context
            passing.

        Examples
        --------
        >>> m.optimize()

        '''

    def read(self, filename: str) -> None:
        '''
        Read data from a file. The data type depends on the suffix of the file name.

        Parameters
        ----------
        filename: str
            The name of the file. The suffix implies the data type. For example, ".prm"
            indicates that it loads a parameter setting from the file. ".mst" indicates that
            it loads MIP starts from the file.

        Examples
        --------
        >>> m.read("trial1.prm")

        '''

    def remove(self, item: Union[Var, PsdVar, MVar, Constr, QConstr, PsdConstr, SOS, GenConstr, MConstr, MQConstr, list, tuple, dict]) -> None:
        '''
        Remove some variables or constraints from the model

        Parameters
        ----------
        item: Union[Var, PsdVar, MVar, Constr, QConstr, PsdConstr, SOS, GenConstr, MConstr, MQConstr, list, tuple, dict]
            The object to be deleted. Can be one of the following types:
                * Var, the variable to be deleted
                * PsdVar, the PSD variable to be deleted
                * MVar, the variable matrix to be deleted. All variables in the matrix will be
                  deleted from the Model
                * Constr, the constraint to be deleted
                * QConstr, the quadratic constraint to be deleted
                * PsdConstr, the PSD constraint to be deleted
                * SOS, the SOS constraint to be deleted
                * GenConstr, the general constraint to be deleted
                * MConstr, the constraint matrix to be deleted, all constraints in the matrix
                  will be removed from the model
                * MQConstr, the quadratic constraint matrix to be deleted, all quadratic
                  constraints in the matrix will be removed from the model
                * list or tuple, all the above objects in the collection will be deleted from
                  the Model
                * dict, all the above objects contained in all values will be deleted from the
                  Model, and all keys will be ignored.

        Examples
        --------
        >>> m.remove(x)
        >>> m.remove(c)
        >>> m.remove([x0, x1, x2])
        >>> m.remove({'x0': x0, 'x1': x1})

        '''

    def reset(self, clearall: int = 0) -> None:
        '''
        Set the model to the unsolved state and clear all data related to the solution.

        Parameters
        ----------
        clearall: int = 0
            When the value is 0, only the solution is cleared; when the value is 1, all relevant
            data is cleared.

        Examples
        --------
        >>> m.optimize()
        >>> m.reset(1)
        >>> m.optimize()

        '''

    def resetParams(self) -> None:
        '''
        Reset all parameters to their default values.

        Examples
        --------
        >>> m.resetParams()

        '''

    def setAttr(self, attrname, objs: Union[int, float, str, list[Union[Var, Constr]]], newvalues: list[Union[int, float, str]] = None) -> None:
        '''
        Set an attribute value.

        Parameters
        ----------
        attrname
            The name of the attribute.

        objs: Union[int, float, str, list[Union[Var, Constr]]]
            Can be a list of variables or constraints, indicating that an attribute value of
            a variable or constraint is being set. When newvalues is None, objs is used as
            the new attribute value.

        newvalues: list[Union[int, float, str]] = None
            An array containing new attribute values. The length of the array should match
            the length of objs.

        Examples
        --------
        >>> m.modelname = "DietProblem"
        >>> m.setAttr("ModelName", "DietProblem")
        >>> vars = m.addMVar((3,))
        >>> vars.varname = ["x0", "x1", "x2"]
        >>> name_list = ["x3", "x1", "x2"]
        >>> var_list = vars.tolist()
        >>> for i in range(len(var_list)):
        >>>     var_list[i].setAttr("VarName", name_list[i])

        Notes
        -----
        Attributes can also be read and written directly through object attributes. In
        this case, the attribute name is case-insensitive.
        '''

    def setObjective(self, expr: Union[LinExpr, QuadExpr, PsdExpr], sense: int = 0) -> None:
        '''
        Set the objective function.

        Parameters
        ----------
        expr: Union[LinExpr, QuadExpr, PsdExpr]
            The expression of the objective function.

        sense: int = 0
            The optimization sense of the objective function, including:
                * MDO.MINIMIZE (1) for minimization
                * MDO.MAXIMIZE (-1) for maximization
            Other values will not change the current optimization sense. The default optimization
            sense is MDO.MINIMIZE.

        Examples
        --------
        >>> m.setObjective(x + 2 * y, MDO.MINIMIZE)

        '''

    def setParam(self, paramname: str, paramvalue: Union[int, float, str]) -> None:
        '''
        Set the value of a parameter.

        Parameters
        ----------
        paramname: str
            The name of the parameter to be set.

        paramvalue: Union[int, float, str]
            Parameter value.

        Examples
        --------
        >>> m.setParam("MaxTime", 10)
        >>> m.setParam("MaxTi*", 10)
        >>> m.setParam("MaxTi*", "default")

        Notes
        -----
        1. Parameter names can contain '*' and '?' wildcards. If more than one parameter name
           is matched, the parameter value is not modified.
        2. When the parameter value is 'default', you can reset the parameter to its default
           value.
        '''

    def terminate(self) -> None:
        '''
        Send a stop request to the solver within a MIP callback function. Once the solver
        is terminated, an error code `ABORT_CTRL_C` will be returned from `Model.optimize`.

        Notes
        -----
        This method can only be called within a callback function.
        '''

    def write(self, filename: str) -> None:
        '''
        Write data of model to a file. The data type depends on the suffix of the file
        name.

        Parameters
        ----------
        filename: str
            The name of the file to be written. Valid suffixes include:
                * '.lp'
                * '.mps'
                * '.qps'
            These will write the model itself into a file. If the suffix is one of
                * '.sol'
                * '.bas'
                * '.prm'
                * '.mst'
            solution, basis, parameter settings, or MIP starts will be written to the file.
            In addition, after specifying a valid suffix, you can add another '.gz' or '.bz2'
            suffix to specify the compression format.

        Examples
        --------
        >>> m.write("prob.mps")
        >>> m.write("settings.prm.gz")

        '''

    ProbName: str = ...
    '''
    The problem name
    '''

    ModelName: str = ...
    '''
    Alias for ProbName. The problem name
    '''

    MinSense: str = ...
    '''
    If the objective function is min sense
    '''

    ModelSense: str = ...
    '''
    The objective function sense, 1 for min and -1 for max
    '''

    HasSolution: str = ...
    '''
    If the problem has a solution
    '''

    HasPrimalRay: str = ...
    '''
    If the problem has primal ray
    '''

    HasDualRay: str = ...
    '''
    If the problem has dual ray
    '''

    NumVars: str = ...
    '''
    The total number of variables
    '''

    NumConss: str = ...
    '''
    The total number of constraints
    '''

    NumConstrs: str = ...
    '''
    Alias for NumConss. The total number of constraints.
    '''

    NumSOS: str = ...
    '''
    The total number of Special Ordered Set (SOS) constraints in the model
    '''

    NumEnts: str = ...
    '''
    The total number of constraint matrix non-zeros
    '''

    NumNZs: str = ...
    '''
    Alias for NumEnts. The total number of constraint matrix non-zeros
    '''

    SPX_NumIters: str = ...
    '''
    The total number of iterations after a simplex method completed.
    '''

    IPM_NumIters: str = ...
    '''
    The total number of iterations after an interior point method has completed.
    '''

    Status: str = ...
    '''
    The optimization status after model optimized.
    '''

    NumPsdVars: str = ...
    '''
    The total number of PSD variables.
    '''

    NumPsdConstrs: str = ...
    '''
    The total number of PSD constraints
    '''

    ObjConst: str = ...
    '''
    The constant component of the objective function.
    '''

    ObjCon: str = ...
    '''
    Alias for ObjConst. The constant component of objective function
    '''

    PrimalObjVal: str = ...
    '''
    The objective value of the primal solution.
    '''

    ObjVal: str = ...
    '''
    Alias for PrimalObjVal. The objective value of primal solution
    '''

    DualObjVal: str = ...
    '''
    The objective value of the dual solution
    '''

    PresolverTime: str = ...
    '''
    Presolver execution time in seconds
    '''

    SolverTime: str = ...
    '''
    Solver execution time in seconds
    '''

    SolutionTime: str = ...
    '''
    Total execution time in seconds
    '''

    MIP_GapAbs: str = ...
    '''
    The absolute gap for a MIP solution. If the user wants to set the maximum tolerable
    gap before optimization, see parameter `MIP/GapAbs`.
    '''

    MIP_GapRel: str = ...
    '''
    The relative gap for a MIP solution. If the user wants to set the maximum tolerable
    gap before optimization, see parameter `MIP/GapRel`.
    '''

    Param: ParamConstClass = ...

    param: ParamConstClass = ...

class PsdConstr:

    def getAttr(self, attrname: str) -> Union[int, float, str]:
        '''
        Obtain the attribute value corresponding to a PsdConstr.

        Parameters
        ----------
        attrname: str
            Attribute name

        Examples
        --------
        >>> m = Model()
        >>> x = m.addPsdVar(dim = 2)
        >>> c = m.addConstr(x * numpy.identity(2) == 2, name="c0")
        >>> print(c.psdcname == "c0")
        >>> print(c.getAttr(MDO.Attr.PsdCName) == "c0")

        Notes
        -----
        Attributes can also be read and written directly through object attributes; in
        this case, the attribute name is case-insensitive.
        '''

    index: int = ...
    '''
    Index position of PsdConstr
    '''

    def sameAs(self, constr: PsdConstr) -> bool:
        '''
        Test whether the PsdConstr and another PsdConstr are the same.

        Parameters
        ----------
        constr: PsdConstr
            Another PsdConstr to be tested.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addPsdVar(dim = 2)
        >>> c = m.addConstr(x * numpy.identity(2) == 2)
        >>> print(c.sameAs(m.getPsdConstrs()[0]))

        '''

    def setAttr(self, attrname: str, attrvalue: Union[int, float, str]) -> None:
        '''
        Set the attribute value corresponding to the PsdConstr.

        Parameters
        ----------
        attrname: str
            The name of the attribute.

        attrvalue: Union[int, float, str]
            The value of the attribute to be set.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addPsdVar(dim = 2)
        >>> c = m.addConstr(x * numpy.identity(2) == 2, name = "x0")
        >>> c.setAttr(MDO.Attr.PsdCName, "c0")
        >>> print(c.psdcname)
        >>> c.psdcname = "c1"
        >>> print(c.psdcname)

        Notes
        -----
        Attributes can also be read and written directly through object attributes; in
        this case, the attribute name is case-insensitive.
        '''

    PsdCName: str = ...
    '''
    The PSD constraint name
    '''

    PsdCLHS: str = ...
    '''
    psd constraint left-hand-side value
    '''

    PsdCRHS: str = ...
    '''
    PSD constraint right-hand-side value
    '''

class PsdExpr:

    def __init__(self, arg1: Union[Number, Var, LinExpr, PsdExpr] = 0, arg2: Union[Var, PsdVar, tuple, list, np.ndarray] = None) -> None:
        '''
        Construct a semi-definite expression.

        Parameters
        ----------
        arg1: Union[Number, Var, LinExpr, PsdExpr] = 0
            The initial value of a PsdExpr, which can be a constant, a Var, a LinExpr, or
            another PsdExpr.

        arg2: Union[Var, PsdVar, tuple, list, np.ndarray] = None
            When it is not None, it is usually a Var or PsdVar, or a list of variables.

        Examples
        --------
        >>> PsdExpr([mat], [psdx])
        >>> PsdExpr(mat, psdx)
        >>> PsdExpr(coeff, x)
        >>> PsdExpr(x)
        >>> PsdExpr(mat * psdx)
        >>> PsdExpr(2 * x + 1)
        >>> PsdExpr([(mat1, px1), (mat2, px2), (mat3, px3)])
        >>> PsdExpr([(1, x), (2, y), (1, z)])
        >>> PsdExpr(1)

        '''

    def add(self, expr: PsdExpr, mult: float = 1.0) -> None:
        '''
        Add all terms of another PsdExpr to the current PsdExpr.

        Parameters
        ----------
        expr: PsdExpr
            Another PsdExpr.

        mult: float = 1.0
            Multiplier. Default value: 1.0.

        Examples
        --------
        >>> psdExpr.add(psdExpr1, -1)

        '''

    def addConstant(self, c: float) -> None:
        '''
        Add a value to the constant term of the PsdExpr.

        Parameters
        ----------
        c: float
            The value to be added. A negative number indicates that a value is subtracted.

        Examples
        --------
        >>> psdExpr.addConstant(-psdExpr.getConstant())

        '''

    def addTerms(self, coeffs: Union[Number, np.ndarray, Sequence[Number]], vars: Union[Var, np.ndarray, PsdVar, Sequence[Var]]) -> None:
        '''
        Add one or more terms. When plain variables and numeric coefficients are provided,
        linear terms are added. When PsdVar and matrices are provided, a semi-definite
        term is added.

        Parameters
        ----------
        coeffs: Union[Number, np.ndarray, Sequence[Number]]
            The coefficient of the term(s) to be added, which may be a single number, a single
            matrix, or a list.

        vars: Union[Var, np.ndarray, PsdVar, Sequence[Var]]
            The variable of the term(s) to be added, which can be a single Var, a PsdVar, or
            a list.

        Examples
        --------
        >>> psdExpr.addTerms([1, 2], [x, y])
        >>> psdExpr.addTerms([mat1, mat2], [px1, px2])
        >>> psdExpr.addTerms(1, x)
        >>> psdExpr.addTerms(mat, px)

        '''

    def clear(self) -> None:
        '''
        Clear all included terms and set constant to 0

        Examples
        --------
        >>> psdExpr = mat1 * px1 + 3 * x + 1
        >>> psdExpr.clear()
        >>> print(psdExpr.size() == 0)
        >>> print(psdExpr.getLinExpr().size() == 0)
        >>> print(psdExpr.getConstant() == 0)

        '''

    def getCoeff(self, index: int) -> np.ndarray:
        '''
        Obtain the coefficient of a semi-definite term in a PsdExpr.

        Parameters
        ----------
        index: int
            To obtain the index of the semi-definite term's coefficient.

        Examples
        --------
        >>> psdExpr = mat1 * px1 + mat2 * px2
        >>> print(psdExpr.getCoeff(0) == mat1)

        '''

    def getConstant(self) -> float:
        '''
        Obtain the constant term of a PsdExpr.

        Examples
        --------
        >>> psdExpr.addConstant(-psdExpr.getConstant())

        '''

    def getLinExpr(self) -> LinExpr:
        '''
        Get a linear expression contained in a PsdExpr.

        Examples
        --------
        >>> psdExpr = mat * px + 1 * x + 3 * y + 1
        >>> print(psdExpr.getLinExpr().size() == 2)
        >>> print(psdExpr.getLinExpr().getConstant() == 1)

        '''

    def getValue(self) -> float:
        '''
        After solving the problem, obtain the value of the PsdExpr.

        Examples
        --------
        >>> m.optimize()
        >>> psdExpr = mat1 * px1 + mat2 * px2 + 1 * x + 2
        >>> print(psdExpr.getValue())

        '''

    def getVar(self, index: int) -> PsdVar:
        '''
        Obtain the PsdVar of a term in a PsdExpr.

        Parameters
        ----------
        index: int
            To obtain the index of the term of the PsdVar.

        Examples
        --------
        >>> psdExpr = mat1 * px1 + mat2 * px2
        >>> print(psdExpr.getVar(1).sameAs(px2))

        '''

    def remove(self, item: Union[int, PsdVar]) -> None:
        '''
        Delete specific terms from a PsdExpr.

        Parameters
        ----------
        item: Union[int, PsdVar]
            If item is an integer, the semi-definite term at the specified index is removed.
            If item is a Var, all linear terms containing this Var are removed. If item is a
            PsdVar, all semi-definite terms containing this PsdVar are removed.

        Examples
        --------
        >>> psdExpr = mat1 * px1 + mat2 * px2 + 3 * y + 4 * x
        >>> psdExpr.remove(0)
        >>> psdExpr.remove(px2)
        >>> print(psdExpr.size() == 0)
        >>> psdExpr.remove(x)
        >>> psdExpr.remove(y)
        >>> print(psdExpr.getLinExpr().size() == 0)

        '''

    def size(self) -> int:
        '''
        Obtain the number of semi-definite terms, excluding linear terms and constant
        terms.

        Examples
        --------
        >>> psdExpr = mat1 * px1 + 3 * x + 1
        >>> print(psdExpr.size() == 1)

        '''

class PsdVar:

    def getAttr(self, attrname: str) -> Union[int, str, np.ndarray]:
        '''
        Obtain the attribute value of a PSD variable.

        Parameters
        ----------
        attrname: str
            Attribute name

        Examples
        --------
        >>> m = Model()
        >>> x = m.addPsdVar(dim = 1)
        >>> print(x.dim)
        >>> print(x.getAttr(MDO.Attr.Dim))

        Notes
        -----
        Attributes can also be read and written directly through object attributes; in
        this case, the attribute name is case-insensitive.
        '''

    index: int = ...
    '''
    The index position of the PSD variable.
    '''

    def sameAs(self, var: PsdVar) -> bool:
        '''
        Test whether the PSD variable is the same as another PSD variable.

        Parameters
        ----------
        var: PsdVar
            Another PSD variable to be tested

        Examples
        --------
        >>> m = Model()
        >>> x = m.addPsdVar(dim=1)
        >>> print(x.sameAs(m.getPsdVars()[0]))

        '''

    def setAttr(self, attrname: str, attrvalue: Union[int, str, np.ndarray]) -> None:
        '''
        Set the attribute value of a PSD variable.

        Parameters
        ----------
        attrname: str
            The name of the attribute.

        attrvalue: Union[int, str, np.ndarray]
            The value of the attribute to be set.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addPsdVar(dim = 1)
        >>> x.setAttr(MDO.Attr.PsdVarName, "x0")
        >>> print(x.psdvarname == "x0")

        Notes
        -----
        Attributes can also be read and written directly through object attributes; in
        this case, the attribute name is case-insensitive.
        '''

    PsdVarName: str = ...
    '''
    The PSD variable name
    '''

    Dim: str = ...
    '''
    The dimension of a PSD variable
    '''

    PsdX: str = ...
    '''
    The solution of the PSD variable in the primal problem.
    '''

    PsdObj: str = ...
    '''
    The objective coefficient of a PSD variable.
    '''

class QConstr:

    def getAttr(self, attrname: str) -> Union[int, float, str]:
        '''
        Obtain the attribute value associated with the quadratic constraint.

        Parameters
        ----------
        attrname: str
            Attribute name

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVar()
        >>> qc = m.addConstr(2 * x * x <= 1)
        >>> print(qc.qcrhs)
        >>> print(qc.getAttr(MDO.Attr.QCRHS))

        Notes
        -----
        Attribute can also be read and written directly through object attributes; in this
        case, the attribute name is case-insensitive.
        '''

    index: int = ...
    '''
    The index of the quadratic constraint.
    '''

    def sameAs(self, qconstr: QConstr) -> bool:
        '''
        Test whether the quadratic constraint is the same as another quadratic constraint.

        Parameters
        ----------
        qconstr: QConstr
            Another quadratic constraint to be tested.

        '''

    def setAttr(self, attrname: str, attrvalue: Union[int, float, str]) -> None:
        '''
        Set the attribute value associated with the quadratic constraint.

        Parameters
        ----------
        attrname: str
            The name of the attribute.

        attrvalue: Union[int, float, str]
            The value of the attribute to be set.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVar()
        >>> qc = m.addConstr(2 * x * x <= 1)
        >>> qc.qcrhs = 2.0
        >>> qc.setAttr(MDO.Attr.QCRHS, 2.0)

        Notes
        -----
        Attributes can also be read and written directly through object attributes; in
        this case, the attribute name is case-insensitive.
        '''

class QuadExpr:

    def __init__(self, expr: Union[Number, Var, LinExpr, QuadExpr] = None) -> None:
        '''
        Construct a quadratic expression

        Parameters
        ----------
        expr: Union[Number, Var, LinExpr, QuadExpr] = None
            The initial value of a quadratic expression, which can be a constant, a variable,
            a linear expression, or another quadratic expression.

        Examples
        --------
        >>> QuadExpr()
        >>> QuadExpr(1)
        >>> QuadExpr(x)
        >>> QuadExpr(2 * x + y)
        >>> QuadExpr(2 * x * x)

        '''

    def add(self, expr: Union[LinExpr, QuadExpr], mult: float = 1.0) -> None:
        '''
        Add all terms of another expression to the current quadratic expression.

        Parameters
        ----------
        expr: Union[LinExpr, QuadExpr]
            Another expression.

        mult: float = 1.0
            Multiplier. Default value: 1.0.

        Examples
        --------
        >>> quadExpr.add(linExpr, -1)
        >>> quadExpr.add(quadExpr1, -1)

        '''

    def addConstant(self, c: float) -> None:
        '''
        Add a value to the constant term of the quadratic expression.

        Parameters
        ----------
        c: float
            The value to be added. A negative number indicates that this value should be
            subtracted.

        Examples
        --------
        >>> quadExpr.addConstant(-quadExpr.getConstant())

        '''

    def addTerms(self, coeffs: Union[Number, Sequence[Number]], vars: Union[Var, Sequence[Var]], vars2: Union[Var, Sequence[Var]] = None) -> None:
        '''
        Add one or more term(s).

        Parameters
        ----------
        coeffs: Union[Number, Sequence[Number]]
            The coefficient of the term(s) to be added, which may be a number or an array.

        vars: Union[Var, Sequence[Var]]
            The variable of the term(s) to be added, which can be a single variable or an
            array.

        vars2: Union[Var, Sequence[Var]] = None
            If it is not None, it indicates the second variable of the quadratic term, which
            can be a single variable or an array.

        Examples
        --------
        >>> quadExpr.addTerms([1, 2], [x, y])
        >>> quadExpr.addTerms(1, x)
        >>> quadExpr.addTerms(1, x, y)

        '''

    def clear(self) -> None:
        '''
        Clear all included terms and set the constant to 0

        Examples
        --------
        >>> quadExpr = 2 * x * x +3 * y +1
        >>> quadExpr.clear()
        >>> print(quadExpr.size() == 0)
        >>> print(quadExpr.getLinExpr().size() == 0)
        >>> print(quadExpr.getConstant() == 0)

        '''

    def copy(self) -> QuadExpr:
        '''
        Return a copy of a quadratic expression.

        Examples
        --------
        >>> another = quadExpr.copy()

        '''

    def getCoeff(self, index: int) -> float:
        '''
        Obtain the coefficient of a quadratic term from expression.

        Parameters
        ----------
        index: int
            The index of the term.

        Examples
        --------
        >>> quadExpr = 2 * x + 1 * y + 3 * z * z
        >>> print(quadExpr.getCoeff(0) == 2)

        '''

    def getConstant(self) -> float:
        '''
        Obtain the constant term of a quadratic expression.

        Examples
        --------
        >>> quadExpr.addConstant(-quadExpr.getConstant())

        '''

    def getLinExpr(self) -> LinExpr:
        '''
        Get a linear expression contained in a quadratic expression

        Examples
        --------
        >>> quadExpr = 2 * x * x + 3 * y + 1
        >>> print(quadExpr.getLinExpr().size() == 1)
        >>> print(quadExpr.getLinExpr().getConstant() == 1)

        '''

    def getValue(self) -> float:
        '''
        After solving the problem, obtain the value of the quadratic expression

        Examples
        --------
        >>> m.optimize()
        >>> quadExpr = 2 * x * x + y
        >>> print(quadExpr.getValue())

        '''

    def getVar1(self, index: int) -> Var:
        '''
        Get the first variable of a quadratic term in a quadratic expression.

        Parameters
        ----------
        index: int
            index of quadratic term in expression

        Examples
        --------
        >>> quadExpr = 2 * x + 1 * y + 3 * x * y
        >>> print(quadExpr.getVar1(0).sameAs(x))

        '''

    def getVar2(self, index: int) -> Var:
        '''
        Get the second variable of a quadratic term in a quadratic expression.

        Parameters
        ----------
        index: int
            index of quadratic term in expression

        Examples
        --------
        >>> quadExpr = 2 * x + 1 * y + 3 * x * y
        >>> print(quadExpr.getVar2(0).sameAs(y))

        '''

    def remove(self, item: Union[int, Var]) -> None:
        '''
        Delete terms from an expression based on specified criteria.

        Parameters
        ----------
        item: Union[int, Var]
            If `item` is a number, the term at the index `item` is removed. If `item` is a
            variable, all terms containing this variable, including quadratic and linear terms,
            are deleted.

        Examples
        --------
        >>> quadExpr = 2 * x * x +3 * y + 4 * x
        >>> quadExpr.remove(1)
        >>> quadExpr.remove(x)
        >>> print(quadExpr.size() == 0)
        >>> print(quadExpr.getLinExpr().size() == 0)

        '''

    def size(self) -> int:
        '''
        Obtain the number of quadratic terms, excluding linear terms and constant terms.

        Examples
        --------
        >>> quadExpr = 2 * x * x + 3 * y + 1
        >>> print(quadExpr.size() == 1)

        '''

class SOS:

    def getAttr(self, attrname: str) -> Union[int, float, str]:
        '''
        Obtain the attribute value of SOS constraint.

        Parameters
        ----------
        attrname: str
            Attribute name

        Notes
        -----
        Attribute can also be read and written directly through object attributes, in this
        case, the attribute name is case-insensitive
        '''

    index: int = ...
    '''
    The index position of the SOS constraint.
    '''

    def sameAs(self, sos: SOS) -> bool:
        '''
        Test whether the SOS constraint is the same as another SOS constraint.

        Parameters
        ----------
        sos: SOS
            Another SOS constraint to be tested.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVar()
        >>> y = m.addVar()
        >>> sos = m.addSOS(MDO.SOS_TYPE1, [x, y])
        >>> print(sos.sameAs(m.getSOSs()[0]))

        '''

    def setAttr(self, attrname: str, attrvalue: Union[int, float, str]) -> None:
        '''
        Set the attribute value of SOS constraint.

        Parameters
        ----------
        attrname: str
            The name of the attribute.

        attrvalue: Union[int, float, str]
            The value of the attribute to be set.

        Notes
        -----
        Attribute can also be read and written directly through object attributes, in this
        case, the attribute name is case-insensitive.
        '''

class TempConstr:

    def getExpr(self) -> Union[LinExpr, QuadExpr, MLinExpr, MQuadExpr, PsdExpr]:
        '''
        Get a expression part of constraint

        '''

    def getLhs(self) -> float:
        '''
        Gets the lower bound of a constraint

        '''

    def getRhs(self) -> float:
        '''
        Gets the upper bound of a constraint

        '''

class Var:

    def getAttr(self, attrname: str) -> Union[int, float, str]:
        '''
        Get the attribute value of a variable

        Parameters
        ----------
        attrname: str
            Attribute name

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVar()
        >>> print(x.varname)
        >>> print(x.getAttr(MDO.Attr.VarName))

        Notes
        -----
        Attribute can also be read and written directly through object attributes; in this
        case, the attribute name is case-insensitive
        '''

    index: int = ...
    '''
    The index position of the variable.
    '''

    def sameAs(self, var: Var) -> bool:
        '''
        Test whether the variable is the same as another variable.

        Parameters
        ----------
        var: Var
            Another variable to be tested.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVar()
        >>> print(x.sameAs(m.getVars()[0]))

        '''

    def setAttr(self, attrname: str, attrvalue: Union[int, float, str]) -> None:
        '''
        Set the attribute value of a variable.

        Parameters
        ----------
        attrname: str
            The name of the attribute.

        attrvalue: Union[int, float, str]
            The value of the attribute to be set.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVar()
        >>> x.ub = 1.0
        >>> x.setAttr(MDO.Attr.UB, 2.0)
        >>> print(x.ub == 2.0)

        Notes
        -----
        Attribute can also be read and written directly through object attributes, in this
        case, the attribute name is case-insensitive
        '''

    ColName: str = ...
    '''
    The variable name
    '''

    VarName: str = ...
    '''
    Alias for ColName, The variable name
    '''

    IsInteger: str = ...
    '''
    If a variable is of integral type
    '''

    ColBasis: str = ...
    '''
    The basis of a column
    '''

    VType: str = ...
    '''
    The variable type
    '''

    LB: str = ...
    '''
    The lower bound of a variable
    '''

    UB: str = ...
    '''
    The upper bound of a variable
    '''

    Obj: str = ...
    '''
    The objective coefficient of a variable
    '''

    ReducedCost: str = ...
    '''
    The reduced cost
    '''

    RC: str = ...
    '''
    Alias for ReducedCost. The reduced cost
    '''

    PrimalSoln: str = ...
    '''
    The solution of the primal problem
    '''

    X: str = ...
    '''
    Alias for PrimalSoln. The solution of the primal problem.
    '''

    Start: str = ...
    '''
    The current MIP start vector
    '''

def disposeDefaultEnv() -> None:
    '''
    Releases the resources associated with the default Environment.

    Notes
    -----
    When you need to use the default Environment again after you disposed of it, the
    Environment will be automatically recreated.
    '''

def models() -> list[Model]:
    '''
    Return all current instantiated models except those in the user's data structure.

    '''

def multidict(d: dict) -> tuple[tuplelist, tupledict]:
    '''
    Split a dictionary into multiple dictionaries.

    Parameters
    ----------
    d: dict
        Dictionary to be split.

    Examples
    --------
    >>> (keys, dict1, dict2) = multidict ({
    >>>     'keye': [1, 2],
    >>>     'key2': [1, 3],
    >>>     'key3': [1, 4]})

    '''

def paramHelp(paramname: str) -> None:
    '''
    Get help documentation for Mindopt parameters

    Parameters
    ----------
    paramname: str
        The name of the parameter for help

    Examples
    --------
    >>> paramHelp()
    >>> paramHelp("MaxTime")
    >>> paramHelp("IPM*")

    Notes
    -----
    Argument `paramname` can contain '*' and '?' wildcard characters
    '''

def quicksum(li: list[Union[LinExpr, QuadExpr]]) -> Union[LinExpr, QuadExpr]:
    '''
    Quickly sum to get an expression.

    Parameters
    ----------
    li: list[Union[LinExpr, QuadExpr]]
        List of terms.

    Examples
    --------
    >>> m = Model()
    >>> x = m.addVar()
    >>> y = m.addVar()
    >>> linExpr = quicksum([1 * x, 2 * y])
    >>> quadExpr = quicksum([1 * x * x, 2 * x * y])

    '''

def read(filename: str, env: Optional[Env] = None) -> Model:
    '''
    Read a model from a file

    Parameters
    ----------
    filename: str
        The file name that contains the model. The format of the model is determined by
        the suffix of the file name, such as '.mps', '.lp', '.qps', '.dat-s'. If the file
        is compressed, the filename must include a suffix to indicate its compression
        type, such as '.gz', '.bz2'.

    env: Optional[Env] = None
        Optional. Set this if you want to use a custom Environment.

    '''

def readParams(filename: str) -> None:
    '''
    Read parameter settings from a file.

    Parameters
    ----------
    filename: str
        The file name of the parameter settings; valid suffix is '.prm'.

    Examples
    --------
    >>> readParams("settings.prm")

    Notes
    -----
    This modification applies to all models that can be returned from models().
    '''

def resetParams() -> None:
    '''
    Set all parameters to their default values.

    Examples
    --------
    >>> resetParams()

    Notes
    -----
    This modification applies to all models that can be returned from models().
    '''

def setParam(paramname: str, paramvalue: Union[int, float, str]) -> None:
    '''
    Set the value of a parameter.

    Parameters
    ----------
    paramname: str
        The name of the parameter to be set.

    paramvalue: Union[int, float, str]
        Parameter value.

    Examples
    --------
    >>> setParam("MaxTime", 10)
    >>> setParam("MaxTi*", 10)
    >>> setParam("MaxTi*", "default")

    Notes
    -----
    1. This modification applies to all models that can be returned from models().
    2. Parameter names can contain '*' and '?' wildcards. If more than one parameter name
       is matched, the parameter value is not modified.
    3. When the parameter value is 'default', you can reset the parameter to its default
       value.
    '''

def system(command: str) -> None:
    '''
    Start a process in shell to execute commands or scripts

    Parameters
    ----------
    command: str
        The list of command or script parameters to be executed.

    Examples
    --------
    >>> system("echo 'mindopt'")

    '''

class tupledict(dict[_T, _U]):

    def __init__(self, *args, **kwargs) -> None:
        '''
        Construct a tupledict.

        Parameters
        ----------
        *args
            Array parameters.

        **kwargs
            Dictionary parameters.

        Examples
        --------
        >>> tupledict()
        >>> tupledict(another_dict)
        >>> tupledict([('a', 1), (' B ', 2)])
        >>> tupledict(a = 1, B = 2)

        '''

    def clean(self) -> None:
        '''
        Clear the index to release memory.

        Notes
        -----
        After the index is cleared, it will be rebuilt before a query is performed again.
        '''

    def prod(self, coeffs: dict, *query) -> Union[LinExpr, QuadExpr]:
        '''
        Specify a row vector and a query to produce a column vector, then return the
        product of the two vectors. The product is an expression.

        Parameters
        ----------
        coeffs: dict
            Row vector.

        *query
            The pattern of the key to be matched. The matching result is used as the column
            vector.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVars([(1,1), (1,2), (1,3)])
        >>> coeff = dict([((1,1), 1), ((1,2), 2), ((1,3), 3)])
        >>> expr = x.prod(coeff)
        >>> expr = x.prod(coeff, '*', 3)

        '''

    def select(self, *query) -> list[_U]:
        '''
        Query the tupledict to obtain the matching value list.

        Parameters
        ----------
        *query
            The pattern of the key to be matched.

        Examples
        --------
        >>> li = tupledict([((1, 2), 3), ((2, 2), 4)])
        >>> li.select(1)
        >>> li.select('*', 2)

        Notes
        -----
        Calling `select` triggers the creation of index, but modifying the tupledict clears
        the index. Avoid frequent index creation.
        '''

    def sum(self, *query) -> Union[LinExpr, QuadExpr]:
        '''
        Query a list from tupledict, and sum them as an expression.

        Parameters
        ----------
        *query
            The pattern of the key to be matched.

        Examples
        --------
        >>> m = Model()
        >>> x = m.addVar()
        >>> y = m.addVar()
        >>> mapping1 = ((1, 2), 1 * x + 2 * y)
        >>> mapping2 = ((2, 1), 2 * x + 1 * y)
        >>> td = tupledict([mapping1, mapping2])
        >>> linExpr = td.sum('*')

        '''

class tuplelist(list[_T]):

    def __init__(self, li, wildcard) -> None:
        '''
        Construct a tuplelist

        Parameters
        ----------
        li
            The array of data that is initially appended.

        wildcard
            The string that matches any value. Default value '*'

        Examples
        --------
        >>> li = tuplelist([(1, 2), (3, 4)], wildcard='@')

        Notes
        -----
        The elements of the input array can be scalar or tuple. If it is a tuple, all
        tuples must have the same length.
        '''

    def clean(self) -> None:
        '''
        Clear the index of the tuplelist to release memory.

        Notes
        -----
        After the index is cleared, it will be rebuilt when a query is performed again.
        '''

    def select(self, *query) -> tuplelist[_T]:
        '''
        Match scalar or tuple from tuplelist

        Parameters
        ----------
        *query
            The tuple pattern to match.

        Examples
        --------
        >>> li = tuplelist([(1, 2, 3), (2, 2, 3)])
        >>> li.select('*', 2, 3)
        >>> li.select(1)
        >>> li.select(1, 2)

        Notes
        -----
        Calling `select` triggers the creation of index, but modifying the tuplelist clears
        the index. Avoid frequent index creation.
        '''

def version() -> tuple:
    '''
    Retrieve version numbers of MindOpt.

    '''

def writeParams(filename: str) -> None:
    '''
    Writes the parameter settings of the current default Environment to a file.

    Parameters
    ----------
    filename: str
        The name of the file.

    Examples
    --------
    >>> writeParams("settings.prm")

    Notes
    -----
    If the current default Environment is released, the method reports an error.
    '''

class CallbackClass:

    MIPSTART: str = ...
    '''MIP Optimizer is in initial optimization phase.'''

    MIPSOL: str = ...
    '''MIP Optimizer just found a new incumbent solution.'''

    MIPNODE: str = ...
    '''MIP Optimizer is currently exploring a node.'''

    PRE_NUMVARS: str = ...
    '''Number columns of the presolved model.'''

    PRE_NUMCONSTRS: str = ...
    '''Number rows of the presolved model.'''

    PRE_NUMNZS: str = ...
    '''Number nonzero elements of the presolved model.'''

    MIP_OBJBST: str = ...
    '''Current best objective (global primal bound). '''

    MIP_OBJBND: str = ...
    '''Current best objective bound (global dual bound).'''

    MIP_RELVAL: str = ...
    '''Current relaxation objective (local dual bound).'''

    MIP_NODCNT: str = ...
    '''Total number of nodes explored so far. '''

    MIP_SOLCNT: str = ...
    '''Total number of feasible solutions found so far. '''

    MIP_CUTCNT: str = ...
    '''Total number of cutting planes applied so far. '''

    MIP_NODLFT: str = ...
    '''Total number of nodes unexplored nodes. '''

    MIP_NODEID: str = ...
    '''The unique ID of the current node. '''

    MIP_DEPTH: str = ...
    '''The depth of the current node. '''

    MIP_PHASE: str = ...
    '''Current phase in the MIP optimizer. (0: no solution; 1: far away from optimum; 2: close to the optimum) '''

    MIP_SOL: str = ...
    '''Array to hold the best solution(in original domain) found so far.'''

    MIP_REL: str = ...
    '''Array to hold the relaxation solution(in original domain) found so far.'''

class StatusConstClass:

    UNKNOWN: str = ...
    '''Model status is not available.'''

    OPTIMAL: str = ...
    '''Model was proven to be primal/dual feasible, and an optimal solution is available.'''

    INFEASIBLE: str = ...
    '''Model was proven to be primal infeasible.'''

    UNBOUNDED: str = ...
    '''Model was proven to be primal unbounded.'''

    INF_OR_UBD: str = ...
    '''Model was proven to be either primal infeasible or primal unbounded.'''

    SUB_OPTIMAL: str = ...
    '''A sub-optimal solution is available.'''

    ITERATION_LIMIT: str = ...
    '''IterationLimit exceeded.'''

    TIME_LIMIT: str = ...
    '''TimeLimit exceeded.'''

    NODE_LIMIT: str = ...
    '''NodeLimit exceeded.'''

    SOLUTION_LIMIT: str = ...
    '''SolutionLimit exceeded.'''

    STALLING_NODE_LIMIT: str = ...
    '''StallingNodeLimit exceeded.'''

    INTERRUPTED: str = ...
    '''Optimization was terminated by the user.'''

class ErrorConstClass:

    OKAY: str = ...
    '''Nothing wrong.'''

    ERROR: str = ...
    '''Unspecified internal error.'''

    NOMEMORY: str = ...
    '''Insufficient memory.'''

    INVALID_ARGUMENT: str = ...
    '''Arguments is not valid.'''

    INVALID_LICENSE: str = ...
    '''License is not valid.'''

    HOME_ENV_NOT_FOUND: str = ...
    '''MINDOPT_HOME does not exists.'''

    DLL_ERROR: str = ...
    '''Failed to load a dynamic library.'''

    IO_ERROR: str = ...
    '''General IO error.'''

    FILE_READ_ERROR: str = ...
    '''Failed to read data from file.'''

    FILE_WRITE_ERROR: str = ...
    '''Failed to write data to file.'''

    DIRECTORY_ERROR: str = ...
    '''Invalid directory.'''

    FORMAT_ERROR: str = ...
    '''Failed to parse the file.'''

    VERSION_ERROR: str = ...
    '''Failed to load model/parameter from file due to incompatible version error.'''

    REMOTE_INVALID_TOKEN: str = ...
    '''The input token ID for the remote computing is not valid.'''

    REMOTE_CONNECTION_ERROR: str = ...
    '''Failed to connect to the remote computing server.'''

    MODEL_INPUT_ERROR: str = ...
    '''Failed to input/load a model.'''

    MODEL_EMPTY: str = ...
    '''Model is empty.'''

    MODEL_INVALID_ROW_IDX: str = ...
    '''Row index is not valid .'''

    MODEL_INVALID_COL_IDX: str = ...
    '''Column index is not valid.'''

    MODEL_INVALID_ROW_NAME: str = ...
    '''Row name is not valid.'''

    MODEL_INVALID_COL_NAME: str = ...
    '''Column name is not valid.'''

    MODEL_INVALID_SYM_MAT_IDX: str = ...
    '''Index of the symmetric matrix is not valid.'''

    MODEL_INVALID_SYM_MAT_ROW_IDX: str = ...
    '''Row index of a symmetric matrix is not valid.'''

    MODEL_INVALID_SYM_MAT_COL_IDX: str = ...
    '''Column index of a symmetric matrix is not valid.'''

    MODEL_INVALID_STR_ATTR: str = ...
    '''A string attribute was not recognized.'''

    MODEL_INVALID_INT_ATTR: str = ...
    '''An integer attribute was not recognized.'''

    MODEL_INVALID_REAL_ATTR: str = ...
    '''A real attribute was not recognized.'''

    MODEL_INVALID_REAL_ATTR_SYM_MAT: str = ...
    '''A real attribute for symmetric matrix was not recognized.'''

    MODEL_INVALID_CHAR_ATTR: str = ...
    '''A char attribute was not recognized.'''

    MODEL_INVALID_MAT_ATTR: str = ...
    '''A matrix attribute was not recognized.'''

    MODEL_INVALID_ATTR_NAME: str = ...
    '''An attribute name was not recognized.'''

    MODEL_INVALID_SOS_TYPE: str = ...
    '''A SOS type was not recognized.'''

    MODEL_INVALID_SOS_IDX: str = ...
    '''SOS index is not valid.'''

    MODEL_INVALID_INDICATOR_COL_IDX: str = ...
    '''Column index to specify a indicator variable is not valid.'''

    MODEL_INVALID_INDICATOR_ROW_IDX: str = ...
    '''Indicator constraint index is not valid.'''

    MODEL_INVALID_INT_RELAX: str = ...
    '''Integral column cannot be relaxed, due to indicator constraints.'''

    DATA_NOT_AVAILABLE: str = ...
    '''Attempted to query or set an attribute that could not be accessed at that time.'''

    NO_SOLN: str = ...
    '''Solution is not available.'''

    NO_RAY: str = ...
    '''Unbounded ray is not available.'''

    NO_STATISTICS: str = ...
    '''Solver statistics is not available.'''

    INVALID_BASIS_STATUS: str = ...
    '''Unrecognized basis status.'''

    IIS_NO_SOLN: str = ...
    '''No IIS available for the current model.'''

    IIS_FEASIBLE: str = ...
    '''IIS is not available on a feasible model.'''

    INVALID_SOL_IDX: str = ...
    '''Solution index to retrieve is out of range'''

    PARAM_SET_ERROR: str = ...
    '''Failed to change a parameter value.'''

    PARAM_GET_ERROR: str = ...
    '''Failed to retrieve a parameter value.'''

    CB_INVALID_WHERE: str = ...
    '''Invalid `where` argument in a callback function.'''

    CB_INVALID_WHAT: str = ...
    '''Invalid `what` argument in a callback function.'''

    CB_INVALID_SUBMISSION: str = ...
    '''An error occured in a submission-type (cbsolution, cbcut, cbbranch) callback function.'''

    ABORT_INVALID_METHOD: str = ...
    '''Selected optimization method is not supported.'''

    ABORT_SOLVER_NOT_AVAILABLE: str = ...
    '''Optimization solver is not available for the input model.'''

    SIMPLEX_NUMERIC: str = ...
    '''Numerical difficulties in Simplex algorithm.'''

    INTERIOR_NUMERIC: str = ...
    '''Numerical difficulties in Interior-point algorithm.'''

    IIS_NUMERIC: str = ...
    '''Numerical difficulties occured while computing IIS.'''

class MDO:

    Attr: AttrConstClass = ...

    Callback: CallbackClass = ...

    Error: ErrorConstClass = ...

    Param: ParamConstClass = ...

    Status: StatusConstClass = ...

    attr: AttrConstClass = ...

    error: ErrorConstClass = ...

    param: ParamConstClass = ...

    status: StatusConstClass = ...

    UNDEFINED: str = ...
    '''Indicates a undefined number'''

    INFINITY: str = ...
    '''Any value greater-than-or-equal-to this number is considered as numerical infinity'''

    GENCONSTR_INDICATOR: str = ...
    '''General constraint types'''

    CONTINUOUS: str = ...
    '''Variable types'''

    BINARY: str = ...
    '''Variable types'''

    INTEGER: str = ...
    '''Variable types'''

    SEMICONT: str = ...
    '''Variable types'''

    SEMIINT: str = ...
    '''Variable types'''

    EQUAL: str = ...
    '''Sense values'''

    LESS_EQUAL: str = ...
    '''Sense values'''

    GREATER_EQUAL: str = ...
    '''Sense values'''

    MINIMIZE: str = ...
    '''Obj sense values'''

    MAXIMIZE: str = ...
    '''Obj sense values'''

    SOS_TYPE1: str = ...
    '''SOS types'''

    SOS_TYPE2: str = ...
    '''SOS types'''

    OKAY: str = ...
    '''Nothing wrong.'''

    ERROR: str = ...
    '''Unspecified internal error.'''

    NOMEMORY: str = ...
    '''Insufficient memory.'''

    INVALID_ARGUMENT: str = ...
    '''Arguments is not valid.'''

    INVALID_LICENSE: str = ...
    '''License is not valid.'''

    HOME_ENV_NOT_FOUND: str = ...
    '''MINDOPT_HOME does not exists.'''

    DLL_ERROR: str = ...
    '''Failed to load a dynamic library.'''

    IO_ERROR: str = ...
    '''General IO error.'''

    FILE_READ_ERROR: str = ...
    '''Failed to read data from file.'''

    FILE_WRITE_ERROR: str = ...
    '''Failed to write data to file.'''

    DIRECTORY_ERROR: str = ...
    '''Invalid directory.'''

    FORMAT_ERROR: str = ...
    '''Failed to parse the file.'''

    VERSION_ERROR: str = ...
    '''Failed to load model/parameter from file due to incompatible version error.'''

    REMOTE_INVALID_TOKEN: str = ...
    '''The input token ID for the remote computing is not valid.'''

    REMOTE_CONNECTION_ERROR: str = ...
    '''Failed to connect to the remote computing server.'''

    MODEL_INPUT_ERROR: str = ...
    '''Failed to input/load a model.'''

    MODEL_EMPTY: str = ...
    '''Model is empty.'''

    MODEL_INVALID_ROW_IDX: str = ...
    '''Row index is not valid .'''

    MODEL_INVALID_COL_IDX: str = ...
    '''Column index is not valid.'''

    MODEL_INVALID_ROW_NAME: str = ...
    '''Row name is not valid.'''

    MODEL_INVALID_COL_NAME: str = ...
    '''Column name is not valid.'''

    MODEL_INVALID_SYM_MAT_IDX: str = ...
    '''Index of the symmetric matrix is not valid.'''

    MODEL_INVALID_SYM_MAT_ROW_IDX: str = ...
    '''Row index of a symmetric matrix is not valid.'''

    MODEL_INVALID_SYM_MAT_COL_IDX: str = ...
    '''Column index of a symmetric matrix is not valid.'''

    MODEL_INVALID_STR_ATTR: str = ...
    '''A string attribute was not recognized.'''

    MODEL_INVALID_INT_ATTR: str = ...
    '''An integer attribute was not recognized.'''

    MODEL_INVALID_REAL_ATTR: str = ...
    '''A real attribute was not recognized.'''

    MODEL_INVALID_REAL_ATTR_SYM_MAT: str = ...
    '''A real attribute for symmetric matrix was not recognized.'''

    MODEL_INVALID_CHAR_ATTR: str = ...
    '''A char attribute was not recognized.'''

    MODEL_INVALID_MAT_ATTR: str = ...
    '''A matrix attribute was not recognized.'''

    MODEL_INVALID_ATTR_NAME: str = ...
    '''An attribute name was not recognized.'''

    MODEL_INVALID_SOS_TYPE: str = ...
    '''A SOS type was not recognized.'''

    MODEL_INVALID_SOS_IDX: str = ...
    '''SOS index is not valid.'''

    MODEL_INVALID_INDICATOR_COL_IDX: str = ...
    '''Column index to specify a indicator variable is not valid.'''

    MODEL_INVALID_INDICATOR_ROW_IDX: str = ...
    '''Indicator constraint index is not valid.'''

    MODEL_INVALID_INT_RELAX: str = ...
    '''Integral column cannot be relaxed, due to indicator constraints.'''

    DATA_NOT_AVAILABLE: str = ...
    '''Attempted to query or set an attribute that could not be accessed at that time.'''

    NO_SOLN: str = ...
    '''Solution is not available.'''

    NO_RAY: str = ...
    '''Unbounded ray is not available.'''

    NO_STATISTICS: str = ...
    '''Solver statistics is not available.'''

    INVALID_BASIS_STATUS: str = ...
    '''Unrecognized basis status.'''

    IIS_NO_SOLN: str = ...
    '''No IIS available for the current model.'''

    IIS_FEASIBLE: str = ...
    '''IIS is not available on a feasible model.'''

    INVALID_SOL_IDX: str = ...
    '''Solution index to retrieve is out of range'''

    PARAM_SET_ERROR: str = ...
    '''Failed to change a parameter value.'''

    PARAM_GET_ERROR: str = ...
    '''Failed to retrieve a parameter value.'''

    CB_INVALID_WHERE: str = ...
    '''Invalid `where` argument in a callback function.'''

    CB_INVALID_WHAT: str = ...
    '''Invalid `what` argument in a callback function.'''

    CB_INVALID_SUBMISSION: str = ...
    '''An error occured in a submission-type (cbsolution, cbcut, cbbranch) callback function.'''

    ABORT_INVALID_METHOD: str = ...
    '''Selected optimization method is not supported.'''

    ABORT_SOLVER_NOT_AVAILABLE: str = ...
    '''Optimization solver is not available for the input model.'''

    SIMPLEX_NUMERIC: str = ...
    '''Numerical difficulties in Simplex algorithm.'''

    INTERIOR_NUMERIC: str = ...
    '''Numerical difficulties in Interior-point algorithm.'''

    IIS_NUMERIC: str = ...
    '''Numerical difficulties occured while computing IIS.'''
