// This file is part of the mlhp project. License: See LICENSE

#include "mlhp/core/triangulation.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/algorithm.hpp"
#include "mlhp/core/quadrature.hpp"

#include <execution>
#include <filesystem>
#include <climits>

namespace mlhp
{

using namespace marchingcubes;

template<size_t D>
std::array<size_t, 3> Triangulation<D>::triangleIndices( size_t itriangle ) const
{
    MLHP_CHECK( itriangle < ntriangles( ), "Invalid triangle index." );

    return triangles[itriangle];
}

template<size_t D>
spatial::Triangle<D> Triangulation<D>::triangleVertices( size_t itriangle ) const
{
    auto [i0, i1, i2] = triangleIndices( itriangle ); 

    return { vertices[i0], vertices[i1], vertices[i2] };
}

template<size_t D>
spatial::BoundingBox<D> Triangulation<D>::boundingBox( ) const
{
    return spatial::boundingBox<D>( vertices );
}

template<size_t D>
spatial::BoundingBox<D> Triangulation<D>::boundingBox( size_t itriangle ) const
{
    return spatial::boundingBox<D>( triangleVertices( itriangle ) );
}

template<size_t D>
double Triangulation<D>::area( ) const
{
    auto limit = static_cast<std::int64_t>( ntriangles( ) );
    auto area = 0.0;

    #pragma omp parallel for schedule( dynamic, 512 ) reduction(+:area)
    for( std::int64_t ii = 0; ii < limit; ++ii )
    {
        auto [v0, v1, v2] = triangleVertices( static_cast<size_t>( ii ) );

        if constexpr( D == 3 )
        {
            area += 0.5 * spatial::norm( spatial::cross( v1 - v0, v2 - v0 ) );
        }
        else if constexpr ( D == 2 )
        {
            area += 0.5 * std::abs( ( v1[0] - v0[0] ) * ( v2[1] - v0[1] ) -
                                    ( v2[0] - v0[0] ) * ( v1[1] - v0[1] ) );
        }
        else
        {
            MLHP_NOT_IMPLEMENTED;
        }
    }

    return area;
}

template<size_t D>
size_t Triangulation<D>::memoryUsage( ) const
{
    return utilities::vectorInternalMemory( vertices, triangles );
}

template<size_t D>
size_t TriangleCellAssociation<D>::memoryUsage( ) const
{
    return utilities::vectorInternalMemory( rst, offsets );
}

std::array<double, 3> integrateNormalComponents( const Triangulation<3>& triangulation, bool abs )
{
    static constexpr auto D = size_t { 3 };

    auto result = std::array<double, D> { };

    #pragma omp parallel
    {   
        auto local = std::array<double, D> { };
        auto ntriangles = static_cast<std::int64_t>( triangulation.ntriangles( ) );

        #pragma omp for schedule(static)
        for( std::int64_t ii = 0; ii < ntriangles; ++ii )
        {
            auto [v0, v1, v2] = triangulation.triangleVertices( static_cast<size_t>( ii ) );

            auto cross = spatial::triangleCross( v0, v1, v2 );

            for( size_t axis = 0; axis < D; ++axis )
            {
                local[axis] += abs ? std::abs( 0.5 * cross[axis] ) : 0.5 * cross[axis];
            }
        }

        #pragma omp critical
        {
            result = result + local;
        }
    }

    return result;
}

// https://stackoverflow.com/a/26171886
CoordinateList<3> readStl( const std::string& filename, bool flipOnOppositeNormal )
{
    auto path = std::filesystem::path { filename };
    auto file = std::ifstream { filename };
    auto line = std::string { };
    auto word = std::string { };
    
    MLHP_CHECK( file.is_open( ), "Error parsing stl file (unable to open file)." );

    auto filesize = std::filesystem::file_size( path );

    MLHP_CHECK( filesize >= 15, "Error parsing stl file (smaller than 15 bytes)." );

    auto vertices = CoordinateList<3> { };
    auto normals = CoordinateList<3> { };

    file >> line;

    auto ascii = false;

    // Parse Ascii
    if( line == "solid" )
    {
        while( std::getline( file, line ) )
        {
            auto sstream = std::istringstream { line };

            if( !sstream )
            {
                continue;
            }

            auto parseCoordinates = [&]( auto& target )
            { 
                auto coordinates = std::array<double, 3> { };
            
                for( size_t axis = 0; axis < 3; ++axis )
                {
                    sstream >> coordinates[axis];
                }

                target.push_back( coordinates );
            };
        
            sstream >> word;

            if( word == "vertex" )
            {
                parseCoordinates( vertices );
            }
            else if( word == "facet" )
            {
                sstream >> word;

                MLHP_CHECK( word == "normal", "Error parsing stl file (missing normal)." );

                parseCoordinates( normals );
            }
        }

        if( word == "endsolid" )
        {
            ascii = true;
        }
    }
    
    file.close( );

    // Parse binary
    if( !ascii )
    {
        MLHP_CHECK( sizeof( float ) * CHAR_BIT == 32, "Floats are not 32 bit (required for parsing binary STL)." );
        
        file = std::ifstream( filename, std::ifstream::binary );

        MLHP_CHECK( filesize >= 84, "Error parsing stl file (not ascii and smaller than 84 bytes)." );
        MLHP_CHECK( file.seekg( 80 ), "Error parsing stl file (Unable to seekg after header bytes)." );

        char header[4];

        file.read( header, 4 );

        MLHP_CHECK( file.good( ), "Error parsing stl file (binary header read failed)" );

        constexpr auto facetsize = 3 * 4 * sizeof( float ) + sizeof( int16_t );
        
        auto ntriangles = *reinterpret_cast<uint32_t*>( header );
        auto targetsize = 84 + ntriangles * facetsize;

        MLHP_CHECK( filesize == targetsize, "Error parsing stl file (not ascii and inconsistent size)." );

        vertices.resize( 3 * ntriangles );
        normals.resize( ntriangles );

        for( size_t itriangle = 0; itriangle < ntriangles; ++itriangle )
        {
            char buffer[facetsize];

            auto read = [&, index = size_t { 0 }]( ) mutable
            { 
                return *( reinterpret_cast<float*>( buffer ) + index++ );
            };
            
            file.read( buffer, facetsize );

            MLHP_CHECK( file.good( ), "Error parsing stl file (binary data read failed)" );

            for( size_t axis = 0; axis < 3; ++axis )
            {
                normals[itriangle][axis] = read( );
            }
            
            for( size_t ivertex = 0; ivertex < 3; ++ivertex )
            {
                for( size_t axis = 0; axis < 3; ++axis )
                {
                    vertices[3 * itriangle + ivertex][axis] = read( );
                }
            }

        } // for itriangle

        MLHP_CHECK( file.tellg( ) == static_cast<std::streamoff>( filesize ), 
                    "Error parsing stl file (not at end of file)." );
    
        file.close( );
    }

    // Fix vertex order based on normal vectors
    if( flipOnOppositeNormal )
    {
        for( size_t itriangle = 0; itriangle < normals.size( ); ++itriangle )
        {
            auto& v0 = vertices[3 * itriangle + 0];
            auto& v1 = vertices[3 * itriangle + 1];
            auto& v2 = vertices[3 * itriangle + 2];
        
            auto normal = spatial::triangleNormal( v0, v1, v2 );
            auto dot = spatial::dot( normal, normals[itriangle] );

            // Reverse order with inconsistent normals
            if( std::abs( dot + 1.0 ) < 0.01 )
            {
                std::swap( v1, v2 );
            }
        }
    }

    MLHP_CHECK( vertices.size( ) == 3 * normals.size( ), "Inconsistent sizes." );

    return vertices;
}

template<size_t D>
Triangulation<D> createTriangulation( CoordinateConstSpan<D> vertices )
{
    Triangulation<D> result;

    MLHP_CHECK( vertices.size( ) % 3 == 0, "Vertex number not a multiple of three." );

    result.vertices.resize( vertices.size( ) );
    result.triangles.resize( vertices.size( ) / 3 );

    std::copy( vertices.begin( ), vertices.end( ), result.vertices.begin( ) );

    for( size_t i = 0; i < result.triangles.size( ); ++i )
    {
        result.triangles[i][0] = 3 * i + 0;
        result.triangles[i][1] = 3 * i + 1;
        result.triangles[i][2] = 3 * i + 2;
    }

    return result;
}

size_t countIntersections( const KdTree<3>& tree,
                           const Triangulation<3>& triangulation,
                           const std::array<double, 3>& rayOrigin,
                           const std::array<double, 3>& rayDirection,
                           std::vector<size_t>& triangleTarget )
{
    kdtree::accumulateItems( tree, rayOrigin, rayDirection, utilities::resize0( triangleTarget ) );

    auto count = size_t { 0 };

    for( auto itriangle : triangleTarget )
    {
        MLHP_CHECK( itriangle < triangulation.triangles.size( ), "Invalid triangle index" );

        auto [v0, v1, v2] = triangulation.triangleVertices( itriangle );

        count += spatial::triangleRayIntersection( v0, v1, v2, rayOrigin, rayDirection ) != std::nullopt;
    }

    return count;
}

bool pointMembershipTest( const KdTree<3>& tree,
                          const Triangulation<3>& triangulation,
                          const std::array<double, 3>& rayOrigin,
                          [[maybe_unused]]const std::span<std::array<double, 3>> rayDirections,
                          std::vector<size_t>& triangleTarget )
{
    //auto sum = size_t { 0 };

    //for( auto direction : rayDirections )
    //{
    //    sum += countIntersections( tree, triangulation, rayOrigin, direction, triangleTarget ) % 2;
    //}

    //return ( 2 * sum ) / rayDirections.size( );
    
    auto ray = std::array { 0.3123, -0.423, 0.8323 };

    return countIntersections( tree, triangulation, rayOrigin, ray, triangleTarget) % 2;
}

MLHP_EXPORT
TriangulationDomain::TriangulationDomain( const TriangulationPtr& triangulation,
                                          const KdTreePtr& kdTree ) :
    triangulation_ { triangulation }, kdtree_ { kdTree }
{ 
    #pragma omp parallel
    {
        auto nleaves = static_cast<std::int64_t>( kdTree->ncells( ) );
        auto mapping = kdTree->createMapping( );
        auto rays = spatial::fibonacciSphere( 4 );
        auto items = std::vector<size_t> { };

        #pragma omp for
        for( std::int64_t ii = 0; ii < nleaves; ++ii )
        {
            auto ileaf = static_cast<CellIndex>( ii );
            auto ifull = kdTree->fullIndex( ileaf );
            auto state = std::int16_t { 0 };

            if( kdTree->itemsFull( ifull ).empty( ) )
            {
                kdtree_->prepareMapping( ileaf, mapping );

                state = pointMembershipTest( *kdtree_, *triangulation_, 
                    mapping( { } ), rays, items ) ? 1 : -1;
            }

            kdtree_->stateFull( ifull, state );
        }
    }
}

bool TriangulationDomain::inside( std::array<double, 3> xyz, std::vector<size_t>& cache ) const
{
    if( auto index = kdtree_->fullIndexAt( xyz ); index == NoCell )
    {
        return false;
    }
    else if( auto state = kdtree_->stateFull( index ); state != 0 )
    {
        return state > 0;
    }

    auto ray = std::array { 0.3123, -0.423, 0.8323 };

    return countIntersections( *kdtree_, *triangulation_, xyz, ray, cache ) % 2;
}

ImplicitFunction<3> makeTriangulationDomain( memory::vptr<Triangulation<3>> triangulation,
                                             memory::vptr<KdTree<3>> kdtree )
{
    static constexpr size_t D = 3;

    auto domain = TriangulationDomain { triangulation, kdtree };
    auto cache = utilities::ThreadLocalContainer<std::vector<size_t>> { };

    auto evaluateCached = [domain = std::move( domain ), cache = std::move( cache )] ( std::array<double, D> xyz ) mutable
    {
        return domain.inside( xyz, cache.get( ) );
    };

    return std::function { std::move( evaluateCached ) };
}

ImplicitFunction<3> makeTriangulationDomain( memory::vptr<Triangulation<3>> triangulation )
{
    return makeTriangulationDomain( triangulation, std::make_shared<KdTree<3>>( buildKdTree( *triangulation ) ) );
}

ImplicitFunction<3> makeTriangulationDomain( const std::string& stlfile )
{
    return makeTriangulationDomain( std::make_shared<Triangulation<3>>( createTriangulation<3>( readStl( stlfile ) ) ) );
}

namespace
{

std::optional<std::pair<size_t, size_t>> planarOnFace( const std::array<std::array<double, 3>, 3>& vertices )
{
    for( size_t axis = 0; axis < 3; ++axis )
    {
        for( size_t side = 0; side < 2; ++side )
        {
            auto x = side ? 1.0 : -1.0;
            auto planar = true;

            for( size_t ivertex = 0; ivertex < 3; ++ivertex )
            {
                planar = planar && std::abs( vertices[ivertex][axis] - x ) < 1e-8;
            }

            if( planar )
            {
                return std::pair { axis, side };
            }
        }
    }

    return std::nullopt;
}

template<size_t D>
bool intersectThisSide( const AbsMesh<D>& mesh, CellIndex icell, MeshCellFaces& neighbors, size_t iface )
{
    mesh.neighbours( icell, iface, utilities::resize0( neighbors ) );

    if( neighbors.size( ) != 1 )
    {
        return true;
    }

    auto [neighborIndex, neighborFace] = neighbors[0];

    mesh.neighbours( neighborIndex, neighborFace, utilities::resize0( neighbors ) );

    if( neighbors.size( ) == 1 )
    {
        return icell < neighborIndex;
    }

    return false;
}

} // namespace

CellAssociatedTriangulation<3> intersectTriangulationWithMesh( const AbsMesh<3>& mesh,
                                                               const Triangulation<3>& triangulation,
                                                               const KdTree<3>& tree )
{
    static constexpr size_t D = 3;

    auto ncells = static_cast<std::int64_t>( mesh.ncells( ) );
    
    //#pragma omp parallel
    {
        auto intersected = Triangulation<D> { };
        auto celldata = TriangleCellAssociation<D> { };

        celldata.offsets.resize( mesh.ncells( ) + 1, 0 );

        auto triangles = std::vector<size_t> { };
        auto neighbors = std::vector<MeshCellFace> { };

        auto forwardMapping = mesh.createMapping( );
        auto polyonTarget = std::array<std::array<double, D>, 9> { };

        //#pragma omp for
        for( std::int64_t ii = 0; ii < ncells; ++ii )
        {
            utilities::resize0( triangles );

            auto icell = static_cast<CellIndex>( ii );

            // Get mesh cell bounding box
            mesh.prepareMapping( icell, forwardMapping );

            MLHP_CHECK( forwardMapping.type == CellType::NCube, "Cell type not implemented." );

            auto bounds = mesh::boundingBox( forwardMapping, 2 );
            auto reference = array::maxElement( bounds[1] - bounds[0] );

            // Accumulate triangles inside mesh cell bounding box
            kdtree::accumulateItems( tree, bounds, triangles );

            // Loop over candidate triangles
            for( auto itriangle : triangles )
            {
                // Map triangle vertices to cell local coordinates
                auto vertices = triangulation.triangleVertices( itriangle );

                for( size_t ivertex = 0; ivertex < 3; ++ivertex )
                {
                    auto rst = mapBackward( forwardMapping, vertices[ivertex] );

                    MLHP_CHECK( rst, "Backward mapping did not converge." );

                    vertices[ivertex] = *rst;
                }

                auto localBounds = std::array { array::make<D>( -1.0 ), array::make<D>( 1.0 ) };

                if( auto planar = planarOnFace( vertices ) )
                {
                    if( intersectThisSide( mesh, icell, neighbors, 2 * planar->first + planar->second ) )
                    {
                        localBounds[0][planar->first] = std::numeric_limits<double>::lowest( );
                        localBounds[1][planar->first] = std::numeric_limits<double>::max( );
                    }
                    else
                    {
                        continue;
                    }
                }

                // Clip mapped triangle to local coordinate bounds
                auto polygon = spatial::clipTriangle<D>( vertices[0], 
                    vertices[1], vertices[2], localBounds, polyonTarget );

                // Remesh and append new triangles
                if( polygon.size( ) >= 3 )
                {
                    auto vertexOffset = intersected.vertices.size( );

                    for( auto& vertex : polygon )
                    {
                        celldata.rst.push_back( vertex );
                        
                        vertex = forwardMapping( vertex );

                        intersected.vertices.push_back( vertex );
                    }

                    for( size_t ivertex = 1; ivertex + 1 < polygon.size( ); ++ivertex )
                    {
                        auto i0 = vertexOffset;
                        auto i1 = vertexOffset + ivertex;
                        auto i2 = vertexOffset + ivertex + 1;

                        auto area = spatial::triangleArea( intersected.vertices[i0], 
                                                           intersected.vertices[i1], 
                                                           intersected.vertices[i2] );

                        if( area > 1e-8 * reference )
                        {

                            celldata.offsets[icell + 1] += 1;

                            intersected.triangles.push_back( std::array<size_t, 3> { i0, i1, i2 } );
                        }
                    }
                }
            }

        }

        std::partial_sum( celldata.offsets.begin( ), celldata.offsets.end( ), celldata.offsets.begin( ) );

        return std::pair { intersected, celldata };
    }
}

template<size_t D>
TriangulationQuadrature<D>::TriangulationQuadrature( memory::vptr<Triangulation<D>> triangulation,
                                                     memory::vptr<TriangleCellAssociation<D>> celldata,
                                                     size_t degree ) :
    triangulation_ { std::move( triangulation ) }, celldata_ { std::move( celldata ) }
{ 
    auto quadratureCache = QuadraturePointCache { };

    //triangleTrapezoidalRule( rs_, weights_ );
    simplexQuadrature( array::make<2>( degree + 1 ), rs_, weights_, quadratureCache );
}

template<size_t D>
void TriangulationQuadrature<D>::distribute( const MeshMapping<D>& mapping,
                                             CoordinateList<D>& rst,
                                             CoordinateList<D>& normals,
                                             std::vector<double>& weights,
                                             std::any& ) const
{ 
    auto begin = celldata_->offsets[mapping.icell];
    auto end = celldata_->offsets[mapping.icell + 1];

    auto rsize = rst.size( );
    auto wsize = weights.size( );
    auto nsize = normals.size( );

    auto npoints = rs_.size( ) * ( end - begin );

    rst.resize( rsize + npoints );
    weights.resize( wsize + npoints );
    normals.resize( nsize + npoints );

    auto bounds = mesh::boundingBox( mapping );
    auto reference = array::maxElement( bounds[1] - bounds[0] );

    for( size_t itriangle = begin; itriangle < end; ++itriangle )
    {
        auto [i0, i1, i2] = triangulation_->triangleIndices( itriangle );

        auto triangle = TriangleMapping<D> { celldata_->rst[i0], 
                                                celldata_->rst[i1], 
                                                celldata_->rst[i2] };

        auto normal = spatial::triangleCross( triangulation_->vertices[i0],
                                                triangulation_->vertices[i1],
                                                triangulation_->vertices[i2] );

        if( auto norm = spatial::norm( normal ); norm > 1e-10 * reference )
        {
            normal = normal / norm;
        }
        else
        {
            normal = array::make<D>( 0.0 );
        }
            
        auto localArea = spatial::triangleArea( celldata_->rst[i0],
                                                celldata_->rst[i1],
                                                celldata_->rst[i2] );

        if( localArea < 1e-8 )
        {
            //std::cout << "Rejecting local" << std::endl;

            continue;
        }

        for( size_t ipoint = 0; ipoint < rs_.size( ); ++ipoint )
        {
            auto [coords, J0] = map::withJ( triangle, rs_[ipoint] );
            auto [xyz, J1] = map::withJ( mapping, coords );

            auto J = spatial::concatenateJacobians<D, D, D - 1>( J0, J1 );
            auto detJ = spatial::computeDeterminant<D, D - 1>( J );
                
            auto index = ( itriangle - begin ) * rs_.size( ) + ipoint;

            rst[rsize + index] = coords;
            weights[wsize + index] = weights_[ipoint] * detJ;

            normals[nsize + index] = normal;
        }
    } 

}

namespace
{

template<size_t D>
auto internalFilterTriangulation( const Triangulation<D>& triangulation,
                                  const ImplicitFunction<D>& function,
                                  size_t nseedpoints )
{
    // Compute masks
    auto ntriangles = triangulation.ntriangles( );
    auto vertexMask = std::vector<std::uint8_t>( triangulation.nvertices( ), false );
    auto triangleMask = std::vector<std::uint8_t>( ntriangles, false );

    for( size_t itriangle = 0; itriangle < ntriangles; ++itriangle )
    {
        auto rstGenerator = spatial::makeGridPointGenerator<2>( array::make<2>( nseedpoints ), array::make<2>( 1.0 ), { } );
        auto [v0, v1, v2] = triangulation.triangleVertices( itriangle );

        auto mapping = TriangleMapping<D> { v0, v1, v2 };
        auto count = size_t { 0 };
        
        nd::executeTriangularBoundary<2>( nseedpoints, [&]( std::array<size_t, 2> ijk )
        {
            count += function( mapping( rstGenerator( ijk ) ) );
        } );

        if( count == ( nseedpoints * ( nseedpoints + 1 ) ) / 2 )
        {
            triangleMask[itriangle] = true;

            for( size_t ivertex = 0; ivertex < 3; ++ivertex )
            {
                vertexMask[triangulation.triangles[itriangle][ivertex]] = true;
            }
        }
    }

    // Construct filtered triangulation
    auto vertexForwardMap = algorithm::forwardIndexMap<size_t>( vertexMask );
    auto vertexBackwardMap = algorithm::backwardIndexMap<size_t>( std::move( vertexMask ) );
    auto triangleForwardMap = algorithm::forwardIndexMap<size_t>( std::move( triangleMask ) );

    auto filtered = Triangulation<D> { };

    filtered.vertices.resize( vertexForwardMap.size( ) );
    filtered.triangles.resize( triangleForwardMap.size( ) );

    for( size_t ivertex = 0; ivertex < vertexForwardMap.size( ); ++ivertex )
    {
        filtered.vertices[ivertex] = triangulation.vertices[vertexForwardMap[ivertex]];
    }

    for( size_t itriangle = 0; itriangle < triangleForwardMap.size( ); ++itriangle )
    {
        filtered.triangles[itriangle] = triangulation.triangles[triangleForwardMap[itriangle]];

        for( size_t ivertex = 0; ivertex < 3; ++ivertex )
        {
            filtered.triangles[itriangle][ivertex] = vertexBackwardMap[filtered.triangles[itriangle][ivertex]];
        }
    }

    return std::tuple { std::move( filtered ), std::move( vertexForwardMap ), std::move( triangleMask ) };
}

} // namespace

template<size_t D>
Triangulation<D> filterTriangulation( const Triangulation<D>& triangulation,
                                      const ImplicitFunction<D>& function,
                                      size_t nseedpoints )
{
    return std::get<0>( internalFilterTriangulation( triangulation, function, nseedpoints ) );
}

template<size_t D> MLHP_EXPORT
CellAssociatedTriangulation<D> filterTriangulation( const Triangulation<D>& triangulation,
                                                    const TriangleCellAssociation<D>& celldata,
                                                    const ImplicitFunction<D>& function,
                                                    size_t nseedpoints )
{
    MLHP_CHECK( !celldata.offsets.empty( ), "Empty offset vector." );

    auto [filteredTriangulation, vertexMap, triangleMask] = 
        internalFilterTriangulation( triangulation, function, nseedpoints );

    auto filteredCelldata = TriangleCellAssociation<D> { };
    auto nvertices = filteredTriangulation.vertices.size( );
    auto ncells = celldata.offsets.size( ) - 1;

    filteredCelldata.rst.resize( nvertices );
    filteredCelldata.offsets.resize( ncells + 1 );
    filteredCelldata.offsets[0] = 0;

    for( size_t ivertex = 0; ivertex < nvertices; ++ivertex )
    {
        filteredCelldata.rst[ivertex] = celldata.rst[vertexMap[ivertex]];
    }

    for( auto icell = size_t { 0 }; icell < ncells; ++icell )
    {
        auto ntriangles = std::accumulate( utilities::begin( triangleMask, celldata.offsets[icell] ),
                                           utilities::begin( triangleMask, celldata.offsets[icell + 1] ),
                                           size_t { 0 } );

        filteredCelldata.offsets[icell + 1] = filteredCelldata.offsets[icell] + ntriangles;
    }

    return std::pair { std::move( filteredTriangulation ), std::move( filteredCelldata ) };
}

template<size_t D>
KdTree<D> buildKdTree( const Triangulation<D>& triangulation,
                       const spatial::BoundingBox<D>& bounds,
                       const kdtree::Parameters& parameters )
{
    return buildKdTree( kdtree::makeTriangleProvider( triangulation ), bounds, parameters );
}

template<size_t D>
KdTree<D> buildKdTree( const Triangulation<D>& triangulation,
                       const kdtree::Parameters& parameters )
{
    auto bounds = triangulation.boundingBox( );

    return buildKdTree( triangulation, bounds, parameters );
}

namespace kdtree
{

template<size_t D> MLHP_EXPORT
kdtree::ObjectProvider<D> makeTriangleProvider( const Triangulation<D>& triangulation, bool clip )
{
    if( clip )
    {
        std::function provider = [&triangulation]( size_t itriangle, const spatial::BoundingBox<D>& box )
        {
            auto vertices = triangulation.triangleVertices( itriangle );
        
            auto bounds = spatial::triangleClippedBoundingBox( vertices[0], vertices[1], vertices[2], box );

            return spatial::boundingBoxAnd( bounds, box );
        };

        return utilities::makeIndexRangeFunction( triangulation.ntriangles( ), provider );
    }
    else
    {
        std::function provider = [&triangulation]( size_t itriangle, const spatial::BoundingBox<D>& box )
        {
            auto bounds = spatial::boundingBox<D>( triangulation.triangleVertices( itriangle ) );

            return spatial::boundingBoxAnd<D>( bounds, box );
        };

        return utilities::makeIndexRangeFunction( triangulation.ntriangles( ), provider );
    }

}

} // kdtree

Triangulation<3> marchingCubes( const ImplicitFunction<3>& function,
                                std::array<size_t, 3> ncells,
                                std::array<double, 3> lengths,
                                std::array<double, 3> origin )
{
    auto triangulation = Triangulation<3> { };
    auto dx = std::array<double, 3> { };

    for( size_t axis = 0; axis < 3; ++axis )
    {
        dx[axis] = lengths[axis] / ncells[axis];
    }

    nd::execute( ncells, [&]( std::array<size_t, 3> ijkCell )
    { 
        auto vertices = std::array<std::array<double, 3>, 8> { };
        auto index = std::uint8_t { 0 };
        
        nd::executeWithIndex( array::makeSizes<3>( 2 ), [&]( std::array<size_t, 3> ijkPoint, size_t linearIndex )
        {
            vertices[linearIndex][0] = ( ijkCell[0] + ijkPoint[0] ) * dx[0] + origin[0];
            vertices[linearIndex][1] = ( ijkCell[1] + ijkPoint[1] ) * dx[1] + origin[1];
            vertices[linearIndex][2] = ( ijkCell[2] + ijkPoint[2] ) * dx[2] + origin[2];
            
            index |= function( vertices[linearIndex] ) * utilities::binaryPow<std::uint8_t>( linearIndex );
        } );
        
        for( auto itriangle = triangleIndices[index]; itriangle < triangleIndices[index + 1]; ++itriangle )
        {
            triangulation.triangles.push_back( { } );

            for( size_t ivertex = 0; ivertex < 3; ++ivertex )
            {
                auto edgeId = triangleData[3 * itriangle + ivertex];
                auto nodeIds = std::array { numbering[edgeId][0], numbering[edgeId][1] };
        
                auto value0 = index & utilities::binaryPow<std::uint8_t>( nodeIds[0] );
                auto value1 = index & utilities::binaryPow<std::uint8_t>( nodeIds[1] );
        
                auto vertex = interpolate( function, vertices[nodeIds[0]], value0, vertices[nodeIds[1]], value1 );
                
                triangulation.triangles.back( )[ivertex] = triangulation.vertices.size( );
                triangulation.vertices.push_back( vertex );
            }
        }
    } );

    return triangulation;
}

template<MarchingCubesIndex Index>
struct SmallMarchingCubes
{
    static constexpr Index NoVertex = std::numeric_limits<Index>::max( );
	
    std::array<size_t, 3> ncells;
    std::array<size_t, 3> npoints;
    std::array<size_t, 4> edgeOffset;
    std::array<size_t, 3> cornerStrides;
    std::array<std::array<size_t, 3>, 3> edgeStrides;

    std::vector<Index> vertexMap;

    CoordinateList<3>* xyz;

    void reset( std::array<size_t, 3> resolution, 
                CoordinateList<3>* coordinateList )
    {
        xyz = coordinateList;

        bool rebuild = resolution != ncells || resolution == array::makeSizes<3>( 0 );

        if( rebuild  )
        {
            ncells = resolution;
            npoints = array::add( ncells, size_t{ 1 } );

            cornerStrides = nd::stridesFor( npoints );
            
            edgeStrides = { nd::stridesFor( std::array { ncells[0], npoints[1], npoints[2] } ),
                            nd::stridesFor( std::array { npoints[0], ncells[1], npoints[2] } ),
                            nd::stridesFor( std::array { npoints[0], npoints[1], ncells[2] } ) };
            
            edgeOffset[0] = array::product( npoints );
            edgeOffset[1] = edgeOffset[0] + ncells[0] * npoints[1] * npoints[2];
            edgeOffset[2] = edgeOffset[1] + npoints[0] * ncells[1] * npoints[2];
            edgeOffset[3] = edgeOffset[2] + npoints[0] * npoints[1] * ncells[2];
        }

        vertexMap.resize( edgeOffset.back( ) );
    
        std::fill( vertexMap.begin( ), vertexMap.end( ), NoVertex );
    }
    
    template<typename Create>
    Index vertexIndex( std::array<size_t, 3> ijk, Create&& create ) 
    { 
        auto index = nd::linearIndex( ijk, cornerStrides );

        if( vertexMap[index] == NoVertex )
        {
            vertexMap[index] = static_cast<Index>( xyz->size( ) );

            xyz->push_back( create( ijk ) );
        }

        return vertexMap[index];
    }

    template<typename Create>
    Index edgeIndex( std::array<size_t, 3> ijk0, std::array<size_t, 3> ijk1, Create&& create ) 
    { 
        auto axis = ijk0[0] != ijk1[0] ? size_t{ 0 } : (ijk0[1] != ijk1[1] ? size_t{ 1 } : size_t{ 2 } );
        auto ijk = array::setEntry( ijk0, axis, std::min( ijk0[axis], ijk1[axis] ) );
        auto index = nd::linearIndex( ijk, edgeStrides[axis] ) + edgeOffset[axis];

        if( vertexMap[index] == NoVertex )
        {
            vertexMap[index] = static_cast<Index>( xyz->size( ) );
                
            xyz->push_back( create( ijk0, ijk1 ) );
        }

        return vertexMap[index];
    }
};

template<MarchingCubesIndex IndexType>
void marchingCubesVolume( const AbsMapping<3>& mapping,
                          const ImplicitFunction<3>& function,
                          const std::vector<bool>& evaluations,
                          const CoordinateGrid<3>& rstGrid,
                          std::array<size_t, 3> resolution,
                          CoordinateList<3>& rstList,
                          std::vector<IndexType>& connectivity,
                          std::vector<IndexType>& offsets,
                          bool meshBothSides,
                          std::any& anyCache )
{
    if( !anyCache.has_value( ) )
    {
        anyCache = SmallMarchingCubes<IndexType> { };
    }

    // Prepare vertex map that reduces Cartesian indices to the existing ones
    auto& vertexMap = std::any_cast<SmallMarchingCubes<IndexType>&>( anyCache );

    vertexMap.reset( resolution, &rstList );

    auto strides = vertexMap.cornerStrides;
        
    // Get cell ijk + local vertex index and return local vertex ijk
    auto vertexIjk = [=]( auto ijkCell, size_t index ) 
    { 
        return array::add( ijkCell, nd::binaryUnravel<size_t, 3>( index ) ); 
    };

    // Callback function for creating a vertex with given global vertex ijk
    auto createCorner = [&]( std::array<size_t, 3> ijk )
    { 
        return array::extract( rstGrid, ijk ); 
    };

    // Callback function for creating an edge between two vertices with given global vertex ijk
    auto createEdge = [&]( std::array<size_t, 3> ijk0, std::array<size_t, 3> ijk1 ) 
    {
        return marchingcubes::interpolate( function, mapping,
            array::extract( rstGrid, ijk0 ), evaluations[nd::linearIndex( ijk0, strides )],
            array::extract( rstGrid, ijk1 ), evaluations[nd::linearIndex( ijk1, strides )] ); 
    };

    // Create all tests in cell with given cell ijk. The bits of cutConfig store the inside-outside state of the corners.
    auto createTets = [&]( auto ijkCell, std::uint8_t cutConfiguration )
    {
        for( size_t itet = 0; itet < marchingcubes::tetrahedra[cutConfiguration].size( ) / 4; ++itet )
        {
            for( size_t ivertex = 0; ivertex < 4; ++ivertex )
            {
                if( auto id = marchingcubes::tetrahedra[cutConfiguration][4 * itet + ivertex]; id >= 8 )
                {
                    auto localVertexIndex1 = vertexIjk( ijkCell, marchingcubes::numbering[id - 8][0] );
                    auto localVertexIndex2 = vertexIjk( ijkCell, marchingcubes::numbering[id - 8][1] );

                    connectivity.push_back( vertexMap.edgeIndex( localVertexIndex1, localVertexIndex2, createEdge ) );
                }
                else
                {
                    connectivity.push_back( vertexMap.vertexIndex( vertexIjk( ijkCell, id ), createCorner ) );
                }
            }
                
            offsets.push_back( static_cast<IndexType>( connectivity.size( ) ) );
        }
    };

    // Loop over cell grid
    nd::execute( resolution, [&]( std::array<size_t, 3> ijkCell )
    {
        auto index = std::uint8_t { 0 };
    
        for( size_t ivertex = 0; ivertex < 8; ++ivertex )
        {
            auto linearIndex = nd::linearIndex( vertexIjk( ijkCell, ivertex ), strides );

            index |= evaluations[linearIndex] * utilities::binaryPow<std::uint8_t>( ivertex );
        }

        if( index == 255 || ( meshBothSides && index == 0 ) )
        {
            for( size_t ivertex = 0; ivertex < 8; ++ivertex )
            {
                connectivity.push_back( vertexMap.vertexIndex( vertexIjk( ijkCell, ivertex ), createCorner ) );
            }
        
            offsets.push_back( static_cast<IndexType>( connectivity.size( ) ) );
        }
        else
        {
            createTets( ijkCell, index );

            if( meshBothSides )
            {
                createTets( ijkCell, 255 - index );
            }
        }
    } );
}

namespace marchingcubes
{

void evaluateGrid( const AbsMapping<3>& mapping,
                   const ImplicitFunction<3>& function,
                   std::array<size_t, 3> resolution,
                   std::array<std::vector<double>, 3>& rstGrid,
                   std::vector<bool>& evaluations )
{
    spatial::cartesianTickVectors( resolution, { 2.0, 2.0, 2.0 }, { -1.0, -1.0, -1.0 }, rstGrid );

    auto npoints = array::add<size_t, 3>( resolution, 1 );

    evaluations.resize( array::product( npoints ) );

    nd::executeWithIndex( npoints, [&]( std::array<size_t, 3> ijk, size_t index )
    { 
        evaluations[index] = function( mapping.map( array::extract( rstGrid, ijk ) ) );
    } );
}

} // marchingcubes

template<MarchingCubesIndex IndexType>
void marchingCubesBoundary( const AbsMapping<3>& mapping,
                            const ImplicitFunction<3>& function,
                            const std::vector<bool>& evaluations,
                            const CoordinateGrid<3>& rstGrid,
                            std::array<size_t, 3> resolution,
                            CoordinateList<3>& rstList,
                            std::vector<IndexType>& triangles,
                            std::any& anyCache )
{
    if( !anyCache.has_value( ) )
    {
        anyCache = SmallMarchingCubes<IndexType> { };
    }

    // Prepare vertex map that reduces Cartesian indices to the existing ones
    auto& vertexMap = std::any_cast<SmallMarchingCubes<IndexType>&>( anyCache );

    vertexMap.reset( resolution, &rstList );

    auto strides = vertexMap.cornerStrides;

    // Create marching cubes
    nd::execute( resolution, [&]( std::array<size_t, 3> ijkCell )
    {
        auto vertexIjk = [=]( size_t index ) { return array::add( ijkCell, nd::binaryUnravel<size_t, 3>( index ) ); };
        auto index = std::uint8_t { 0 };
    
        for( size_t ivertex = 0; ivertex < 8; ++ivertex )
        {
            auto linearIndex = nd::linearIndex( vertexIjk( ivertex ), strides );

            index |= evaluations[linearIndex] * utilities::binaryPow<std::uint8_t>( ivertex );
        }
    
        auto createEdge = [&]( std::array<size_t, 3> ijk0, std::array<size_t, 3> ijk1 ) {
            return marchingcubes::interpolate( function, mapping,
                array::extract( rstGrid, ijk0 ), evaluations[nd::linearIndex( ijk0, strides )],
                array::extract( rstGrid, ijk1 ), evaluations[nd::linearIndex( ijk1, strides )] ); };

   
        auto begin = marchingcubes::triangleIndices[index];
        auto end = marchingcubes::triangleIndices[index + 1];

        for( auto itriangle = begin; itriangle < end; ++itriangle )
        {
            for( size_t iedge = 0; iedge < 3; ++iedge )
            {
                auto id = marchingcubes::triangleData[3 * itriangle + iedge];

                triangles.push_back( vertexMap.edgeIndex( 
                    vertexIjk( marchingcubes::numbering[id][0] ),
                    vertexIjk( marchingcubes::numbering[id][1] ), createEdge ) );
            }
        }
    } );
}

#define MLHP_INSTANTIATE_MARCHING_CUBES( INDEX_TYPE )                 \
                                                                      \
    template MLHP_EXPORT                                              \
    void marchingCubesVolume( const AbsMapping<3>& mapping,           \
                              const ImplicitFunction<3>& function,    \
                              const std::vector<bool>& evaluations,   \
                              const CoordinateGrid<3>& rstGrid,       \
                              std::array<size_t, 3> resolution,       \
                              CoordinateList<3>& rstList,             \
                              std::vector<INDEX_TYPE>& connectivity,  \
                              std::vector<INDEX_TYPE>& offsets,       \
                              bool meshBothSides,                     \
                              std::any& anyCache );                   \
                                                                      \
    template MLHP_EXPORT                                              \
    void marchingCubesBoundary( const AbsMapping<3>& mapping,         \
                                const ImplicitFunction<3>& function,  \
                                const std::vector<bool>& evaluations, \
                                const CoordinateGrid<3>& rstGrid,     \
                                std::array<size_t, 3> resolution,     \
                                CoordinateList<3>& rstList,           \
                                std::vector<INDEX_TYPE>& triangles,   \
                                std::any& anyCache )

MLHP_INSTANTIATE_MARCHING_CUBES( size_t );
MLHP_INSTANTIATE_MARCHING_CUBES( std::int64_t );

template class TriangulationQuadrature<3>;

#define MLHP_INSTANTIATE_DIM( D )                                                              \
                                                                                               \
    template struct Triangulation<D>;                                                          \
    template struct TriangleCellAssociation<D>;                                                \
                                                                                               \
    namespace kdtree                                                                           \
    {                                                                                          \
        template MLHP_EXPORT                                                                   \
        kdtree::ObjectProvider<D> makeTriangleProvider( const Triangulation<D>& triangles,     \
                                                        bool clip );                           \
    }                                                                                          \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    KdTree<D> buildKdTree( const Triangulation<D>& triangulation,                              \
                           const kdtree::Parameters& parameters );                             \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    KdTree<D> buildKdTree( const Triangulation<D>& triangulation,                              \
                           const spatial::BoundingBox<D>& bounds,                              \
                           const kdtree::Parameters& parameters );                             \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    Triangulation<D> createTriangulation( CoordinateConstSpan<D> vertices );                   \
                                                                                               \
    template MLHP_EXPORT                                                                       \
    Triangulation<D> filterTriangulation( const Triangulation<D>& triangulation,               \
                                          const ImplicitFunction<D>& function,                 \
                                          size_t nseedpoints );                                \
    template MLHP_EXPORT                                                                       \
    CellAssociatedTriangulation<D> filterTriangulation( const Triangulation<D>& triangulation, \
                                                        const TriangleCellAssociation<D>&,     \
                                                        const ImplicitFunction<D>& function,   \
                                                        size_t nseedpoints );


MLHP_DIMENSIONS_XMACRO_LIST
#undef MLHP_INSTANTIATE_DIM


//CellAssociatedTriangles marchingCubes( const ImplicitFunction<3>& function,
//                                       const AbsMapping<3>& mapping,
//                                       std::array<size_t, 3> ncells,
//                                       std::vector<std::array<double, 3>>& local,
//                                       std::vector<std::array<double, 3>>& global,
//                                       std::vector<std::int64_t>& connectivity,
//                                       std::vector<std::int64_t>& offsets,
//                                       std::vector<double>& values )
//{
//    // Prepare marching cubes grid
//    auto npoints = array::add<size_t, 3>( ncells, 1 );
//    
//    local.resize( array::product( npoints ) );
//    global.resize( local.size( ) );
//    values.resize( local.size( ) );
//    
//    auto dx = std::array<double, 3> { };
//    
//    for( size_t axis = 0; axis < 3; ++axis )
//    {
//        dx[axis] = 2.0 / ncells[axis];
//    }
//    
//    nd::executeWithIndex( npoints, [&]( std::array<size_t, 3> ijk, size_t index )
//    { 
//        for( size_t axis = 0; axis < 3; ++axis )
//        {
//            local[index][axis] = ijk[axis] * dx[axis] - 1.0;
//        }
//    
//        global[index] = mapping.map( local[index] );
//        values[index] = function( global[index] );
//    } );
//    
//    // Create triangles
//    nd::execute( ncells, [&]( std::array<size_t, 3> ijkCell )
//    {
//        auto vertexIndices = std::array<size_t, 8> { };
//        auto strides = nd::stridesFor( npoints );
//        auto index = std::uint8_t { 0 };
//    
//        nd::executeWithIndex( array::make<size_t, 3>( 2 ), [&]( std::array<size_t, 3> ijkVertex, size_t ivertex )
//        { 
//            vertexIndices[ivertex] = nd::linearIndex( array::add( ijkCell, ijkVertex ), strides );
//            index |= values[vertexIndices[ivertex]] * utilities::binaryPow<std::uint8_t>( ivertex );
//        } );
//    
//        for( auto itriangle = triangleIndices[index]; itriangle < triangleIndices[index + 1]; ++itriangle )
//        {
//            for( size_t ivertex = 0; ivertex < 3; ++ivertex )
//            {
//                auto edgeId = triangleData[3 * itriangle + ivertex];
//                auto nodeIds1 = std::array { numbering[edgeId][0], numbering[edgeId][1] };
//                auto nodeIds2 = std::array { vertexIndices[nodeIds1[0]], vertexIndices[nodeIds1[1]] };
//        
//                auto value0 = index & utilities::binaryPow<std::uint8_t>( nodeIds1[0] );
//                auto value1 = index & utilities::binaryPow<std::uint8_t>( nodeIds1[1] );
//        
//                auto vertex = interpolate( function, global[nodeIds2[0]], value0, global[nodeIds2[1]], value1 );
//                
//                for( size_t axis = 0; axis < 3; ++axis )
//                {
//                    triangles.first.push_back( vertex[axis] );
//                }
//            }
//
//            triangles.second.push_back( icell );
//        }
//    } );
//
//    return { };
//}

//CellAssociatedTriangles marchingCubes( const ImplicitFunction<3>& function,
//                                       const AbsMesh<3>& mesh, 
//                                       size_t ncellsPerDirection )
//{
//    auto ncells = mesh.ncells( );
//    auto result = CellAssociatedTriangles { };
//
//    #pragma omp parallel
//    {
//        auto local = std::vector<std::array<double, 3>> { };
//        auto global = std::vector<std::array<double, 3>> { };
//        auto values = std::vector<bool> { };
//        auto mapping = mesh.createMapping( );
//        auto triangles = CellAssociatedTriangles { };
//
//        #pragma omp for
//        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( ncells ); ++ii )
//        {
//            auto icell = static_cast<CellIndex>( ii );
//
//            // Prepare marching cubes grid
//            auto resolution = array::make<size_t, 3>( ncellsPerDirection );
//            auto npoints = array::make<size_t, 3>( ncellsPerDirection + 1 );
//        
//            local.resize( array::product( npoints ) );
//            global.resize( local.size( ) );
//            values.resize( local.size( ) );
//        
//            auto dx = std::array<double, 3> { };
//        
//            for( size_t axis = 0; axis < 3; ++axis )
//            {
//                dx[axis] = 2.0 / resolution[axis];
//            }
//        
//            mesh.prepareMapping( icell, *mapping );
//        
//            nd::executeWithIndex( npoints, [&]( std::array<size_t, 3> ijk, size_t index )
//            { 
//                for( size_t axis = 0; axis < 3; ++axis )
//                {
//                    local[index][axis] = ijk[axis] * dx[axis] - 1.0;
//                }
//        
//                global[index] = mapping->map( local[index] );
//                values[index] = function( global[index] );
//            } );
//        
//            // Create triangles
//            nd::execute( resolution, [&]( std::array<size_t, 3> ijkCell )
//            {
//                auto vertexIndices = std::array<size_t, 8> { };
//                auto strides = nd::stridesFor( npoints );
//                auto index = std::uint8_t { 0 };
//        
//                nd::executeWithIndex( array::make<size_t, 3>( 2 ), [&]( std::array<size_t, 3> ijkVertex, size_t ivertex )
//                { 
//                    vertexIndices[ivertex] = nd::linearIndex( array::add( ijkCell, ijkVertex ), strides );
//                    index |= values[vertexIndices[ivertex]] * utilities::binaryPow<std::uint8_t>( ivertex );
//                } );
//        
//                for( auto itriangle = triangleIndices[index]; itriangle < triangleIndices[index + 1]; ++itriangle )
//                {
//                    for( size_t ivertex = 0; ivertex < 3; ++ivertex )
//                    {
//                        auto edgeId = triangleData[3 * itriangle + ivertex];
//                        auto nodeIds1 = std::array { numbering[edgeId][0], numbering[edgeId][1] };
//                        auto nodeIds2 = std::array { vertexIndices[nodeIds1[0]], vertexIndices[nodeIds1[1]] };
//                
//                        auto value0 = index & utilities::binaryPow<std::uint8_t>( nodeIds1[0] );
//                        auto value1 = index & utilities::binaryPow<std::uint8_t>( nodeIds1[1] );
//                
//                        auto vertex = interpolate( function, global[nodeIds2[0]], value0, global[nodeIds2[1]], value1 );
//                        
//                        for( size_t axis = 0; axis < 3; ++axis )
//                        {
//                            triangles.first.push_back( vertex[axis] );
//                        }
//                    }
//
//                    triangles.second.push_back( icell );
//                }
//            } );
//        }
//
//        #pragma omp critical
//        {
//            result.first.insert( result.first.end( ), triangles.first.begin( ), triangles.first.end( ) );
//            result.second.insert( result.second.end( ), triangles.second.begin( ), triangles.second.end( ) );
//        }
//
//    } // omp parallel
//
//    return result;
//}

CellAssociatedTriangulation<3> marchingCubesBoundary( const AbsMesh<3>& mesh,
                                                      const ImplicitFunction<3>& function,
                                                      std::array<size_t, 3> resolution )
{
    static constexpr size_t D = 3;

    auto triangulation = Triangulation<3> { };
    auto celldata = TriangleCellAssociation<3> { };
    auto vertexOffsets = std::vector<size_t>( mesh.ncells( ) + 1, 0 );

    celldata.offsets.resize( mesh.ncells( ) + 1, 0 );

    #pragma omp parallel
    {
        auto rstGrid = CoordinateGrid<D> { };
        auto evaluations = std::vector<bool> { };
        auto mapping = mesh.createMapping( );
        auto cache = std::any { };

        auto localCells = std::vector<CellIndex> { };
        auto localRst = CoordinateList<D> { };
        auto localXyz = CoordinateList<D> { };
        auto localTriangles = std::vector<size_t> { };

        #pragma omp for schedule( dynamic, 10 )
        for( std::int64_t ii = 0; ii < static_cast<std::int64_t>( mesh.ncells( ) ); ++ii )
        {
            utilities::resize0( rstGrid, evaluations );

            auto icell = static_cast<CellIndex>( ii );

            mesh.prepareMapping( icell, mapping );
            
            marchingcubes::evaluateGrid( mapping, function, 
                resolution, rstGrid, evaluations );
   
            auto nvertices0 = localRst.size( );
            auto ntriangles0 = localTriangles.size( ) / 3;

            marchingCubesBoundary( mapping, function, evaluations, 
                rstGrid, resolution, localRst, localTriangles, cache );

            celldata.offsets[icell + 1] = localTriangles.size( ) / 3 - ntriangles0;
            vertexOffsets[icell + 1] = localRst.size( ) - nvertices0;

            if( celldata.offsets[icell + 1] )
            {
                localCells.push_back( icell );
                localXyz.resize( localRst.size( ) );

                for( auto ivertex = nvertices0; ivertex < localRst.size( ); ++ivertex )
                {
                    localXyz[ivertex] = mapping( localRst[ivertex] );
                }

                for( auto ivertex = 3 * ntriangles0; ivertex < localTriangles.size( ); ++ivertex )
                {
                    localTriangles[ivertex] -= nvertices0;
                }
            }
        }

        #pragma omp barrier 
        { }

        #pragma omp single
        {
            std::partial_sum( celldata.offsets.begin( ), celldata.offsets.end( ), celldata.offsets.begin( ) );
            std::partial_sum( vertexOffsets.begin( ), vertexOffsets.end( ), vertexOffsets.begin( ) );

            celldata.rst.resize( vertexOffsets.back( ) );
            triangulation.vertices.resize( vertexOffsets.back( ) );
            triangulation.triangles.resize( celldata.offsets.back( ) );
        }

        auto vertexOffset = size_t { 0 };
        auto triangleOffset = size_t { 0 };

        for( size_t ilocal = 0; ilocal < localCells.size( ); ++ilocal )
        {
            auto icell = localCells[ilocal];
            auto nvertices = vertexOffsets[icell + 1] - vertexOffsets[icell];
            auto ntriangles = celldata.offsets[icell + 1] - celldata.offsets[icell];

            std::copy( utilities::begin( localRst, vertexOffset ),
                       utilities::begin( localRst, vertexOffset + nvertices ),
                       utilities::begin( celldata.rst, vertexOffsets[icell] ) );

            std::copy( utilities::begin( localXyz, vertexOffset ),
                       utilities::begin( localXyz, vertexOffset + nvertices ),
                       utilities::begin( triangulation.vertices, vertexOffsets[icell] ) );

            auto triangles = std::span( utilities::begin( triangulation.triangles, celldata.offsets[icell] ), ntriangles );

            for( size_t itriangle = 0; itriangle < ntriangles; ++itriangle )
            {
                for( size_t ivertex = 0; ivertex < 3; ++ivertex )
                {
                    auto index = 3 * ( triangleOffset + itriangle ) + ivertex;

                    triangles[itriangle][ivertex] = localTriangles[index] + vertexOffsets[icell];
                }
            }

            vertexOffset += nvertices;
            triangleOffset += ntriangles;
        }
    } // omp parallel

    return std::pair { std::move( triangulation ), std::move( celldata ) };
}

struct MarchingCubesCache
{
    std::array<std::unordered_map<size_t, size_t>, 3> edgeMaps;
    std::unordered_map<size_t, size_t> vertexMap;
};



//      8: { 0, 4 },
//      9: { 4, 6 },
//     10: { 6, 2 },
//     11: { 2, 0 },
//     12: { 1, 5 },
//     13: { 5, 7 },
//     14: { 7, 3 },
//     15: { 3, 1 },
//     16: { 0, 1 },
//     17: { 4, 5 },
//     18: { 6, 7 },
//     19: { 2, 3 }   


// void printBinary( auto number, size_t length, std::string before )
// {
//     std::cout << before << " = ";
//     for( size_t i = 0; i < length; ++i )
//     {
//         std::cout << (( number & utilities::binaryPow<decltype(number)>( i ) ) > 0);
//     }
//     std::cout << std::endl;
// }

// http://www.paulbourke.net/geometry/polygonise/
// https://gist.github.com/dwilliamson/c041e3454a713e58baf6e4f8e5fffecd

namespace marchingcubes
{

std::array<std::array<size_t, 2>, 12> numbering = 
{
    std::array<size_t, 2>{ 0, 4 },
    std::array<size_t, 2>{ 4, 6 },
    std::array<size_t, 2>{ 6, 2 },
    std::array<size_t, 2>{ 2, 0 },
    std::array<size_t, 2>{ 1, 5 },
    std::array<size_t, 2>{ 5, 7 },
    std::array<size_t, 2>{ 7, 3 },
    std::array<size_t, 2>{ 3, 1 },
    std::array<size_t, 2>{ 0, 1 },
    std::array<size_t, 2>{ 4, 5 },
    std::array<size_t, 2>{ 6, 7 },
    std::array<size_t, 2>{ 2, 3 }
};

namespace
{

auto interpolateImpl( auto&& function,
                      std::array<double, 3> c1, bool v1, 
                      std::array<double, 3> c2, bool v2 )
{
    static constexpr size_t D = 3;

    if( !v1 )
    {
        std::swap( c1, c2 );
        std::swap( v1, v2 );
    }

    std::array<double, D> m;

    for( size_t it = 0; it < 12; ++it )
    {
        for( size_t axis = 0; axis < D; ++axis )
        {
            m[axis] = 0.5 * ( c1[axis] + c2[axis] );
        }

        if( function( m ) == v1 )
        {
            c1 = m;
        }
        else
        {
            c2 = m;
        }
    }

    // Return point inside (may not be the closest)
    return c1;
}

} // namespace detail

std::array<double, 3> interpolate( const ImplicitFunction<3>& function,
                                   const AbsMapping<3>& mapping,
                                   std::array<double, 3> c1, bool v1,
                                   std::array<double, 3> c2, bool v2 )
{
    return interpolateImpl( [&]( std::array<double, 3> rst ) { 
        return function( mapping.map( rst ) ); }, c1, v1, c2, v2 );
}

std::array<double, 3> interpolate( const ImplicitFunction<3>& function,
                                   std::array<double, 3> c1, bool v1,
                                   std::array<double, 3> c2, bool v2 )
{
    return interpolateImpl( function, c1, v1, c2, v2 );
}

std::array<std::uint8_t, 2460> triangleData =
{ 
                                                      //   0: 00000000
    0, 8, 3,                                          //   1: 00000001 
    4, 7, 8,                                          //   2: 00000010
    4, 3, 0, 7, 3, 4,                                 //   3: 00000011
    3, 11, 2,                                         //   4: 00000100 
    0, 11, 2, 8, 11, 0,                               //   5: 00000101 
    8, 4, 7, 3, 11, 2,                                //   6: 00000110 
    11, 4, 7, 11, 2, 4, 2, 0, 4,                      //   7: 00000111 
    7, 6, 11,                                         //   8: 00001000 
    3, 0, 8, 11, 7, 6,                                //   9: 00001001 
    6, 8, 4, 11, 8, 6,                                //  10: 00001010 
    3, 6, 11, 3, 0, 6, 0, 4, 6,                       //  11: 00001011 
    7, 2, 3, 6, 2, 7,                                 //  12: 00001100 
    7, 0, 8, 7, 6, 0, 6, 2, 0,                        //  13: 00001101 
    8, 2, 3, 8, 4, 2, 4, 6, 2,                        //  14: 00001110 
    0, 4, 2, 4, 6, 2,                                 //  15: 00001111 
    0, 1, 9,                                          //  16: 00010000 
    1, 8, 3, 9, 8, 1,                                 //  17: 00010001  
    0, 1, 9, 8, 4, 7,                                 //  18: 00010010 
    4, 1, 9, 4, 7, 1, 7, 3, 1,                        //  19: 00010011 
    1, 9, 0, 2, 3, 11,                                //  20: 00010100  
    1, 11, 2, 1, 9, 11, 9, 8, 11,                     //  21: 00010101  
    9, 0, 1, 8, 4, 7, 2, 3, 11,                       //  22: 00010110  
    4, 7, 11, 9, 4, 11, 9, 11, 2, 9, 2, 1,            //  23: 00010111  
    0, 1, 9, 11, 7, 6,                                //  24: 00011000  
    8, 1, 9, 8, 3, 1, 11, 7, 6,                       //  25: 00011001  
    8, 6, 11, 8, 4, 6, 9, 0, 1,                       //  26: 00011010  
    9, 4, 6, 9, 6, 3, 9, 3, 1, 11, 3, 6,              //  27: 00011011  
    2, 7, 6, 2, 3, 7, 0, 1, 9,                        //  28: 00011100  
    1, 6, 2, 1, 8, 6, 1, 9, 8, 8, 7, 6,               //  29: 00011101  
    1, 9, 0, 2, 3, 4, 2, 4, 6, 4, 3, 8,               //  30: 00011110  
    1, 9, 4, 1, 4, 2, 2, 4, 6,                        //  31: 00011111
    9, 5, 4,                                          //  32: 00100000  
    9, 5, 4, 0, 8, 3,                                 //  33: 00100001 
    9, 7, 8, 5, 7, 9,                                 //  34: 00100010 
    9, 3, 0, 9, 5, 3, 5, 7, 3,                        //  35: 00100011 
    9, 5, 4, 2, 3, 11,                                //  36: 00100100 
    0, 11, 2, 0, 8, 11, 4, 9, 5,                      //  37: 00100101 
    7, 9, 5, 7, 8, 9, 3, 11, 2,                       //  38: 00100110 
    9, 5, 7, 9, 7, 2, 9, 2, 0, 2, 7, 11,              //  39: 00100111 
    4, 9, 5, 7, 6, 11,                                //  40: 00101000 
    0, 8, 3, 4, 9, 5, 11, 7, 6,                       //  41: 00101001 
    6, 9, 5, 6, 11, 9, 11, 8, 9,                      //  42: 00101010 
    3, 6, 11, 0, 6, 3, 0, 5, 6, 0, 9, 5,              //  43: 00101011 
    7, 2, 3, 7, 6, 2, 5, 4, 9,                        //  44: 00101100 
    9, 5, 4, 0, 8, 6, 0, 6, 2, 6, 8, 7,               //  45: 00101101 
    5, 8, 9, 5, 2, 8, 5, 6, 2, 3, 8, 2,               //  46: 00101110 
    9, 5, 6, 9, 6, 0, 0, 6, 2,                        //  47: 00101111 
    0, 5, 4, 1, 5, 0,                                 //  48: 00110000 
    8, 5, 4, 8, 3, 5, 3, 1, 5,                        //  49: 00110001 
    0, 7, 8, 0, 1, 7, 1, 5, 7,                        //  50: 00110010 
    1, 5, 3, 3, 5, 7,                                 //  51: 00110011 
    0, 5, 4, 0, 1, 5, 2, 3, 11,                       //  52: 00110100 
    2, 1, 5, 2, 5, 8, 2, 8, 11, 4, 8, 5,              //  53: 00110101 
    2, 3, 11, 0, 1, 8, 1, 7, 8, 1, 5, 7,              //  54: 00110110 
    11, 2, 1, 11, 1, 7, 7, 1, 5,                      //  55: 00110111 
    5, 0, 1, 5, 4, 0, 7, 6, 11,                       //  56: 00111000 
    11, 7, 6, 8, 3, 4, 3, 5, 4, 3, 1, 5,              //  57: 00111001 
    0, 11, 8, 0, 5, 11, 0, 1, 5, 5, 6, 11,            //  58: 00111010 
    6, 11, 3, 6, 3, 5, 5, 3, 1,                       //  59: 00111011 
    3, 6, 2, 3, 7, 6, 1, 5, 0, 5, 4, 0,               //  60: 00111100 
    6, 2, 8, 6, 8, 7, 2, 1, 8, 4, 8, 5, 1, 5, 8,      //  61: 00111101 
    1, 5, 8, 1, 8, 0, 5, 6, 8, 3, 8, 2, 6, 2, 8,      //  62: 00111110 
    1, 5, 6, 2, 1, 6,                                 //  63: 00111111 
    1, 2, 10,                                         //  64: 01000000 
    0, 8, 3, 1, 2, 10,                                //  65: 01000001 
    1, 2, 10, 8, 4, 7,                                //  66: 01000010 
    3, 4, 7, 3, 0, 4, 1, 2, 10,                       //  67: 01000011 
    3, 10, 1, 11, 10, 3,                              //  68: 01000100 
    0, 10, 1, 0, 8, 10, 8, 11, 10,                    //  69: 01000101 
    3, 10, 1, 3, 11, 10, 7, 8, 4,                     //  70: 01000110 
    1, 11, 10, 1, 4, 11, 1, 0, 4, 7, 11, 4,           //  71: 01000111 
    10, 1, 2, 6, 11, 7,                               //  72: 01001000 
    1, 2, 10, 3, 0, 8, 6, 11, 7,                      //  73: 01001001 
    6, 8, 4, 6, 11, 8, 2, 10, 1,                      //  74: 01001010 
    1, 2, 10, 3, 0, 11, 0, 6, 11, 0, 4, 6,            //  75: 01001011 
    10, 7, 6, 10, 1, 7, 1, 3, 7,                      //  76: 01001100 
    10, 7, 6, 1, 7, 10, 1, 8, 7, 1, 0, 8,             //  77: 01001101 
    8, 1, 3, 8, 6, 1, 8, 4, 6, 6, 10, 1,              //  78: 01001110 
    10, 1, 0, 10, 0, 6, 6, 0, 4,                      //  79: 01001111 
    9, 2, 10, 0, 2, 9,                                //  80: 01010000 
    2, 8, 3, 2, 10, 8, 10, 9, 8,                      //  81: 01010001 
    9, 2, 10, 9, 0, 2, 8, 4, 7,                       //  82: 01010010 
    2, 10, 9, 2, 9, 7, 2, 7, 3, 7, 9, 4,              //  83: 01010011 
    3, 9, 0, 3, 11, 9, 11, 10, 9,                     //  84: 01010100 
    9, 8, 10, 10, 8, 11,                              //  85: 01010101 
    4, 7, 8, 9, 0, 11, 9, 11, 10, 11, 0, 3,           //  86: 01010110 
    4, 7, 11, 4, 11, 9, 9, 11, 10,                    //  87: 01010111 
    2, 9, 0, 2, 10, 9, 6, 11, 7,                      //  88: 01011000 
    6, 11, 7, 2, 10, 3, 10, 8, 3, 10, 9, 8,           //  89: 01011001 
    4, 11, 8, 4, 6, 11, 0, 2, 9, 2, 10, 9,            //  90: 01011010 
    10, 9, 3, 10, 3, 2, 9, 4, 3, 11, 3, 6, 4, 6, 3,   //  91: 01011011 
    0, 3, 7, 0, 7, 10, 0, 10, 9, 6, 10, 7,            //  92: 01011100 
    7, 6, 10, 7, 10, 8, 8, 10, 9,                     //  93: 01011101 
    4, 6, 3, 4, 3, 8, 6, 10, 3, 0, 3, 9, 10, 9, 3,    //  94: 01011110 
    10, 9, 4, 6, 10, 4,                               //  95: 01011111 
    1, 2, 10, 9, 5, 4,                                //  96: 01100000 
    3, 0, 8, 1, 2, 10, 4, 9, 5,                       //  97: 01100001 
    9, 7, 8, 9, 5, 7, 10, 1, 2,                       //  98: 01100010 
    10, 1, 2, 9, 5, 0, 5, 3, 0, 5, 7, 3,              //  99: 01100011 
    10, 3, 11, 10, 1, 3, 9, 5, 4,                     // 100: 01100100
    4, 9, 5, 0, 8, 1, 8, 10, 1, 8, 11, 10,            // 101: 01100101
    9, 5, 8, 8, 5, 7, 10, 1, 3, 10, 3, 11,            // 102: 01100110
    5, 7, 0, 5, 0, 9, 7, 11, 0, 1, 0, 10, 11, 10, 0,  // 103: 01100111
    9, 5, 4, 10, 1, 2, 7, 6, 11,                      // 104: 01101000
    6, 11, 7, 1, 2, 10, 0, 8, 3, 4, 9, 5,             // 105: 01101001
    1, 2, 10, 9, 5, 11, 9, 11, 8, 11, 5, 6,           // 106: 01101010
    0, 11, 3, 0, 6, 11, 0, 9, 6, 5, 6, 9, 1, 2, 10,   // 107: 01101011
    9, 5, 4, 10, 1, 6, 1, 7, 6, 1, 3, 7,              // 108: 01101100
    1, 6, 10, 1, 7, 6, 1, 0, 7, 8, 7, 0, 9, 5, 4,     // 109: 01101101
    1, 3, 6, 1, 6, 10, 3, 8, 6, 5, 6, 9, 8, 9, 6,     // 110: 01101110
    10, 1, 0, 10, 0, 6, 9, 5, 0, 5, 6, 0,             // 111: 01101111
    5, 2, 10, 5, 4, 2, 4, 0, 2,                       // 112: 01110000
    2, 10, 5, 3, 2, 5, 3, 5, 4, 3, 4, 8,              // 113: 01110001
    8, 0, 2, 8, 2, 5, 8, 5, 7, 10, 5, 2,              // 114: 01110010
    2, 10, 5, 2, 5, 3, 3, 5, 7,                       // 115: 01110011
    5, 4, 0, 5, 0, 11, 5, 11, 10, 11, 0, 3,           // 116: 01110100
    5, 4, 8, 5, 8, 10, 10, 8, 11,                     // 117: 01110101
    11, 10, 0, 11, 0, 3, 10, 5, 0, 8, 0, 7, 5, 7, 0,  // 118: 01110110
    11, 10, 5, 7, 11, 5,                              // 119: 01110111
    7, 6, 11, 5, 4, 10, 4, 2, 10, 4, 0, 2,            // 120: 01111000
    3, 4, 8, 3, 5, 4, 3, 2, 5, 10, 5, 2, 11, 7, 6,    // 121: 01111001
    11, 8, 5, 11, 5, 6, 8, 0, 5, 10, 5, 2, 0, 2, 5,   // 122: 01111010
    6, 11, 3, 6, 3, 5, 2, 10, 3, 10, 5, 3,            // 123: 01111011
    4, 0, 10, 4, 10, 5, 0, 3, 10, 6, 10, 7, 3, 7, 10, // 124: 01111100
    7, 6, 10, 7, 10, 8, 5, 4, 10, 4, 8, 10,           // 125: 01111101
    0, 3, 8, 5, 6, 10,                                // 126: 01111110
    10, 5, 6,                                         // 127: 01111111
    10, 6, 5,                                         // 128: 10000000
    0, 8, 3, 5, 10, 6,                                // 129: 10000001
    5, 10, 6, 4, 7, 8,                                // 130: 10000010
    4, 3, 0, 4, 7, 3, 6, 5, 10,                       // 131: 10000011
    2, 3, 11, 10, 6, 5,                               // 132: 10000100
    11, 0, 8, 11, 2, 0, 10, 6, 5,                     // 133: 10000101
    3, 11, 2, 7, 8, 4, 10, 6, 5,                      // 134: 10000110
    5, 10, 6, 4, 7, 2, 4, 2, 0, 2, 7, 11,             // 135: 10000111
    11, 5, 10, 7, 5, 11,                              // 136: 10001000
    11, 5, 10, 11, 7, 5, 8, 3, 0,                     // 137: 10001001
    5, 8, 4, 5, 10, 8, 10, 11, 8,                     // 138: 10001010
    5, 0, 4, 5, 11, 0, 5, 10, 11, 11, 3, 0,           // 139: 10001011
    2, 5, 10, 2, 3, 5, 3, 7, 5,                       // 140: 10001100
    8, 2, 0, 8, 5, 2, 8, 7, 5, 10, 2, 5,              // 141: 10001101
    2, 5, 10, 3, 5, 2, 3, 4, 5, 3, 8, 4,              // 142: 10001110
    5, 10, 2, 5, 2, 4, 4, 2, 0,                       // 143: 10001111
    9, 0, 1, 5, 10, 6,                                // 144: 10010000
    1, 8, 3, 1, 9, 8, 5, 10, 6,                       // 145: 10010001
    1, 9, 0, 5, 10, 6, 8, 4, 7,                       // 146: 10010010
    10, 6, 5, 1, 9, 7, 1, 7, 3, 7, 9, 4,              // 147: 10010011
    0, 1, 9, 2, 3, 11, 5, 10, 6,                      // 148: 10010100
    5, 10, 6, 1, 9, 2, 9, 11, 2, 9, 8, 11,            // 149: 10010101
    0, 1, 9, 4, 7, 8, 2, 3, 11, 5, 10, 6,             // 150: 10010110
    9, 2, 1, 9, 11, 2, 9, 4, 11, 7, 11, 4, 5, 10, 6,  // 151: 10010111
    5, 11, 7, 5, 10, 11, 1, 9, 0,                     // 152: 10011000
    10, 7, 5, 10, 11, 7, 9, 8, 1, 8, 3, 1,            // 153: 10011001
    0, 1, 9, 8, 4, 10, 8, 10, 11, 10, 4, 5,           // 154: 10011010
    10, 11, 4, 10, 4, 5, 11, 3, 4, 9, 4, 1, 3, 1, 4,  // 155: 10011011
    9, 0, 1, 5, 10, 3, 5, 3, 7, 3, 10, 2,             // 156: 10011100
    9, 8, 2, 9, 2, 1, 8, 7, 2, 10, 2, 5, 7, 5, 2,     // 157: 10011101
    3, 10, 2, 3, 5, 10, 3, 8, 5, 4, 5, 8, 0, 1, 9,    // 158: 10011110
    5, 10, 2, 5, 2, 4, 1, 9, 2, 9, 4, 2,              // 159: 10011111
    10, 4, 9, 6, 4, 10,                               // 160: 10100000
    4, 10, 6, 4, 9, 10, 0, 8, 3,                      // 161: 10100001
    7, 10, 6, 7, 8, 10, 8, 9, 10,                     // 162: 10100010
    0, 7, 3, 0, 10, 7, 0, 9, 10, 6, 7, 10,            // 163: 10100011
    10, 4, 9, 10, 6, 4, 11, 2, 3,                     // 164: 10100100
    0, 8, 2, 2, 8, 11, 4, 9, 10, 4, 10, 6,            // 165: 10100101
    2, 3, 11, 10, 6, 8, 10, 8, 9, 8, 6, 7,            // 166: 10100110
    2, 0, 7, 2, 7, 11, 0, 9, 7, 6, 7, 10, 9, 10, 7,   // 167: 10100111
    4, 11, 7, 4, 9, 11, 9, 10, 11,                    // 168: 10101000
    0, 8, 3, 4, 9, 7, 9, 11, 7, 9, 10, 11,            // 169: 10101001
    9, 10, 8, 10, 11, 8,                              // 170: 10101010
    3, 0, 9, 3, 9, 11, 11, 9, 10,                     // 171: 10101011
    2, 9, 10, 2, 7, 9, 2, 3, 7, 7, 4, 9,              // 172: 10101100
    9, 10, 7, 9, 7, 4, 10, 2, 7, 8, 7, 0, 2, 0, 7,    // 173: 10101101
    2, 3, 8, 2, 8, 10, 10, 8, 9,                      // 174: 10101110
    9, 10, 2, 0, 9, 2,                                // 175: 10101111
    10, 0, 1, 10, 6, 0, 6, 4, 0,                      // 176: 10110000
    8, 3, 1, 8, 1, 6, 8, 6, 4, 6, 1, 10,              // 177: 10110001
    10, 6, 7, 1, 10, 7, 1, 7, 8, 1, 8, 0,             // 178: 10110010
    10, 6, 7, 10, 7, 1, 1, 7, 3,                      // 179: 10110011
    3, 11, 2, 0, 1, 6, 0, 6, 4, 6, 1, 10,             // 180: 10110100
    6, 4, 1, 6, 1, 10, 4, 8, 1, 2, 1, 11, 8, 11, 1,   // 181: 10110101
    1, 8, 0, 1, 7, 8, 1, 10, 7, 6, 7, 10, 2, 3, 11,   // 182: 10110110
    11, 2, 1, 11, 1, 7, 10, 6, 1, 6, 7, 1,            // 183: 10110111
    1, 10, 11, 1, 11, 4, 1, 4, 0, 7, 4, 11,           // 184: 10111000
    3, 1, 4, 3, 4, 8, 1, 10, 4, 7, 4, 11, 10, 11, 4,  // 185: 10111001
    0, 1, 10, 0, 10, 8, 8, 10, 11,                    // 186: 10111010
    3, 1, 10, 11, 3, 10,                              // 187: 10111011
    3, 7, 10, 3, 10, 2, 7, 4, 10, 1, 10, 0, 4, 0, 10, // 188: 10111100
    1, 10, 2, 8, 7, 4,                                // 189: 10111101
    2, 3, 8, 2, 8, 10, 0, 1, 8, 1, 10, 8,             // 190: 10111110
    1, 10, 2,                                         // 191: 10111111
    1, 6, 5, 2, 6, 1,                                 // 192: 11000000
    1, 6, 5, 1, 2, 6, 3, 0, 8,                        // 193: 11000001
    6, 1, 2, 6, 5, 1, 4, 7, 8,                        // 194: 11000010
    1, 2, 5, 5, 2, 6, 3, 0, 4, 3, 4, 7,               // 195: 11000011
    6, 3, 11, 6, 5, 3, 5, 1, 3,                       // 196: 11000100
    0, 8, 11, 0, 11, 5, 0, 5, 1, 5, 11, 6,            // 197: 11000101
    8, 4, 7, 3, 11, 5, 3, 5, 1, 5, 11, 6,             // 198: 11000110
    5, 1, 11, 5, 11, 6, 1, 0, 11, 7, 11, 4, 0, 4, 11, // 199: 11000111
    11, 1, 2, 11, 7, 1, 7, 5, 1,                      // 200: 11001000
    0, 8, 3, 1, 2, 7, 1, 7, 5, 7, 2, 11,              // 201: 11001001
    2, 5, 1, 2, 8, 5, 2, 11, 8, 4, 5, 8,              // 202: 11001010
    0, 4, 11, 0, 11, 3, 4, 5, 11, 2, 11, 1, 5, 1, 11, // 203: 11001011
    1, 3, 5, 3, 7, 5,                                 // 204: 11001100
    0, 8, 7, 0, 7, 1, 1, 7, 5,                        // 205: 11001101
    8, 4, 5, 8, 5, 3, 3, 5, 1,                        // 206: 11001110
    0, 4, 5, 1, 0, 5,                                 // 207: 11001111
    9, 6, 5, 9, 0, 6, 0, 2, 6,                        // 208: 11010000
    5, 9, 8, 5, 8, 2, 5, 2, 6, 3, 2, 8,               // 209: 11010001
    8, 4, 7, 9, 0, 5, 0, 6, 5, 0, 2, 6,               // 210: 11010010
    7, 3, 9, 7, 9, 4, 3, 2, 9, 5, 9, 6, 2, 6, 9,      // 211: 11010011
    3, 11, 6, 0, 3, 6, 0, 6, 5, 0, 5, 9,              // 212: 11010100
    6, 5, 9, 6, 9, 11, 11, 9, 8,                      // 213: 11010101
    0, 5, 9, 0, 6, 5, 0, 3, 6, 11, 6, 3, 8, 4, 7,     // 214: 11010110
    6, 5, 9, 6, 9, 11, 4, 7, 9, 7, 11, 9,             // 215: 11010111
    9, 7, 5, 9, 2, 7, 9, 0, 2, 2, 11, 7,              // 216: 11011000
    7, 5, 2, 7, 2, 11, 5, 9, 2, 3, 2, 8, 9, 8, 2,     // 217: 11011001
    0, 2, 5, 0, 5, 9, 2, 11, 5, 4, 5, 8, 11, 8, 5,    // 218: 11011010
    9, 4, 5, 2, 11, 3,                                // 219: 11011011
    9, 0, 3, 9, 3, 5, 5, 3, 7,                        // 220: 11011100
    9, 8, 7, 5, 9, 7,                                 // 221: 11011101
    8, 4, 5, 8, 5, 3, 9, 0, 5, 0, 3, 5,               // 222: 11011110
    9, 4, 5,                                          // 223: 11011111
    1, 4, 9, 1, 2, 4, 2, 6, 4,                        // 224: 11100000
    3, 0, 8, 1, 2, 9, 2, 4, 9, 2, 6, 4,               // 225: 11100001
    1, 2, 6, 1, 6, 8, 1, 8, 9, 8, 6, 7,               // 226: 11100010
    2, 6, 9, 2, 9, 1, 6, 7, 9, 0, 9, 3, 7, 3, 9,      // 227: 11100011
    9, 6, 4, 9, 3, 6, 9, 1, 3, 11, 6, 3,              // 228: 11100100
    8, 11, 1, 8, 1, 0, 11, 6, 1, 9, 1, 4, 6, 4, 1,    // 229: 11100101
    8, 9, 6, 8, 6, 7, 9, 1, 6, 11, 6, 3, 1, 3, 6,     // 230: 11100110
    0, 9, 1, 11, 6, 7,                                // 231: 11100111
    4, 11, 7, 9, 11, 4, 9, 2, 11, 9, 1, 2,            // 232: 11101000
    9, 7, 4, 9, 11, 7, 9, 1, 11, 2, 11, 1, 0, 8, 3,   // 233: 11101001
    1, 2, 11, 1, 11, 9, 9, 11, 8,                     // 234: 11101010
    3, 0, 9, 3, 9, 11, 1, 2, 9, 2, 11, 9,             // 235: 11101011
    4, 9, 1, 4, 1, 7, 7, 1, 3,                        // 236: 11101100
    4, 9, 1, 4, 1, 7, 0, 8, 1, 8, 7, 1,               // 237: 11101101
    1, 3, 8, 9, 1, 8,                                 // 238: 11101110
    0, 9, 1,                                          // 239: 11101111
    0, 2, 4, 4, 2, 6,                                 // 240: 11110000
    8, 3, 2, 8, 2, 4, 4, 2, 6,                        // 241: 11110001
    7, 8, 0, 7, 0, 6, 6, 0, 2,                        // 242: 11110010
    7, 3, 2, 6, 7, 2,                                 // 243: 11110011
    3, 11, 6, 3, 6, 0, 0, 6, 4,                       // 244: 11110100
    6, 4, 8, 11, 6, 8,                                // 245: 11110101
    7, 8, 0, 7, 0, 6, 3, 11, 0, 11, 6, 0,             // 246: 11110110
    7, 11, 6,                                         // 247: 11110111
    11, 7, 4, 11, 4, 2, 2, 4, 0,                      // 248: 11111000
    11, 7, 4, 11, 4, 2, 8, 3, 4, 3, 2, 4,             // 249: 11111001
    0, 2, 11, 8, 0, 11,                               // 250: 11111010
    3, 2, 11,                                         // 251: 11111011
    4, 0, 3, 7, 4, 3,                                 // 252: 11111100
    4, 8, 7,                                          // 253: 11111101
    0, 3, 8                                           // 254: 11111110
                                                      // 255: 11111111
};

std::array<std::uint16_t, 257> triangleIndices =
{
    0, 0, 1, 2, 4, 5, 7, 9, 12, 13, 15, 17, 20, 22, 25, 28, 30, 31, 33, 35, 38, 40, 43, 
    46, 50, 52, 55, 58, 62, 65, 69, 73, 76, 77, 79, 81, 84, 86, 89, 92, 96, 98, 101, 104, 
    108, 111, 115, 119, 122, 124, 127, 130, 132, 135, 139, 143, 146, 149, 153, 157, 160, 
    164, 169, 174, 176, 177, 179, 181, 184, 186, 189, 192, 196, 198, 201, 204, 208, 211, 
    215, 219, 222, 224, 227, 230, 234, 237, 239, 243, 246, 249, 253, 257, 262, 266, 269, 
    274, 276, 278, 281, 284, 288, 291, 295, 299, 304, 307, 311, 315, 320, 324, 329, 334, 
    338, 341, 345, 349, 352, 356, 359, 364, 366, 370, 375, 380, 384, 389, 393, 395, 396, 
    397, 399, 401, 404, 406, 409, 412, 416, 418, 421, 424, 428, 431, 435, 439, 442, 444, 
    447, 450, 454, 457, 461, 465, 470, 473, 477, 481, 486, 490, 495, 500, 504, 506, 509, 
    512, 516, 519, 523, 527, 532, 535, 539, 541, 544, 548, 553, 556, 558, 561, 565, 569, 
    572, 576, 581, 586, 590, 594, 599, 602, 604, 609, 611, 615, 616, 618, 621, 624, 628, 
    631, 635, 639, 644, 647, 651, 655, 660, 662, 665, 668, 670, 673, 677, 681, 686, 690, 
    693, 698, 702, 706, 711, 716, 718, 721, 723, 727, 728, 731, 735, 739, 744, 748, 753, 
    758, 760, 764, 769, 772, 776, 779, 783, 785, 786, 788, 791, 794, 796, 799, 801, 805, 
    806, 809, 813, 815, 816, 818, 819, 820, 820
};

std::array<std::uint16_t, 256> edgeTable =
{
    0, 265, 400, 153, 2060, 2309, 2460, 2197, 2240, 2505, 2384, 2137, 204, 453, 348, 85, 
    515, 778, 915, 666, 2575, 2822, 2975, 2710, 2755, 3018, 2899, 2650, 719, 966, 863, 
    598, 560, 825, 928, 681, 2620, 2869, 2988, 2725, 2800, 3065, 2912, 2665, 764, 1013, 
    876, 613, 51, 314, 419, 170, 2111, 2358, 2479, 2214, 2291, 2554, 2403, 2154, 255, 
    502, 367, 102, 1030, 1295, 1430, 1183, 3082, 3331, 3482, 3219, 3270, 3535, 3414, 3167, 
    1226, 1475, 1370, 1107, 1541, 1804, 1941, 1692, 3593, 3840, 3993, 3728, 3781, 4044, 
    3925, 3676, 1737, 1984, 1881, 1616, 1590, 1855, 1958, 1711, 3642, 3891, 4010, 3747, 
    3830, 4095, 3942, 3695, 1786, 2035, 1898, 1635, 1077, 1340, 1445, 1196, 3129, 3376, 
    3497, 3232, 3317, 3580, 3429, 3180, 1273, 1520, 1385, 1120, 1120, 1385, 1520, 1273, 
    3180, 3429, 3580, 3317, 3232, 3497, 3376, 3129, 1196, 1445, 1340, 1077, 1635, 1898, 
    2035, 1786, 3695, 3942, 4095, 3830, 3747, 4010, 3891, 3642, 1711, 1958, 1855, 1590, 
    1616, 1881, 1984, 1737, 3676, 3925, 4044, 3781, 3728, 3993, 3840, 3593, 1692, 1941,
    1804, 1541, 1107, 1370, 1475, 1226, 3167, 3414, 3535, 3270, 3219, 3482, 3331, 3082, 
    1183, 1430, 1295, 1030, 102, 367, 502, 255, 2154, 2403, 2554, 2291, 2214, 2479, 2358, 
    2111, 170, 419, 314, 51, 613, 876, 1013, 764, 2665, 2912, 3065, 2800, 2725, 2988, 2869, 
    2620, 681, 928, 825, 560, 598, 863, 966, 719, 2650, 2899, 3018, 2755, 2710, 2975, 2822, 
    2575, 666, 915, 778, 515, 85, 348, 453, 204, 2137, 2384, 2505, 2240, 2197, 2460, 2309, 
    2060, 153, 400, 265, 0
};


std::vector<std::vector<size_t>> tetrahedra =
{
    {  },
    {  8, 16, 11,  0 },
    { 12, 16, 15,  1 },
    { 12, 11,  8,  0, 15, 11, 12,  1,  0,  1, 11, 12 },
    { 10, 19, 11,  2 },
    { 16, 10, 19,  2,  8, 10, 16,  0,  2,  0, 10, 16 },
    { 16, 12, 15,  1, 11, 19, 10,  2 },
    { 19, 12, 15,  0, 19, 10, 12,  0, 10,  8, 12,  0,  0,  1, 12, 15,  0,  2, 19, 10 },
    { 14, 19, 15,  3 },
    { 16,  8, 11,  0, 15, 19, 14,  3 },
    { 16, 14, 19,  3, 12, 14, 16,  1,  3,  1, 14, 16 },
    { 19,  8, 11,  1, 19, 14,  8,  1, 14, 12,  8,  1,  1,  0,  8, 11,  1,  3, 19, 14 },
    { 14, 11, 10,  2, 15, 11, 14,  3,  2,  3, 11, 14 },
    { 16, 14, 15,  2, 16,  8, 14,  2,  8, 10, 14,  2,  2,  3, 14, 15,  2,  0, 16,  8 },
    { 16, 10, 11,  3, 16, 12, 10,  3, 12, 14, 10,  3,  3,  2, 10, 11,  3,  1, 16, 12 },
    {  8, 12, 10,  0, 12, 14, 10,  3,  0,  3, 10, 12,  0,  1,  3, 12,  0,  2,  3, 10 },
    {  8, 17,  9,  4 },
    { 17, 11, 16,  0,  9, 11, 17,  4,  0,  4, 11, 17 },
    { 16, 15, 12,  1,  8, 17,  9,  4 },
    { 17, 15, 12,  0, 17,  9, 15,  0,  9, 11, 15,  0,  0,  1, 15, 12,  0,  4, 17,  9 },
    {  8, 17,  9,  4, 11, 10, 19,  2 },
    { 10, 17,  9,  0, 10, 19, 17,  0, 19, 16, 17,  0,  0,  4, 17,  9,  0,  2, 10, 19 },
    { 17,  8,  9,  4, 16, 12, 15,  1, 10, 11, 19,  2 },
    { 19, 15,  0, 10,  0, 12, 17, 15,  0, 10, 15, 17,  0, 10,  9, 17,  0,  4,  9, 17,  0,  1, 15, 12,  0,  2, 19, 10 },
    {  8,  9, 17,  4, 19, 15, 14,  3 },
    { 16,  9, 17,  4, 16, 11,  9,  4, 19, 15, 14,  3,  0,  4, 11, 16 },
    { 16, 14, 19,  3, 16, 12, 14,  3, 17,  8,  9,  4,  1,  3, 12, 16 },
    { 19, 11, 12,  1, 17, 12,  0, 11,  0, 11,  1, 12,  0, 11,  4, 17, 19,  3,  1, 12, 12, 14, 19,  3,  4,  9, 17, 11, 11, 14, 12, 19, 11, 14, 12, 17 },
    { 10, 15, 14,  3, 10, 11, 15,  3,  8,  9, 17,  4,  2,  3, 11, 10 },
    {  9, 10, 16,  0, 15, 16,  2, 10,  2, 10,  0, 16,  2, 10,  3, 15,  9,  4,  0, 16, 16, 17,  9,  4,  3, 14, 15, 10, 10, 17, 16,  9, 10, 17, 16, 15 },
    {  4,  8,  9, 17,  1, 14, 16, 12, 10, 14, 11, 12, 10, 14, 11,  2, 11, 12, 16, 14,  2, 11,  3, 14, 11, 16,  3, 14, 16,  1,  3, 14 },
    { 17, 10,  9,  0, 17, 12, 10,  0, 12, 14, 10,  3,  4,  0,  9, 17,  3,  2, 10, 12,  2, 10, 12,  0,  3,  2,  0, 12,  3,  1,  0, 12 },
    { 12, 17, 13,  5 },
    { 16, 11,  8,  0, 12, 17, 13,  5 },
    { 17, 15, 16,  1, 13, 15, 17,  5,  1,  5, 15, 17 },
    { 17, 11,  8,  1, 17, 13, 11,  1, 13, 15, 11,  1,  1,  0, 11,  8,  1,  5, 17, 13 },
    { 12, 13, 17,  5, 19, 11, 10,  2 },
    { 16, 10, 19,  2, 16,  8, 10,  2, 17, 12, 13,  5,  0,  2,  8, 16 },
    { 16, 13, 17,  5, 16, 15, 13,  5, 19, 11, 10,  2,  1,  5, 15, 16 },
    { 19, 15,  8,  0, 17,  8,  1, 15,  1, 15,  0,  8,  1, 15,  5, 17, 19,  2,  0,  8,  8, 10, 19,  2,  5, 13, 17, 15, 15, 10,  8, 19, 15, 10,  8, 17 },
    { 12, 17, 13,  5, 15, 14, 19,  3 },
    { 17, 12, 13,  5, 16,  8, 11,  0, 14, 15, 19,  3 },
    { 14, 17, 13,  1, 14, 19, 17,  1, 19, 16, 17,  1,  1,  5, 17, 13,  1,  3, 14, 19 },
    { 19, 11,  1, 14,  1,  8, 17, 11,  1, 14, 11, 17,  1, 14, 13, 17,  1,  5, 13, 17,  1,  0, 11,  8,  1,  3, 19, 14 },
    { 14, 11, 10,  2, 14, 15, 11,  2, 12, 13, 17,  5,  3,  2, 15, 14 },
    {  5, 12, 13, 17,  0, 10, 16,  8, 14, 10, 15,  8, 14, 10, 15,  3, 15,  8, 16, 10,  3, 15,  2, 10, 15, 16,  2, 10, 16,  0,  2, 10 },
    { 13, 14, 16,  1, 11, 16,  3, 14,  3, 14,  1, 16,  3, 14,  2, 11, 13,  5,  1, 16, 16, 17, 13,  5,  2, 10, 11, 14, 14, 17, 16, 13, 14, 17, 16, 11 },
    { 17, 14, 13,  1, 17,  8, 14,  1,  8, 10, 14,  2,  5,  1, 13, 17,  2,  3, 14,  8,  3, 14,  8,  1,  2,  3,  1,  8,  2,  0,  1,  8 },
    { 12,  9,  8,  4, 13,  9, 12,  5,  4,  5,  9, 12 },
    { 16, 13, 12,  4, 16, 11, 13,  4, 11,  9, 13,  4,  4,  5, 13, 12,  4,  0, 16, 11 },
    { 16,  9,  8,  5, 16, 15,  9,  5, 15, 13,  9,  5,  5,  4,  9,  8,  5,  1, 16, 15 },
    { 11, 15,  9,  0, 15, 13,  9,  5,  0,  5,  9, 15,  0,  1,  5, 15,  0,  4,  5,  9 },
    {  8, 13, 12,  5,  8,  9, 13,  5, 10, 11, 19,  2,  4,  5,  9,  8 },
    { 10,  9, 16,  0, 12, 16,  4,  9,  4,  9,  0, 16,  4,  9,  5, 12, 10,  2,  0, 16, 16, 19, 10,  2,  5, 13, 12,  9,  9, 19, 16, 10,  9, 19, 16, 12 },
    {  2, 11, 10, 19,  1, 13, 16, 15,  9, 13,  8, 15,  9, 13,  8,  4,  8, 15, 16, 13,  4,  8,  5, 13,  8, 16,  5, 13, 16,  1,  5, 13 },
    { 19,  9, 10,  0, 19, 15,  9,  0, 15, 13,  9,  5,  2,  0, 10, 19,  5,  4,  9, 15,  4,  9, 15,  0,  5,  4,  0, 15,  5,  1,  0, 15 },
    { 12,  9,  8,  4, 12, 13,  9,  4, 14, 15, 19,  3,  5,  4, 13, 12 },
    {  3, 15, 14, 19,  0,  9, 16, 11, 13,  9, 12, 11, 13,  9, 12,  5, 12, 11, 16,  9,  5, 12,  4,  9, 12, 16,  4,  9, 16,  0,  4,  9 },
    { 14, 13, 16,  1,  8, 16,  5, 13,  5, 13,  1, 16,  5, 13,  4,  8, 14,  3,  1, 16, 16, 19, 14,  3,  4,  9,  8, 13, 13, 19, 16, 14, 13, 19, 16,  8 },
    { 19, 13, 14,  1, 19, 11, 13,  1, 11,  9, 13,  4,  3,  1, 14, 19,  4,  5, 13, 11,  5, 13, 11,  1,  4,  5,  1, 11,  4,  0,  1, 11 },
    { 15, 14,  3, 10, 15,  3,  2, 10, 15, 11,  2, 10,  5, 12, 13,  9,  5,  4, 12,  9,  4, 12,  8,  9 },
    {  9, 16,  0, 10, 15, 16, 10,  2, 12, 16,  4,  9, 10,  2,  0, 16,  9, 16,  4,  0, 10,  2,  3, 15, 15, 14, 10,  3,  5, 12,  9,  4, 13,  5, 12,  9,  9, 10, 16, 15,  9, 10, 15, 14, 16, 15, 12,  9, 15, 12,  9, 13, 13, 15, 14,  9 },
    { 13, 16,  1, 14, 11, 16, 14,  3,  8, 16,  5, 13, 14,  3,  1, 16, 13, 16,  5,  1, 14,  3,  2, 11, 11, 10, 14,  2,  4,  8, 13,  5,  9,  4,  8, 13, 13, 14, 16, 11, 13, 14, 11, 10, 16, 11,  8, 13, 11,  8, 13,  9,  9, 11, 10, 13 },
    {  9, 13, 14,  1, 10,  9, 14,  0,  9, 14,  0,  1,  0,  1,  4,  9,  1,  4,  5,  9,  1,  5,  9, 13,  0,  1,  3, 14,  0,  2,  3, 14,  0,  2, 10, 14 },
    { 10, 18,  9,  6 },
    { 10, 18,  9,  6, 11,  8, 16,  0 },
    { 10,  9, 18,  6, 16, 15, 12,  1 },
    {  8, 15, 12,  1,  8, 11, 15,  1, 10,  9, 18,  6,  0,  1, 11,  8 },
    { 18, 11, 19,  2,  9, 11, 18,  6,  2,  6, 11, 18 },
    {  8, 18,  9,  2,  8, 16, 18,  2, 16, 19, 18,  2,  2,  6, 18,  9,  2,  0,  8, 16 },
    { 19,  9, 18,  6, 19, 11,  9,  6, 16, 15, 12,  1,  2,  6, 11, 19 },
    {  9,  8, 19,  2, 15, 19,  0,  8,  0,  8,  2, 19,  0,  8,  1, 15,  9,  6,  2, 19, 19, 18,  9,  6,  1, 12, 15,  8,  8, 18, 19,  9,  8, 18, 19, 15 },
    { 19, 15, 14,  3, 10, 18,  9,  6 },
    { 18, 10,  9,  6, 19, 14, 15,  3,  8, 11, 16,  0 },
    { 19, 12, 16,  1, 19, 14, 12,  1, 18, 10,  9,  6,  3,  1, 14, 19 },
    {  6, 10,  9, 18,  3, 12, 19, 14,  8, 12, 11, 14,  8, 12, 11,  0, 11, 14, 19, 12,  0, 11,  1, 12, 11, 19,  1, 12, 19,  3,  1, 12 },
    { 18, 15, 14,  2, 18,  9, 15,  2,  9, 11, 15,  2,  2,  3, 15, 14,  2,  6, 18,  9 },
    { 16, 15,  2,  8,  2, 14, 18, 15,  2,  8, 15, 18,  2,  8,  9, 18,  2,  6,  9, 18,  2,  3, 15, 14,  2,  0, 16,  8 },
    { 16, 11, 14,  3, 18, 14,  2, 11,  2, 11,  3, 14,  2, 11,  6, 18, 16,  1,  3, 14, 14, 12, 16,  1,  6,  9, 18, 11, 11, 12, 14, 16, 11, 12, 14, 18 },
    { 18,  8,  9,  2, 18, 14,  8,  2, 14, 12,  8,  1,  6,  2,  9, 18,  1,  0,  8, 14,  0,  8, 14,  2,  1,  0,  2, 14,  1,  3,  2, 14 },
    { 17, 10, 18,  6,  8, 10, 17,  4,  6,  4, 10, 17 },
    { 10, 16, 11,  4, 10, 18, 16,  4, 18, 17, 16,  4,  4,  0, 16, 11,  4,  6, 10, 18 },
    { 17, 10, 18,  6, 17,  8, 10,  6, 16, 12, 15,  1,  4,  6,  8, 17 },
    { 10, 11, 17,  4, 12, 17,  0, 11,  0, 11,  4, 17,  0, 11,  1, 12, 10,  6,  4, 17, 17, 18, 10,  6,  1, 15, 12, 11, 11, 18, 17, 10, 11, 18, 17, 12 },
    {  8, 19, 11,  6,  8, 17, 19,  6, 17, 18, 19,  6,  6,  2, 19, 11,  6,  4,  8, 17 },
    { 16, 17, 19,  0, 17, 18, 19,  6,  0,  6, 19, 17,  0,  4,  6, 17,  0,  2,  6, 19 },
    {  1, 16, 15, 12,  4, 18,  8, 17, 19, 18, 11, 17, 19, 18, 11,  2, 11, 17,  8, 18,  2, 11,  6, 18, 11,  8,  6, 18,  8,  4,  6, 18 },
    { 12, 19, 15,  0, 12, 17, 19,  0, 17, 18, 19,  6,  1,  0, 15, 12,  6,  2, 19, 17,  2, 19, 17,  0,  6,  2,  0, 17,  6,  4,  0, 17 },
    { 18,  8, 17,  4, 18, 10,  8,  4, 19, 14, 15,  3,  6,  4, 10, 18 },
    {  3, 19, 15, 14,  6, 17, 10, 18, 16, 17, 11, 18, 16, 17, 11,  0, 11, 18, 10, 17,  0, 11,  4, 17, 11, 10,  4, 17, 10,  6,  4, 17 },
    { 16, 12,  1, 14, 16,  1,  3, 14, 16, 19,  3, 14,  4,  8, 17, 18,  4,  6,  8, 18,  6,  8, 10, 18 },
    { 12, 11,  0, 17, 10, 11, 17,  4, 19, 11,  1, 12, 17,  4,  0, 11, 12, 11,  1,  0, 17,  4,  6, 10, 10, 18, 17,  6,  3, 19, 12,  1, 14,  3, 19, 12, 12, 17, 11, 10, 12, 17, 10, 18, 11, 10, 19, 12, 10, 19, 12, 14, 14, 10, 18, 12 },
    {  8, 11, 18,  6, 14, 18,  2, 11,  2, 11,  6, 18,  2, 11,  3, 14,  8,  4,  6, 18, 18, 17,  8,  4,  3, 15, 14, 11, 11, 17, 18,  8, 11, 17, 18, 14 },
    { 14, 16, 15,  2, 14, 18, 16,  2, 18, 17, 16,  4,  3,  2, 15, 14,  4,  0, 16, 18,  0, 16, 18,  2,  4,  0,  2, 18,  4,  6,  2, 18 },
    { 14, 11,  2, 18,  8, 11, 18,  6, 16, 11,  3, 14, 18,  6,  2, 11, 14, 11,  3,  2, 18,  6,  4,  8,  8, 17, 18,  4,  1, 16, 14,  3, 12,  1, 16, 14, 14, 18, 11,  8, 14, 18,  8, 17, 11,  8, 16, 14,  8, 16, 14, 12, 12,  8, 17, 14 },
    { 14, 12, 17,  0, 18, 14, 17,  2, 14, 17,  2,  0,  2,  0,  3, 14,  0,  3,  1, 14,  0,  1, 14, 12,  2,  0,  4, 17,  2,  6,  4, 17,  2,  6, 18, 17 },
    { 17, 12, 13,  5,  9, 18, 10,  6 },
    { 16,  8, 11,  0, 17, 12, 13,  5, 10,  9, 18,  6 },
    { 17, 15, 16,  1, 17, 13, 15,  1, 18,  9, 10,  6,  5,  1, 13, 17 },
    {  6,  9, 10, 18,  5, 15, 17, 13, 11, 15,  8, 13, 11, 15,  8,  0,  8, 13, 17, 15,  0,  8,  1, 15,  8, 17,  1, 15, 17,  5,  1, 15 },
    { 18, 11, 19,  2, 18,  9, 11,  2, 17, 13, 12,  5,  6,  2,  9, 18 },
    {  5, 17, 13, 12,  0, 19,  8, 16, 18, 19,  9, 16, 18, 19,  9,  6,  9, 16,  8, 19,  6,  9,  2, 19,  9,  8,  2, 19,  8,  0,  2, 19 },
    { 19, 11,  2,  9, 19,  2,  6,  9, 19, 18,  6,  9,  1, 15, 16, 17,  1,  5, 15, 17,  5, 15, 13, 17 },
    { 15,  8,  0, 19,  9,  8, 19,  2, 17,  8,  1, 15, 19,  2,  0,  8, 15,  8,  1,  0, 19,  2,  6,  9,  9, 18, 19,  6,  5, 17, 15,  1, 13,  5, 17, 15, 15, 19,  8,  9, 15, 19,  9, 18,  8,  9, 17, 15,  9, 17, 15, 13, 13,  9, 18, 15 },
    { 19, 14, 15,  3, 18, 10,  9,  6, 12, 13, 17,  5 },
    {  0,  8, 11, 16,  3, 14, 15, 19,  5, 12, 17, 13,  6,  9, 10, 18 },
    {  6, 18,  9, 10,  3, 16, 14, 19, 17, 16, 13, 19, 17, 16, 13,  5, 13, 19, 14, 16,  5, 13,  1, 16, 13, 14,  1, 16, 14,  3,  1, 16 },
    { 19, 10, 11, 18, 18, 14, 13, 17,  8,  9, 17, 18,  6,  9, 10, 18, 11,  9, 10, 18, 11,  8,  9, 18, 14, 18, 19, 17, 18, 19, 11,  8, 18, 19,  8, 17, 11,  8,  1,  0, 11,  8,  1, 19,  8,  1, 19, 17,  1, 19, 17, 14,  1, 19, 14,  3,  1, 13, 17,  5,  1, 13, 17, 14 },
    {  5, 13, 12, 17,  6, 11, 18,  9, 15, 11, 14,  9, 15, 11, 14,  3, 14,  9, 18, 11,  3, 14,  2, 11, 14, 18,  2, 11, 18,  6,  2, 11 },
    { 16, 12, 15, 17, 17,  8,  9, 18, 14, 13, 18, 17,  5, 13, 12, 17, 15, 13, 12, 17, 15, 14, 13, 17,  8, 17, 16, 18, 17, 16, 15, 14, 17, 16, 14, 18, 15, 14,  2,  3, 15, 14,  2, 16, 14,  2, 16, 18,  2, 16, 18,  8,  2, 16,  8,  0,  2,  9, 18,  6,  2,  9, 18,  8 },
    { 11, 14,  3, 16, 13, 14, 16,  1, 18, 14,  2, 11, 16,  1,  3, 14, 11, 14,  2,  3, 16,  1,  5, 13, 13, 17, 16,  5,  6, 18, 11,  2,  9,  6, 18, 11, 11, 16, 14, 13, 11, 16, 13, 17, 14, 13, 18, 11, 13, 18, 11,  9,  9, 13, 17, 11 },
    { 17,  8,  9,  1, 13, 18, 14,  2, 13,  9,  2, 18,  9, 18,  6,  2,  5,  1, 13, 17,  1, 13, 17,  9,  9, 13,  1,  2,  9,  8,  2,  1,  8,  1,  0,  2, 13,  1,  2, 14, 14,  1,  3,  2 },
    { 18, 12, 13,  4, 18, 10, 12,  4, 10,  8, 12,  4,  4,  5, 12, 13,  4,  6, 18, 10 },
    { 18, 13,  4, 10,  4, 12, 16, 13,  4, 10, 13, 16,  4, 10, 11, 16,  4,  0, 11, 16,  4,  5, 13, 12,  4,  6, 18, 10 },
    { 18, 13,  8,  4, 16,  8,  5, 13,  5, 13,  4,  8,  5, 13,  1, 16, 18,  6,  4,  8,  8, 10, 18,  6,  1, 15, 16, 13, 13, 10,  8, 18, 13, 10,  8, 16 },
    { 18, 11, 10,  4, 18, 13, 11,  4, 13, 15, 11,  1,  6,  4, 10, 18,  1,  0, 11, 13,  0, 11, 13,  4,  1,  0,  4, 13,  1,  5,  4, 13 },
    { 11,  8, 18,  6, 13, 18,  4,  8,  4,  8,  6, 18,  4,  8,  5, 13, 11,  2,  6, 18, 18, 19, 11,  2,  5, 12, 13,  8,  8, 19, 18, 11,  8, 19, 18, 13 },
    { 12, 18, 13,  4, 12, 16, 18,  4, 16, 19, 18,  2,  5,  4, 13, 12,  2,  6, 18, 16,  6, 18, 16,  4,  2,  6,  4, 16,  2,  0,  4, 16 },
    { 13,  8,  4, 18, 11,  8, 18,  6, 16,  8,  5, 13, 18,  6,  4,  8, 13,  8,  5,  4, 18,  6,  2, 11, 11, 19, 18,  2,  1, 16, 13,  5, 15,  1, 16, 13, 13, 18,  8, 11, 13, 18, 11, 19,  8, 11, 16, 13, 11, 16, 13, 15, 15, 11, 19, 13 },
    { 15, 13, 18,  4, 19, 15, 18,  0, 15, 18,  0,  4,  0,  4,  1, 15,  4,  1,  5, 15,  4,  5, 15, 13,  0,  4,  6, 18,  0,  2,  6, 18,  0,  2, 19, 18 },
    {  3, 14, 15, 19,  6,  8, 18, 10, 12,  8, 13, 10, 12,  8, 13,  5, 13, 10, 18,  8,  5, 13,  4,  8, 13, 18,  4,  8, 18,  6,  4,  8 },
    { 18, 14, 13, 19, 19, 10, 11, 16, 12, 15, 16, 19,  3, 15, 14, 19, 13, 15, 14, 19, 13, 12, 15, 19, 10, 19, 18, 16, 19, 18, 13, 12, 19, 18, 12, 16, 13, 12,  4,  5, 13, 12,  4, 18, 12,  4, 18, 16,  4, 18, 16, 10,  4, 18, 10,  6,  4, 11, 16,  0,  4, 11, 16, 10 },
    {  8, 13,  5, 16, 14, 13, 16,  1, 18, 13,  4,  8, 16,  1,  5, 13,  8, 13,  4,  5, 16,  1,  3, 14, 14, 19, 16,  3,  6, 18,  8,  4, 10,  6, 18,  8,  8, 16, 13, 14,  8, 16, 14, 19, 13, 14, 18,  8, 14, 18,  8, 10, 10, 14, 19,  8 },
    { 19, 11, 10,  1, 14, 18, 13,  4, 14, 10,  4, 18, 10, 18,  6,  4,  3,  1, 14, 19,  1, 14, 19, 10, 10, 14,  1,  4, 10, 11,  4,  1, 11,  1,  0,  4, 14,  1,  4, 13, 13,  1,  5,  4 },
    { 11, 18,  6,  8, 13, 18,  8,  4, 14, 18,  2, 11,  8,  4,  6, 18, 11, 18,  2,  6,  8,  4,  5, 13, 13, 12,  8,  5,  3, 14, 11,  2, 15,  3, 14, 11, 11,  8, 18, 13, 11,  8, 13, 12, 18, 13, 14, 11, 13, 14, 11, 15, 15, 13, 12, 11 },
    { 14, 18, 13,  2, 15, 12, 16,  4, 15, 13,  4, 12, 13, 12,  5,  4,  3,  2, 15, 14,  2, 15, 14, 13, 13, 15,  2,  4, 13, 18,  4,  2, 18,  2,  6,  4, 15,  2,  4, 16, 16,  2,  0,  4 },
    { 14, 13, 18,  2, 16, 11,  8,  5,  3, 11, 16, 14,  3, 14,  2, 11, 14,  2, 11, 13,  2, 11,  6, 18,  2, 11, 18, 13, 18, 13,  4,  8,  5,  4,  8, 13, 14, 13, 11, 16, 13, 11, 16,  5, 11, 13,  8,  5, 13,  8, 11, 18,  8, 11,  6, 18,  6, 18,  8,  4, 13,  5,  1, 16, 14, 13,  1, 16,  3, 14,  1, 16 },
    { 18, 13, 14,  4, 18,  4,  6,  2, 18, 14,  2,  4,  4,  5, 13,  1,  1,  4, 13, 14,  0,  1,  4, 14,  0,  2,  4, 14,  1,  2,  3, 14,  0,  1,  2, 14 },
    { 14, 18, 13,  7 },
    { 14, 13, 18,  7, 16, 11,  8,  0 },
    { 14, 18, 13,  7, 15, 12, 16,  1 },
    { 12, 11,  8,  0, 12, 15, 11,  0, 14, 13, 18,  7,  1,  0, 15, 12 },
    { 19, 11, 10,  2, 14, 18, 13,  7 },
    { 19,  8, 16,  0, 19, 10,  8,  0, 18, 14, 13,  7,  2,  0, 10, 19 },
    { 18, 14, 13,  7, 19, 10, 11,  2, 12, 15, 16,  1 },
    {  7, 14, 13, 18,  2,  8, 19, 10, 12,  8, 15, 10, 12,  8, 15,  1, 15, 10, 19,  8,  1, 15,  0,  8, 15, 19,  0,  8, 19,  2,  0,  8 },
    { 18, 15, 19,  3, 13, 15, 18,  7,  3,  7, 15, 18 },
    { 19, 13, 18,  7, 19, 15, 13,  7, 16, 11,  8,  0,  3,  7, 15, 19 },
    { 12, 18, 13,  3, 12, 16, 18,  3, 16, 19, 18,  3,  3,  7, 18, 13,  3,  1, 12, 16 },
    { 13, 12, 19,  3, 11, 19,  1, 12,  1, 12,  3, 19,  1, 12,  0, 11, 13,  7,  3, 19, 19, 18, 13,  7,  0,  8, 11, 12, 12, 18, 19, 13, 12, 18, 19, 11 },
    { 18, 11, 10,  3, 18, 13, 11,  3, 13, 15, 11,  3,  3,  2, 11, 10,  3,  7, 18, 13 },
    { 16, 15, 10,  2, 18, 10,  3, 15,  3, 15,  2, 10,  3, 15,  7, 18, 16,  0,  2, 10, 10,  8, 16,  0,  7, 13, 18, 15, 15,  8, 10, 16, 15,  8, 10, 18 },
    { 16, 11,  3, 12,  3, 10, 18, 11,  3, 12, 11, 18,  3, 12, 13, 18,  3,  7, 13, 18,  3,  2, 11, 10,  3,  1, 16, 12 },
    { 18, 12, 13,  3, 18, 10, 12,  3, 10,  8, 12,  0,  7,  3, 13, 18,  0,  1, 12, 10,  1, 12, 10,  3,  0,  1,  3, 10,  0,  2,  3, 10 },
    { 17,  8,  9,  4, 13, 18, 14,  7 },
    { 17, 11, 16,  0, 17,  9, 11,  0, 18, 13, 14,  7,  4,  0,  9, 17 },
    { 16, 12, 15,  1, 17,  8,  9,  4, 14, 13, 18,  7 },
    {  7, 13, 14, 18,  4, 11, 17,  9, 15, 11, 12,  9, 15, 11, 12,  1, 12,  9, 17, 11,  1, 12,  0, 11, 12, 17,  0, 11, 17,  4,  0, 11 },
    { 19, 10, 11,  2, 18, 14, 13,  7,  8,  9, 17,  4 },
    {  7, 18, 13, 14,  2, 16, 10, 19, 17, 16,  9, 19, 17, 16,  9,  4,  9, 19, 10, 16,  4,  9,  0, 16,  9, 10,  0, 16, 10,  2,  0, 16 },
    {  1, 12, 15, 16,  2, 10, 11, 19,  4,  8, 17,  9,  7, 13, 14, 18 },
    { 19, 14, 15, 18, 18, 10,  9, 17, 12, 13, 17, 18,  7, 13, 14, 18, 15, 13, 14, 18, 15, 12, 13, 18, 10, 18, 19, 17, 18, 19, 15, 12, 18, 19, 12, 17, 15, 12,  0,  1, 15, 12,  0, 19, 12,  0, 19, 17,  0, 19, 17, 10,  0, 19, 10,  2,  0,  9, 17,  4,  0,  9, 17, 10 },
    { 18, 15, 19,  3, 18, 13, 15,  3, 17,  9,  8,  4,  7,  3, 13, 18 },
    { 19, 15,  3, 13, 19,  3,  7, 13, 19, 18,  7, 13,  0, 11, 16, 17,  0,  4, 11, 17,  4, 11,  9, 17 },
    {  4, 17,  9,  8,  1, 19, 12, 16, 18, 19, 13, 16, 18, 19, 13,  7, 13, 16, 12, 19,  7, 13,  3, 19, 13, 12,  3, 19, 12,  1,  3, 19 },
    { 11, 12,  1, 19, 13, 12, 19,  3, 17, 12,  0, 11, 19,  3,  1, 12, 11, 12,  0,  1, 19,  3,  7, 13, 13, 18, 19,  7,  4, 17, 11,  0,  9,  4, 17, 11, 11, 19, 12, 13, 11, 19, 13, 18, 12, 13, 17, 11, 13, 17, 11,  9,  9, 13, 18, 11 },
    {  4,  9,  8, 17,  7, 15, 18, 13, 11, 15, 10, 13, 11, 15, 10,  2, 10, 13, 18, 15,  2, 10,  3, 15, 10, 18,  3, 15, 18,  7,  3, 15 },
    { 15, 10,  2, 16,  9, 10, 16,  0, 18, 10,  3, 15, 16,  0,  2, 10, 15, 10,  3,  2, 16,  0,  4,  9,  9, 17, 16,  4,  7, 18, 15,  3, 13,  7, 18, 15, 15, 16, 10,  9, 15, 16,  9, 17, 10,  9, 18, 15,  9, 18, 15, 13, 13,  9, 17, 15 },
    { 16,  8, 11, 17, 17, 12, 13, 18, 10,  9, 18, 17,  4,  9,  8, 17, 11,  9,  8, 17, 11, 10,  9, 17, 12, 17, 16, 18, 17, 16, 11, 10, 17, 16, 10, 18, 11, 10,  3,  2, 11, 10,  3, 16, 10,  3, 16, 18,  3, 16, 18, 12,  3, 16, 12,  1,  3, 13, 18,  7,  3, 13, 18, 12 },
    { 17, 12, 13,  0,  9, 18, 10,  3,  9, 13,  3, 18, 13, 18,  7,  3,  4,  0,  9, 17,  0,  9, 17, 13, 13,  9,  0,  3, 13, 12,  3,  0, 12,  0,  1,  3,  9,  0,  3, 10, 10,  0,  2,  3 },
    { 17, 14, 18,  7, 12, 14, 17,  5,  7,  5, 14, 17 },
    { 17, 14, 18,  7, 17, 12, 14,  7, 16,  8, 11,  0,  5,  7, 12, 17 },
    { 14, 16, 15,  5, 14, 18, 16,  5, 18, 17, 16,  5,  5,  1, 16, 15,  5,  7, 14, 18 },
    { 14, 15, 17,  5,  8, 17,  1, 15,  1, 15,  5, 17,  1, 15,  0,  8, 14,  7,  5, 17, 17, 18, 14,  7,  0, 11,  8, 15, 15, 18, 17, 14, 15, 18, 17,  8 },
    { 18, 12, 17,  5, 18, 14, 12,  5, 19, 10, 11,  2,  7,  5, 14, 18 },
    { 16,  8,  0, 10, 16,  0,  2, 10, 16, 19,  2, 10,  5, 12, 17, 18,  5,  7, 12, 18,  7, 12, 14, 18 },
    {  2, 19, 11, 10,  7, 17, 14, 18, 16, 17, 15, 18, 16, 17, 15,  1, 15, 18, 14, 17,  1, 15,  5, 17, 15, 14,  5, 17, 14,  7,  5, 17 },
    {  8, 15,  1, 17, 14, 15, 17,  5, 19, 15,  0,  8, 17,  5,  1, 15,  8, 15,  0,  1, 17,  5,  7, 14, 14, 18, 17,  7,  2, 19,  8,  0, 10,  2, 19,  8,  8, 17, 15, 14,  8, 17, 14, 18, 15, 14, 19,  8, 14, 19,  8, 10, 10, 14, 18,  8 },
    { 12, 19, 15,  7, 12, 17, 19,  7, 17, 18, 19,  7,  7,  3, 19, 15,  7,  5, 12, 17 },
    {  0, 16, 11,  8,  5, 18, 12, 17, 19, 18, 15, 17, 19, 18, 15,  3, 15, 17, 12, 18,  3, 15,  7, 18, 15, 12,  7, 18, 12,  5,  7, 18 },
    { 16, 17, 19,  1, 17, 18, 19,  7,  1,  7, 19, 17,  1,  5,  7, 17,  1,  3,  7, 19 },
    {  8, 19, 11,  1,  8, 17, 19,  1, 17, 18, 19,  7,  0,  1, 11,  8,  7,  3, 19, 17,  3, 19, 17,  1,  7,  3,  1, 17,  7,  5,  1, 17 },
    { 12, 15, 18,  7, 10, 18,  3, 15,  3, 15,  7, 18,  3, 15,  2, 10, 12,  5,  7, 18, 18, 17, 12,  5,  2, 11, 10, 15, 15, 17, 18, 12, 15, 17, 18, 10 },
    { 10, 15,  3, 18, 12, 15, 18,  7, 16, 15,  2, 10, 18,  7,  3, 15, 10, 15,  2,  3, 18,  7,  5, 12, 12, 17, 18,  5,  0, 16, 10,  2,  8,  0, 16, 10, 10, 18, 15, 12, 10, 18, 12, 17, 15, 12, 16, 10, 12, 16, 10,  8,  8, 12, 17, 10 },
    { 10, 16, 11,  3, 10, 18, 16,  3, 18, 17, 16,  5,  2,  3, 11, 10,  5,  1, 16, 18,  1, 16, 18,  3,  5,  1,  3, 18,  5,  7,  3, 18 },
    { 10,  8, 17,  1, 18, 10, 17,  3, 10, 17,  3,  1,  3,  1,  2, 10,  1,  2,  0, 10,  1,  0, 10,  8,  3,  1,  5, 17,  3,  7,  5, 17,  3,  7, 18, 17 },
    { 18,  8,  9,  5, 18, 14,  8,  5, 14, 12,  8,  5,  5,  4,  8,  9,  5,  7, 18, 14 },
    { 18,  9, 12,  5, 16, 12,  4,  9,  4,  9,  5, 12,  4,  9,  0, 16, 18,  7,  5, 12, 12, 14, 18,  7,  0, 11, 16,  9,  9, 14, 12, 18,  9, 14, 12, 16 },
    { 18,  9,  5, 14,  5,  8, 16,  9,  5, 14,  9, 16,  5, 14, 15, 16,  5,  1, 15, 16,  5,  4,  9,  8,  5,  7, 18, 14 },
    { 18, 15, 14,  5, 18,  9, 15,  5,  9, 11, 15,  0,  7,  5, 14, 18,  0,  1, 15,  9,  1, 15,  9,  5,  0,  1,  5,  9,  0,  4,  5,  9 },
    {  2, 10, 11, 19,  7, 12, 18, 14,  8, 12,  9, 14,  8, 12,  9,  4,  9, 14, 18, 12,  4,  9,  5, 12,  9, 18,  5, 12, 18,  7,  5, 12 },
    { 12,  9,  4, 16, 10,  9, 16,  0, 18,  9,  5, 12, 16,  0,  4,  9, 12,  9,  5,  4, 16,  0,  2, 10, 10, 19, 16,  2,  7, 18, 12,  5, 14,  7, 18, 12, 12, 16,  9, 10, 12, 16, 10, 19,  9, 10, 18, 12, 10, 18, 12, 14, 14, 10, 19, 12 },
    { 18, 10,  9, 19, 19, 14, 15, 16,  8, 11, 16, 19,  2, 11, 10, 19,  9, 11, 10, 19,  9,  8, 11, 19, 14, 19, 18, 16, 19, 18,  9,  8, 19, 18,  8, 16,  9,  8,  5,  4,  9,  8,  5, 18,  8,  5, 18, 16,  5, 18, 16, 14,  5, 18, 14,  7,  5, 15, 16,  1,  5, 15, 16, 14 },
    { 19, 15, 14,  0, 10, 18,  9,  5, 10, 14,  5, 18, 14, 18,  7,  5,  2,  0, 10, 19,  0, 10, 19, 14, 14, 10,  0,  5, 14, 15,  5,  0, 15,  0,  1,  5, 10,  0,  5,  9,  9,  0,  4,  5 },
    { 15, 12, 18,  7,  9, 18,  5, 12,  5, 12,  7, 18,  5, 12,  4,  9, 15,  3,  7, 18, 18, 19, 15,  3,  4,  8,  9, 12, 12, 19, 18, 15, 12, 19, 18,  9 },
    {  9, 12,  5, 18, 15, 12, 18,  7, 16, 12,  4,  9, 18,  7,  5, 12,  9, 12,  4,  5, 18,  7,  3, 15, 15, 19, 18,  3,  0, 16,  9,  4, 11,  0, 16,  9,  9, 18, 12, 15,  9, 18, 15, 19, 12, 15, 16,  9, 15, 16,  9, 11, 11, 15, 19,  9 },
    {  8, 18,  9,  5,  8, 16, 18,  5, 16, 19, 18,  3,  4,  5,  9,  8,  3,  7, 18, 16,  7, 18, 16,  5,  3,  7,  5, 16,  3,  1,  5, 16 },
    { 11,  9, 18,  5, 19, 11, 18,  1, 11, 18,  1,  5,  1,  5,  0, 11,  5,  0,  4, 11,  5,  4, 11,  9,  1,  5,  7, 18,  1,  3,  7, 18,  1,  3, 19, 18 },
    { 15, 18,  7, 12,  9, 18, 12,  5, 10, 18,  3, 15, 12,  5,  7, 18, 15, 18,  3,  7, 12,  5,  4,  9,  9,  8, 12,  4,  2, 10, 15,  3, 11,  2, 10, 15, 15, 12, 18,  9, 15, 12,  9,  8, 18,  9, 10, 15,  9, 10, 15, 11, 11,  9,  8, 15 },
    { 10,  9, 18,  3, 16, 15, 12,  4,  2, 15, 16, 10,  2, 10,  3, 15, 10,  3, 15,  9,  3, 15,  7, 18,  3, 15, 18,  9, 18,  9,  5, 12,  4,  5, 12,  9, 10,  9, 15, 16,  9, 15, 16,  4, 15,  9, 12,  4,  9, 12, 15, 18, 12, 15,  7, 18,  7, 18, 12,  5,  9,  4,  0, 16, 10,  9,  0, 16,  2, 10,  0, 16 },
    { 10, 18,  9,  3, 11,  8, 16,  5, 11,  9,  5,  8,  9,  8,  4,  5,  2,  3, 11, 10,  3, 11, 10,  9,  9, 11,  3,  5,  9, 18,  5,  3, 18,  3,  7,  5, 11,  3,  5, 16, 16,  3,  1,  5 },
    { 18,  9, 10,  5, 18,  5,  7,  3, 18, 10,  3,  5,  5,  4,  9,  0,  0,  5,  9, 10,  1,  0,  5, 10,  1,  3,  5, 10,  0,  3,  2, 10,  1,  0,  3, 10 },
    { 14,  9, 10,  6, 13,  9, 14,  7,  6,  7,  9, 14 },
    { 10, 13, 14,  7, 10,  9, 13,  7,  8, 11, 16,  0,  6,  7,  9, 10 },
    { 14,  9, 10,  6, 14, 13,  9,  6, 12, 15, 16,  1,  7,  6, 13, 14 },
    { 15, 12,  1,  8, 15,  1,  0,  8, 15, 11,  0,  8,  7, 14, 13,  9,  7,  6, 14,  9,  6, 14, 10,  9 },
    { 19, 13, 14,  6, 19, 11, 13,  6, 11,  9, 13,  6,  6,  7, 13, 14,  6,  2, 19, 11 },
    {  8,  9, 19,  2, 14, 19,  6,  9,  6,  9,  2, 19,  6,  9,  7, 14,  8,  0,  2, 19, 19, 16,  8,  0,  7, 13, 14,  9,  9, 16, 19,  8,  9, 16, 19, 14 },
    {  1, 15, 12, 16,  2,  9, 19, 11, 13,  9, 14, 11, 13,  9, 14,  7, 14, 11, 19,  9,  7, 14,  6,  9, 14, 19,  6,  9, 19,  2,  6,  9 },
    {  9, 19,  2,  8, 15, 19,  8,  0, 14, 19,  6,  9,  8,  0,  2, 19,  9, 19,  6,  2,  8,  0,  1, 15, 15, 12,  8,  1,  7, 14,  9,  6, 13,  7, 14,  9,  9,  8, 19, 15,  9,  8, 15, 12, 19, 15, 14,  9, 15, 14,  9, 13, 13, 15, 12,  9 },
    { 19,  9, 10,  7, 19, 15,  9,  7, 15, 13,  9,  7,  7,  6,  9, 10,  7,  3, 19, 15 },
    {  0, 11,  8, 16,  3, 13, 19, 15,  9, 13, 10, 15,  9, 13, 10,  6, 10, 15, 19, 13,  6, 10,  7, 13, 10, 19,  7, 13, 19,  3,  7, 13 },
    { 12, 13, 19,  3, 10, 19,  7, 13,  7, 13,  3, 19,  7, 13,  6, 10, 12,  1,  3, 19, 19, 16, 12,  1,  6,  9, 10, 13, 13, 16, 19, 12, 13, 16, 19, 10 },
    { 13, 19,  3, 12, 11, 19, 12,  1, 10, 19,  7, 13, 12,  1,  3, 19, 13, 19,  7,  3, 12,  1,  0, 11, 11,  8, 12,  0,  6, 10, 13,  7,  9,  6, 10, 13, 13, 12, 19, 11, 13, 12, 11,  8, 19, 11, 10, 13, 11, 10, 13,  9,  9, 11,  8, 13 },
    { 11, 15,  9,  2, 15, 13,  9,  7,  2,  7,  9, 15,  2,  3,  7, 15,  2,  6,  7,  9 },
    { 16,  9,  8,  2, 16, 15,  9,  2, 15, 13,  9,  7,  0,  2,  8, 16,  7,  6,  9, 15,  6,  9, 15,  2,  7,  6,  2, 15,  7,  3,  2, 15 },
    { 16, 13, 12,  3, 16, 11, 13,  3, 11,  9, 13,  6,  1,  3, 12, 16,  6,  7, 13, 11,  7, 13, 11,  3,  6,  7,  3, 11,  6,  2,  3, 11 },
    {  9, 13, 12,  3,  8,  9, 12,  2,  9, 12,  2,  3,  2,  3,  6,  9,  3,  6,  7,  9,  3,  7,  9, 13,  2,  3,  1, 12,  2,  0,  1, 12,  2,  0,  8, 12 },
    { 17, 14, 13,  6, 17,  8, 14,  6,  8, 10, 14,  6,  6,  7, 14, 13,  6,  4, 17,  8 },
    { 11, 10, 17,  4, 13, 17,  6, 10,  6, 10,  4, 17,  6, 10,  7, 13, 11,  0,  4, 17, 17, 16, 11,  0,  7, 14, 13, 10, 10, 16, 17, 11, 10, 16, 17, 13 },
    {  1, 12, 15, 16,  4, 10, 17,  8, 14, 10, 13,  8, 14, 10, 13,  7, 13,  8, 17, 10,  7, 13,  6, 10, 13, 17,  6, 10, 17,  4,  6, 10 },
    { 11, 17,  4, 10, 13, 17, 10,  6, 12, 17,  0, 11, 10,  6,  4, 17, 11, 17,  0,  4, 10,  6,  7, 13, 13, 14, 10,  7,  1, 12, 11,  0, 15,  1, 12, 11, 11, 10, 17, 13, 11, 10, 13, 14, 17, 13, 12, 11, 13, 12, 11, 15, 15, 13, 14, 11 },
    { 17, 13,  6,  8,  6, 14, 19, 13,  6,  8, 13, 19,  6,  8, 11, 19,  6,  2, 11, 19,  6,  7, 13, 14,  6,  4, 17,  8 },
    { 14, 17, 13,  6, 14, 19, 17,  6, 19, 16, 17,  0,  7,  6, 13, 14,  0,  4, 17, 19,  4, 17, 19,  6,  0,  4,  6, 19,  0,  2,  6, 19 },
    { 17, 12, 13, 16, 16,  8, 11, 19, 14, 15, 19, 16,  1, 15, 12, 16, 13, 15, 12, 16, 13, 14, 15, 16,  8, 16, 17, 19, 16, 17, 13, 14, 16, 17, 14, 19, 13, 14,  6,  7, 13, 14,  6, 17, 14,  6, 17, 19,  6, 17, 19,  8,  6, 17,  8,  4,  6, 11, 19,  2,  6, 11, 19,  8 },
    { 12, 17, 13,  0, 15, 14, 19,  6, 15, 13,  6, 14, 13, 14,  7,  6,  1,  0, 15, 12,  0, 15, 12, 13, 13, 15,  0,  6, 13, 17,  6,  0, 17,  0,  4,  6, 15,  0,  6, 19, 19,  0,  2,  6 },
    { 17, 13, 10,  6, 19, 10,  7, 13,  7, 13,  6, 10,  7, 13,  3, 19, 17,  4,  6, 10, 10,  8, 17,  4,  3, 15, 19, 13, 13,  8, 10, 17, 13,  8, 10, 19 },
    { 13, 10,  6, 17, 11, 10, 17,  4, 19, 10,  7, 13, 17,  4,  6, 10, 13, 10,  7,  6, 17,  4,  0, 11, 11, 16, 17,  0,  3, 19, 13,  7, 15,  3, 19, 13, 13, 17, 10, 11, 13, 17, 11, 16, 10, 11, 19, 13, 11, 19, 13, 15, 15, 11, 16, 13 },
    { 10, 13,  7, 19, 12, 13, 19,  3, 17, 13,  6, 10, 19,  3,  7, 13, 10, 13,  6,  7, 19,  3,  1, 12, 12, 16, 19,  1,  4, 17, 10,  6,  8,  4, 17, 10, 10, 19, 13, 12, 10, 19, 12, 16, 13, 12, 17, 10, 12, 17, 10,  8,  8, 12, 16, 10 },
    { 12, 13, 17,  0, 19, 11, 10,  7,  1, 11, 19, 12,  1, 12,  0, 11, 12,  0, 11, 13,  0, 11,  4, 17,  0, 11, 17, 13, 17, 13,  6, 10,  7,  6, 10, 13, 12, 13, 11, 19, 13, 11, 19,  7, 11, 13, 10,  7, 13, 10, 11, 17, 10, 11,  4, 17,  4, 17, 10,  6, 13,  7,  3, 19, 12, 13,  3, 19,  1, 12,  3, 19 },
    { 17, 11,  8,  6, 17, 13, 11,  6, 13, 15, 11,  3,  4,  6,  8, 17,  3,  2, 11, 13,  2, 11, 13,  6,  3,  2,  6, 13,  3,  7,  6, 13 },
    { 15, 13, 17,  6, 16, 15, 17,  2, 15, 17,  2,  6,  2,  6,  3, 15,  6,  3,  7, 15,  6,  7, 15, 13,  2,  6,  4, 17,  2,  0,  4, 17,  2,  0, 16, 17 },
    { 16, 11,  8,  3, 12, 17, 13,  6, 12,  8,  6, 17,  8, 17,  4,  6,  1,  3, 12, 16,  3, 12, 16,  8,  8, 12,  3,  6,  8, 11,  6,  3, 11,  3,  2,  6, 12,  3,  6, 13, 13,  3,  7,  6 },
    { 17, 13, 12,  6, 17,  6,  4,  0, 17, 12,  0,  6,  6,  7, 13,  3,  3,  6, 13, 12,  2,  3,  6, 12,  2,  0,  6, 12,  3,  0,  1, 12,  2,  3,  0, 12 },
    { 17, 10,  9,  7, 17, 12, 10,  7, 12, 14, 10,  7,  7,  6, 10,  9,  7,  5, 17, 12 },
    {  0,  8, 11, 16,  5, 14, 17, 12, 10, 14,  9, 12, 10, 14,  9,  6,  9, 12, 17, 14,  6,  9,  7, 14,  9, 17,  7, 14, 17,  5,  7, 14 },
    { 15, 14, 17,  5,  9, 17,  7, 14,  7, 14,  5, 17,  7, 14,  6,  9, 15,  1,  5, 17, 17, 16, 15,  1,  6, 10,  9, 14, 14, 16, 17, 15, 14, 16, 17,  9 },
    { 15, 17,  5, 14,  9, 17, 14,  7,  8, 17,  1, 15, 14,  7,  5, 17, 15, 17,  1,  5, 14,  7,  6,  9,  9, 10, 14,  6,  0,  8, 15,  1, 11,  0,  8, 15, 15, 14, 17,  9, 15, 14,  9, 10, 17,  9,  8, 15,  9,  8, 15, 11, 11,  9, 10, 15 },
    { 17,  9, 14,  7, 19, 14,  6,  9,  6,  9,  7, 14,  6,  9,  2, 19, 17,  5,  7, 14, 14, 12, 17,  5,  2, 11, 19,  9,  9, 12, 14, 17,  9, 12, 14, 19 },
    { 14,  9,  6, 19,  8,  9, 19,  2, 17,  9,  7, 14, 19,  2,  6,  9, 14,  9,  7,  6, 19,  2,  0,  8,  8, 16, 19,  0,  5, 17, 14,  7, 12,  5, 17, 14, 14, 19,  9,  8, 14, 19,  8, 16,  9,  8, 17, 14,  8, 17, 14, 12, 12,  8, 16, 14 },
    {  9, 14,  7, 17, 15, 14, 17,  5, 19, 14,  6,  9, 17,  5,  7, 14,  9, 14,  6,  7, 17,  5,  1, 15, 15, 16, 17,  1,  2, 19,  9,  6, 11,  2, 19,  9,  9, 17, 14, 15,  9, 17, 15, 16, 14, 15, 19,  9, 15, 19,  9, 11, 11, 15, 16,  9 },
    {  8,  9, 17,  1, 19, 15, 14,  6,  0, 15, 19,  8,  0,  8,  1, 15,  8,  1, 15,  9,  1, 15,  5, 17,  1, 15, 17,  9, 17,  9,  7, 14,  6,  7, 14,  9,  8,  9, 15, 19,  9, 15, 19,  6, 15,  9, 14,  6,  9, 14, 15, 17, 14, 15,  5, 17,  5, 17, 14,  7,  9,  6,  2, 19,  8,  9,  2, 19,  0,  8,  2, 19 },
    { 17,  9,  7, 12,  7, 10, 19,  9,  7, 12,  9, 19,  7, 12, 15, 19,  7,  3, 15, 19,  7,  6,  9, 10,  7,  5, 17, 12 },
    { 17,  8,  9, 16, 16, 12, 15, 19, 10, 11, 19, 16,  0, 11,  8, 16,  9, 11,  8, 16,  9, 10, 11, 16, 12, 16, 17, 19, 16, 17,  9, 10, 16, 17, 10, 19,  9, 10,  7,  6,  9, 10,  7, 17, 10,  7, 17, 19,  7, 17, 19, 12,  7, 17, 12,  5,  7, 15, 19,  3,  7, 15, 19, 12 },
    { 10, 17,  9,  7, 10, 19, 17,  7, 19, 16, 17,  1,  6,  7,  9, 10,  1,  5, 17, 19,  5, 17, 19,  7,  1,  5,  7, 19,  1,  3,  7, 19 },
    {  8, 17,  9,  1, 11, 10, 19,  7, 11,  9,  7, 10,  9, 10,  6,  7,  0,  1, 11,  8,  1, 11,  8,  9,  9, 11,  1,  7,  9, 17,  7,  1, 17,  1,  5,  7, 11,  1,  7, 19, 19,  1,  3,  7 },
    { 17, 15, 12,  7, 17,  9, 15,  7,  9, 11, 15,  2,  5,  7, 12, 17,  2,  3, 15,  9,  3, 15,  9,  7,  2,  3,  7,  9,  2,  6,  7,  9 },
    { 16, 15, 12,  2,  8, 17,  9,  7,  8, 12,  7, 17, 12, 17,  5,  7,  0,  2,  8, 16,  2,  8, 16, 12, 12,  8,  2,  7, 12, 15,  7,  2, 15,  2,  3,  7,  8,  2,  7,  9,  9,  2,  6,  7 },
    { 11,  9, 17,  7, 16, 11, 17,  3, 11, 17,  3,  7,  3,  7,  2, 11,  7,  2,  6, 11,  7,  6, 11,  9,  3,  7,  5, 17,  3,  1,  5, 17,  3,  1, 16, 17 },
    { 17,  9,  8,  7, 17,  7,  5,  1, 17,  8,  1,  7,  7,  6,  9,  2,  2,  7,  9,  8,  3,  2,  7,  8,  3,  1,  7,  8,  2,  1,  0,  8,  3,  2,  1,  8 },
    {  8, 12, 10,  4, 12, 14, 10,  7,  4,  7, 10, 12,  4,  5,  7, 12,  4,  6,  7, 10 },
    { 16, 10, 11,  4, 16, 12, 10,  4, 12, 14, 10,  7,  0,  4, 11, 16,  7,  6, 10, 12,  6, 10, 12,  4,  7,  6,  4, 12,  7,  5,  4, 12 },
    { 16, 14, 15,  5, 16,  8, 14,  5,  8, 10, 14,  6,  1,  5, 15, 16,  6,  7, 14,  8,  7, 14,  8,  5,  6,  7,  5,  8,  6,  4,  5,  8 },
    { 11, 15, 14,  5, 10, 11, 14,  4, 11, 14,  4,  5,  4,  5,  0, 11,  5,  0,  1, 11,  5,  1, 11, 15,  4,  5,  7, 14,  4,  6,  7, 14,  4,  6, 10, 14 },
    { 19,  8, 11,  6, 19, 14,  8,  6, 14, 12,  8,  5,  2,  6, 11, 19,  5,  4,  8, 14,  4,  8, 14,  6,  5,  4,  6, 14,  5,  7,  6, 14 },
    { 14, 12, 16,  4, 19, 14, 16,  6, 14, 16,  6,  4,  6,  4,  7, 14,  4,  7,  5, 14,  4,  5, 14, 12,  6,  4,  0, 16,  6,  2,  0, 16,  6,  2, 19, 16 },
    { 16,  8, 11,  5, 15, 19, 14,  6, 15, 11,  6, 19, 11, 19,  2,  6,  1,  5, 15, 16,  5, 15, 16, 11, 11, 15,  5,  6, 11,  8,  6,  5,  8,  5,  4,  6, 15,  5,  6, 14, 14,  5,  7,  6 },
    { 19, 15, 14,  0, 19,  0,  2,  6, 19, 14,  6,  0,  0,  1, 15,  5,  5,  0, 15, 14,  4,  5,  0, 14,  4,  6,  0, 14,  5,  6,  7, 14,  4,  5,  6, 14 },
    { 19, 12, 15,  7, 19, 10, 12,  7, 10,  8, 12,  4,  3,  7, 15, 19,  4,  5, 12, 10,  5, 12, 10,  7,  4,  5,  7, 10,  4,  6,  7, 10 },
    { 16, 12, 15,  4, 11, 19, 10,  7, 11, 15,  7, 19, 15, 19,  3,  7,  0,  4, 11, 16,  4, 11, 16, 15, 15, 11,  4,  7, 15, 12,  7,  4, 12,  4,  5,  7, 11,  4,  7, 10, 10,  4,  6,  7 },
    { 10,  8, 16,  5, 19, 10, 16,  7, 10, 16,  7,  5,  7,  5,  6, 10,  5,  6,  4, 10,  5,  4, 10,  8,  7,  5,  1, 16,  7,  3,  1, 16,  7,  3, 19, 16 },
    { 19, 11, 10,  1, 19,  1,  3,  7, 19, 10,  7,  1,  1,  0, 11,  4,  4,  1, 11, 10,  5,  4,  1, 10,  5,  7,  1, 10,  4,  7,  6, 10,  5,  4,  7, 10 }, // TODO
    { 11, 15, 12,  7,  6,  7,  2, 11,  7,  2,  3, 11,  7,  3, 11, 15,  8, 11,  6,  7,  4,  8,  6,  7,  8, 11, 12,  7,  8, 12,  5,  7,  8,  4,  5,  7 }, 
    { 16, 15, 12,  2,  2,  3, 15,  7,  7,  2, 15, 12,  6,  7,  2, 12,  7,  4,  5, 12,  6,  7,  4, 12,  0,  6,  2, 16,  2, 16,  6, 12,  4, 12,  6, 16,  0, 16,  4,  6 },
    { 16, 11,  8,  3, 16,  3,  1,  7,  6,  7,  4,  8,  4,  8,  5,  7, 16,  3,  8,  7,  8, 16,  5,  7, 16,  1,  5,  7, 11,  6,  2,  7, 11,  8,  6,  7, 11,  3,  8,  7, 11,  2,  3,  7 }, 
    {  0,  3,  1,  7,  0,  5,  1,  7,  0,  5,  4,  7,  0,  3,  2,  7,  0,  6,  2,  7,  0,  6,  4,  7 },
};

} // namespace marchingcubes

} // mlhp
