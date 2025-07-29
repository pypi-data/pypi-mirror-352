import mlhp
import math

D = 2

print("1. Preprocessing", flush=True)

nelements = 100
degree = 2
alpha = 1e-4
treedepth = degree + 3
filterElements = True

domain = mlhp.invert(mlhp.implicitSphere([0.0] * D, 0.5))

baseGrid = mlhp.makeGrid(nelements=[nelements] * D, lengths=[1.0] * D, origin=[0.0] * D)

if filterElements:
    baseGrid = mlhp.makeFilteredGrid(baseGrid, domain=domain, nseedpoints=degree + 2)

mesh = mlhp.makeRefinedGrid(baseGrid)
basis = mlhp.makeHpTrunkSpace(mesh, degrees=degree, nfields=D)

print(basis)

print("2. Assembly", flush=True)

# Determine Dirichlet dofs
leftDirichlet = mlhp.integrateDirichletDofs(mlhp.scalarField(D, 0.0), basis, [0], ifield=0)
bottomDirichlet = mlhp.integrateDirichletDofs(mlhp.scalarField(D, 0.0), basis, [2], ifield=1)

dirichletDofs=mlhp.combineDirichletDofs([leftDirichlet, bottomDirichlet])

# Allocate linear system for internal dofs
matrix = mlhp.allocateSparseMatrix(basis, dirichletDofs[0])
vector = mlhp.allocateRhsVector(matrix)

print(matrix)

# Assemble domain contribution
E = mlhp.scalarField(D, 206900 * 1e6)
nu = mlhp.scalarField(D, 0.29)
rhs = mlhp.vectorField(D, [0.0] * D)

kinematics = mlhp.smallStrainKinematics(D) 
constitutive = mlhp.planeStressMaterial(E, nu)
domainIntegrand = mlhp.staticDomainIntegrand(kinematics, constitutive, rhs)

#quadrature = mlhp.spaceTreeQuadrature(domain, depth=treedepth, epsilon=alpha)
quadrature = mlhp.momentFittingQuadrature(domain, depth=treedepth, epsilon=alpha) 

mlhp.integrateOnDomain(basis, domainIntegrand, [matrix, vector], quadrature=quadrature, dirichletDofs=dirichletDofs)

# Assemble traction integral
topQuadrature = mlhp.quadratureOnMeshFaces(mesh, [3], degree + 1)
forceIntegrand = mlhp.normalNeumannIntegrand(mlhp.scalarField(D, 100 * 1e6))
mlhp.integrateOnSurface(basis, forceIntegrand, [vector], topQuadrature, dirichletDofs=dirichletDofs)

print("3. Linear system solution", flush=True)
#import mklwrapper
#interiorDofs = mklwrapper.pardisoSolve(matrix, vector)

interiorDofs = mlhp.makeCGSolver(rtol=1e-12, maxiter=10000)(matrix, vector)
allDofs = mlhp.inflateDofs(interiorDofs, dirichletDofs)

print("4. Error integration", flush=True)

internalEnergy = mlhp.ScalarDouble(0.0)
energyIntegrand = mlhp.internalEnergyIntegrand(allDofs, kinematics, constitutive)
mlhp.integrateOnDomain(basis, energyIntegrand, [internalEnergy], quadrature=quadrature)

# This "exact" solution was computed with an overkill solution
relativeError = math.sqrt(abs(internalEnergy.get() - 5.78769965054534e4) / 5.78769965054534e4)

print(f"   Relative error: {100 * relativeError:.2e} percent")

# Check consistency with previous result
assert(abs(relativeError - 0.0019) < 1e-5)

print("5. File output", flush=True)

processors = [mlhp.solutionProcessor(D, allDofs, "Displacement"),
              mlhp.vonMisesProcessor(allDofs, kinematics, constitutive),
              mlhp.functionProcessor(domain)]

gridmesh = mlhp.gridOnCells([1 if degree == 1 else degree + 2] * D)
gridwriter = mlhp.PVtuOutput(filename="outputs/single")
mlhp.writeBasisOutput(basis, gridmesh, gridwriter, processors)
