# This file is part of the mlhp project. License: See LICENSE

import mlhp
import unittest
import math

class CollectionTest(unittest.TestCase):
    def test_integrateScalarFunction2D(self):
        D = 2
        radius = 0.8
        order = 2

        domain = mlhp.implicitSphere([0.0] * D, radius)
        mesh = mlhp.makeGrid([axis + 3 for axis in range(D)], [2] * D, [-1] * D)
        basis = mlhp.makeDummyBasis(mesh)
        target = mlhp.ScalarDouble()

        quadratureOrder = mlhp.relativeQuadratureOrder(D, order)
        quadratureScheme = mlhp.momentFittingQuadrature(domain, depth=5, epsilon=0.0)
        #quadratureScheme = mlhp.spaceTreeQuadrature(domain, depth=5, epsilon=0.0)
        
        integrand = mlhp.functionIntegrand(mlhp.scalarField(D, 1.0))
        
        mlhp.integrateOnDomain(basis, integrand, [target], quadrature=quadratureScheme, orderDeterminor=quadratureOrder)

        expected = math.pi**(D / 2) / math.gamma(D / 2 + 1) * radius**D
        error = abs(expected - target.get()) / expected
        
        #print(error)
        
        self.assertAlmostEqual(error, 0.0007483838265199594, places=6)
        
    def test_integrateVectorFunction3D(self):
        D = 3
        radius = 0.83
        order = 2

        domain = mlhp.implicitSphere([0.0] * D, radius)
        
        r = "((x**2 + y**2 + z**2)**(1/2))"
        
        f0 = f"-2 * {r}**3 + 3 * {r}**2 + 1"
        f1 = f"4 * (1 - {r}**2)"
        
        function = mlhp.vectorField(D, f"[{f0}, {f1}]")
        
        mesh = mlhp.makeGrid([6 - axis for axis in range(D)], [2] * D, [-1] * D)
        basis = mlhp.makeDummyBasis(mesh)
        targets = [mlhp.ScalarDouble() for _ in range(2)]

        #meshcreator = mlhp.marchingCubesVolume(function=domain, resolution=[4] * D, coarsen=True, meshBothSides=False)
        #quadratureScheme = mlhp.cellMeshQuadrature(meshcreator)
        #quadratureScheme = mlhp.momentFittingQuadrature(domain, depth=3, epsilon=0.0)
        quadratureScheme = mlhp.spaceTreeQuadrature(domain, depth=4, epsilon=0.0)
        
        quadratureOrder = mlhp.relativeQuadratureOrder(D, order)
        integrand = mlhp.functionIntegrand(function)
        
        mlhp.integrateOnDomain(basis, integrand, targets, quadrature=quadratureScheme, orderDeterminor=quadratureOrder)
        
        result = [target.get() for target in targets]
        
        expected0 = 4 * math.pi * (-2/6 * radius**6 + 3/5 * radius**5 + 1/3 * radius**3)
        expected1 = 16 * math.pi * (radius**3 / 3 - radius**5 / 5)
        
        error0 = abs(expected0 - targets[0].get()) / expected0
        error1 = abs(expected1 - targets[1].get()) / expected1
        
        #print(error0, error1)
        
        self.assertAlmostEqual(error0, 3.404156148046146e-05, places=6)
        self.assertAlmostEqual(error1, 5.345606556139261e-06, places=6)
        
        # Integral in spherical coordinates:
        # int_rho(0, 2*pi) int_phi(0, pi) int_r(0, R)  f * r**2 * sin(phi) * dr * dphi * drho
        #
        # f = f1: int_rho(0, 2*pi) int_phi(0, pi) int_r(0, R) (-2 * r**3 + 3 * r**2 + 1) * r**2 * sin(phi) * dr * dphi * drho =
        #         int_rho(0, 2*pi) int_phi(0, pi) (-2/6 * R**6 + 3/5 * R**5 + 1/3 * R**3) * [-cos(phi)](0, pi) * drho =
        #         int_rho(0, 2*pi) 2 * (-2/6 * R**6 + 3/5 * R**5 + 1/3 * R**3) * drho =
        #         4*pi * (-2/6 * R**6 + 3/5 * R**5 + 1/3 * R**3)
        #      
        # f = f2: int_rho(0, 2*pi) int_phi(0, pi) int_r(0, R) 4 * (1 - r**2) * r**2 * sin(phi) * dr * dphi * drho =
        #         int_rho(0, 2*pi) int_phi(0, pi) 4/3 * R**3 - 4/5 * R**5 * sin(phi) * dphi * drho =
        #         16 * pi * (R**3 / 3 - R**5 / 5)
        
        
