// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core.hpp"

using namespace mlhp;

int main( )
{
    auto time = utilities::tic( );

    static constexpr size_t D = 3;

    // Domain
    auto domainTriangulation = createTriangulation<3>( readStl( "geometry.stl" ) );
    auto domainKdtree = buildKdTree( domainTriangulation );
    auto domain = makeTriangulationDomain( &domainTriangulation, &domainKdtree );

    auto [min, max] = spatial::extendBoundingBox( domainTriangulation.boundingBox( ) );

    // Discretization
    auto nelements = std::array<size_t, 3> { 50, 50, 50 };
    auto degrees = array::makeSizes<D>( 1 );
    auto resolution = array::add<size_t>( degrees, 1 );
    auto penaltyFCM = 1e-5;
    auto integrationSpaceTreeDepth = size_t { 1 };

    // Create and refine grid
    auto unfiltered = makeCartesianGrid( nelements, max - min, min );
    auto cutstate = mesh::cutstate( *unfiltered, domain, 3 );
    auto filtered = std::make_shared<FilteredGrid<D>>( unfiltered, std::move( cutstate ) );
    auto grid = makeRefinedGrid<D>( filtered );

    print( *grid, std::cout );

    auto nfields = size_t { D };

    // Create mlhp basis on refined grid
    auto basis = makeHpBasis<TrunkSpace>( grid, UniformGrading { degrees }, nfields );

    print( *basis, std::cout );

    // Allocate sparse linear system
    auto matrix = allocateMatrix<linalg::UnsymmetricSparseMatrix>( *basis );
    auto rhs = std::vector<double>( matrix.size1( ), 0.0 );

    linalg::print( matrix, std::cout );

    // Extract left face from triangulation and compute Dirichlet boundary integral
    auto surface0Filter = implicit::cube<3>( { min[0] - 1e-8, min[1], min[2] }, { min[0] + 1e-8, max[1], max[2] } );
    auto surface0 = filterTriangulation( domainTriangulation, surface0Filter );
    auto [intersected0, celldata0] = intersectTriangulationWithMesh( *grid, surface0, buildKdTree( surface0 ) );

    auto boundaryIntegrand0 = makeL2BoundaryIntegrand<D>( spatial::constantFunction<D>( array::make<D>( 1e15 ) ),
                                                          spatial::constantFunction<D>( array::make<D>( 1e15 * 0.0 ) ) );

    auto boundaryQuadrature0 = TriangulationQuadrature<D>( &intersected0, &celldata0, array::maxElement( degrees ) );

    integrateOnSurface( *basis, boundaryIntegrand0, boundaryQuadrature0, { matrix, rhs } );
    
    // Extract right face from triangulation and compute traction boundary integral
    auto surface1Filter = implicit::cube<3>( { max[0] - 1e-8, min[1], min[2] }, { max[0] + 1e-8, max[1], max[2] } );
    auto surface1 = filterTriangulation( domainTriangulation, surface1Filter );
    auto [intersected1, celldata1] = intersectTriangulationWithMesh( *grid, surface1, buildKdTree( surface1 ) );

    auto boundaryIntegrand1 = makeNeumannIntegrand<D>( spatial::constantFunction<D>( std::array { 1.0, 0.2, 0.0 } ) );
    auto boundaryQuadrature1 = TriangulationQuadrature<D>( &intersected1, &celldata1, array::maxElement( degrees ) );

    integrateOnSurface( *basis, boundaryIntegrand1, boundaryQuadrature1, { rhs } );

    // Domain integral
    auto domainQuadrature = MomentFittingQuadrature<D>( domain, penaltyFCM, integrationSpaceTreeDepth );
    //auto domainQuadrature = SpaceTreeQuadrature<D>( domain, penaltyFCM, integrationSpaceTreeDepth );

    auto E = spatial::constantFunction<D>( 2.0e5 );
    auto nu = spatial::constantFunction<D>( 0.2 );
    auto bodyForce = spatial::constantFunction<D>( std::array { 0.0, 0.0, 0.0 } );

    auto kinematics = makeSmallStrainKinematics<D>( );
    auto material = makeIsotropicElasticMaterial( E, nu );
    auto integrand = makeStaticDomainIntegrand<D>( kinematics, material, bodyForce );

    integrateOnDomain( *basis, integrand, { matrix, rhs }, domainQuadrature );

    time = utilities::toc( time, "Preprocessing and assembly took: " );

    // Solve linear system
    auto multiplyM = makeDefaultMultiply( matrix );
    auto multiplyP = linalg::makeDiagonalPreconditioner( matrix );

    auto solution = std::vector<double>( matrix.size1( ), 0.0 );

    linalg::cg( multiplyM, rhs, solution, 1e-6, 0.0, matrix.size1( ), multiplyP );
    
    time = utilities::toc( time, "Solving took:                    " );

    // Postprocess on different geometries
    auto processors = std::tuple
    {
        //makeFunctionProcessor<D>( domain, "Domain" ),
        makeSolutionProcessor<D>( solution, "Displacement" ),
        makeVonMisesProcessor<D>( solution, kinematics, material )
    };

    auto [domainIntersected, domainCelldata] = intersectTriangulationWithMesh( *grid, domainTriangulation, domainKdtree );

    auto fcmMeshPostmesh = cellmesh::createGrid( array::makeSizes<D>( 1 ) );
    auto domainBoundaryPostmesh = cellmesh::associatedTriangles( domainIntersected, domainCelldata );
    auto fcmQuadraturePostmesh = cellmesh::quadraturePoints( domainQuadrature, *basis, relativeQuadratureOrder<D>( ) );
    auto surface0BoundaryPostmesh = cellmesh::associatedTriangles( intersected0, celldata0 );
    auto surface0QuadraturePostmesh = cellmesh::quadraturePoints( boundaryQuadrature0 );
    auto surface1BoundaryPostmesh = cellmesh::associatedTriangles( intersected1, celldata1 );
    auto surface1QuadraturePostmesh = cellmesh::quadraturePoints( boundaryQuadrature1 );

    // Finte cell mesh and quadrature points
    writeOutput( *basis, fcmMeshPostmesh, processors, PVtuOutput { "outputs/stl_fcm_mesh" } );
    writeOutput( *basis, fcmQuadraturePostmesh, processors, PVtuOutput { "outputs/stl_fcm_quadrature" } );

    // Domain boundary
    writeOutput( *basis, domainBoundaryPostmesh, processors, PVtuOutput { "outputs/stl_domain_boundary" } );
    
    // Dirichlet boundary
    writeOutput( *basis, surface0BoundaryPostmesh, processors, PVtuOutput { "outputs/stl_surface0_boundary" } );
    writeOutput( *basis, surface0QuadraturePostmesh, processors, PVtuOutput { "outputs/stl_surface0_quadrature" } );
    
    // Traction boundary
    writeOutput( *basis, surface1BoundaryPostmesh, processors, PVtuOutput { "outputs/stl_surface1_boundary" } );
    writeOutput( *basis, surface1QuadraturePostmesh, processors, PVtuOutput { "outputs/stl_surface1_quadrature" } );

    utilities::toc( time, "Postprocessing took:             " );
}
