// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/triangulation.hpp"
#include "mlhp/core/implicit.hpp"
#include "mlhp/core/refinement.hpp"
#include "mlhp/core/postprocessing.hpp"

#include <map>

namespace mlhp
{

using namespace marchingcubes;

TEST_CASE( "readStl_test" )
{
    auto expected = std::vector<std::array<double, 3>>
    {
       // Triangle 0
       { 0.552139, -0.1804, -0.642338 },
       { 0.0417709, -0.857681, -0.112419 },
       { -0.275457, 0.373881, -0.730983 },

       // Triangle 1
       { -0.785825, -0.303401, -0.201064 },
       { -0.275457, 0.373881, -0.730983 },
       { 0.0417709, -0.857681, -0.112419 },

       // Triangle 2
       { -0.552139, 0.1804, 0.642338 },
       { 0.275457, -0.373881, 0.730983 },
       { -0.0417709, 0.857681, 0.112419 },

       // Triangle 3
       { 0.785825, 0.303401, 0.201064 },
       { -0.0417709, 0.857681, 0.112419 },
       { 0.275457, -0.373881, 0.730983 },

       // Triangle 4
       { 0.552139, -0.1804, -0.642338 },
       { -0.275457, 0.373881, -0.730983 },
       { 0.785825, 0.303401, 0.201064 },

       // Triangle 5
       { -0.0417709, 0.857681, 0.112419 },
       { 0.785825, 0.303401, 0.201064 },
       { -0.275457, 0.373881, -0.730983 },

       // Triangle 6
       { -0.552139, 0.1804, 0.642338 },
       { -0.785825, -0.303401, -0.201064 },
       { 0.275457, -0.373881, 0.730983 },

       // Triangle 7
       { 0.0417709, -0.857681, -0.112419 },
       { 0.275457, -0.373881, 0.730983 },
       { -0.785825, -0.303401, -0.201064 },

       // Triangle 8
       { -0.552139, 0.1804, 0.642338 },
       { -0.0417709, 0.857681, 0.112419 },
       { -0.785825, -0.303401, -0.201064 },

       // Triangle 9
       { -0.275457, 0.373881, -0.730983 },
       { -0.785825, -0.303401, -0.201064 },
       { -0.0417709, 0.857681, 0.112419 },

       // Triangle 10
       { 0.552139, -0.1804, -0.642338 },
       { 0.785825, 0.303401, 0.201064 },
       { 0.0417709, -0.857681, -0.112419 },

       // Triangle 11
       { 0.275457, -0.373881, 0.730983 },
       { 0.0417709, -0.857681, -0.112419 },
       { 0.785825, 0.303401, 0.201064 }
    };

    auto stlWritePath = testing::outputPath( "core/readStl_test.stl" );
    auto stlReadPath = testing::testfilePath( "core/readStl_test.stl" );

    writeStl( createTriangulation<3>( expected ), stlWritePath );

    auto triangles1 = readStl( stlReadPath, false );
    auto triangles2 = readStl( stlWritePath, true );

    REQUIRE( triangles1.size( ) == expected.size( ) );
    REQUIRE( triangles2.size( ) == expected.size( ) );

    for( size_t i = 0; i < expected.size( ); ++i )
    {
        CHECK( spatial::distance( triangles1[i], expected[i] ) < 1e-10 );
        CHECK( spatial::distance( triangles2[i], expected[i] ) < 1e-10 );
    }
}

TEST_CASE( "Triangulation_area3D_test" )
{
    auto t = Triangulation<3> { };

    t.vertices =
    {
        { 9.14, 4.44, 4.57 }, { 1.1 , 5.35, 7.79 }, { 7.88, 8.06, 2.04 },
        { 4.2 , 3.56, 5.07 }, { 7.67, 3.42, 2.58 }, { 3.23, 2.49, 4.21 },
        { 9.42, 9.36, 1.33 }, { 4.78, 8.98, 9.22 }, { 7.73, 0.54, 7.07 },
        { 1.62, 4.24, 0.11 }, { 6.53, 8.13, 7.5  }, { 7.94, 9.57, 3.12 },
        { 9.72, 1.79, 3.89 }, { 7.4 , 7.98, 8.43 }, { 4.03, 1.88, 3.92 }
    };

    t.triangles = 
    {
        { 0, 1, 2 }, { 3, 4, 5 }, { 6, 7, 8 }, { 9, 10, 11 }, { 12, 13, 14 }
    };

    CHECK( t.area( ) == Approx( 106.07389660287483 ).epsilon( 1e-10 ) );
}

TEST_CASE( "Triangulation_area2D_test" )
{
    auto t = Triangulation<2> { };

    t.vertices =
    {
       { 0.88, 0.58 }, { 0.65, 0.45 }, { 0.91, 0.31 },
       { 0.25, 0.34 }, { 0.7 , 0.51 }, { 0.28, 0.08 },
       { 0.67, 0.57 }, { 0.91, 0.14 }, { 0.17, 0.49 },
       { 0.69, 0.62 }, { 0.48, 0.79 }, { 0.68, 0.08 },
    };

    t.triangles = 
    {
        { 0, 1, 2 }, { 3, 4, 5 }, { 6, 7, 8 }, { 9, 10, 11 }
    };

    CHECK( t.area( ) == Approx( 0.2687 ).epsilon( 1e-10 ) );
}

//TEST_CASE( "MarchingCubes_test" )
//{
//    // Build Wikipedia CSG geometry example
//    auto sphere = implicit::sphere<3>( { 0.0, 0.0, 0.0 }, 1.0 );
//    auto cube = implicit::cube<3>( { -0.85, -0.85, -0.85 }, { 0.85, 0.85, 0.85 } );
//    auto intersection = implicit::intersect( sphere, cube );
//
//    auto circle = implicit::sphere<2>( { 0, 0 }, 0.4 );
//
//    auto cylinder1 = implicit::extrude( circle, -1.0, 1.0, 0 );
//    auto cylinder2 = implicit::extrude( circle, -1.0, 1.0, 1 );
//    auto cylinder3 = implicit::extrude( circle, -1.0, 1.0, 2 );
//
//    auto cylinders = implicit::add( cylinder1, cylinder2, cylinder3 );
//
//    auto domain = implicit::subtract( intersection, cylinders );
//
//    // Triangulate
//    auto ncells = array::make<size_t, 3>( 20 );
//    auto lengths = array::make<double, 3>( 2.0 );
//    auto origin = array::make<double, 3>( -1.0 );
//
//    auto triangulation1 = marchingCubes( domain, ncells, lengths, origin );
//
//    CHECK( triangulation1.size( ) == 4660 * 9 );
//
//    // writeTriangles( triangulation1, "csg_standard.vtu" );
//
//    auto mesh = makeRefinedGrid<3>( { 4, 4, 4 }, lengths, origin );
//
//    mesh->refine( refineTowardsDomainBoundary( domain, 3 ) );
//
//    auto triangulation2 = marchingCubes( domain, *mesh, 2 );
//
//    CHECK( triangulation2.first.size( ) == 47152 * 9 );
//    CHECK( triangulation2.second.size( ) == 47152 );
//
//    // writeTriangles( triangulation2.first, "csg_mesh.vtu" );
//
//}


auto transformEdges( std::array<size_t, 20>& indexMap )
{
        std::map<size_t, std::array<size_t, 2>> edgeNodesMap
    {
        {  8, { 0, 4 } },
        {  9, { 4, 6 } },
        { 10, { 2, 6 } },
        { 11, { 0, 2 } },
        { 12, { 1, 5 } },
        { 13, { 5, 7 } },
        { 14, { 3, 7 } },
        { 15, { 1, 3 } },
        { 16, { 0, 1 } },
        { 17, { 4, 5 } },
        { 18, { 6, 7 } },
        { 19, { 2, 3 } }
    };

    std::map<std::array<size_t, 2>, size_t> nodesEdgeMap
    {
        { { 0, 4 },  8 },
        { { 4, 6 },  9 },
        { { 2, 6 }, 10 },
        { { 0, 2 }, 11 },
        { { 1, 5 }, 12 },
        { { 5, 7 }, 13 },
        { { 3, 7 }, 14 },
        { { 1, 3 }, 15 },
        { { 0, 1 }, 16 },
        { { 4, 5 }, 17 },
        { { 6, 7 }, 18 },
        { { 2, 3 }, 19 }
    };

    for( size_t iedge = 8; iedge < 20; ++iedge )
    {
        auto [id0, id1] = edgeNodesMap[iedge];

        id0 = indexMap[id0];
        id1 = indexMap[id1];

        indexMap[iedge] = nodesEdgeMap[std::array { std::min( id0, id1 ), std::max( id0, id1 ) }];
    }
}

auto flipMap( size_t axis )
{
    std::array<size_t, 20> indexMap;

    std::iota( indexMap.begin( ), indexMap.end( ), size_t { 0 } );

    for( size_t i = 0; i < 2; ++i )
    {
        for( size_t j = 0; j < 2; ++j )
        {
            auto strides = nd::stridesFor( array::makeSizes<3>( 2 ) );

            auto index0 = nd::linearIndex( strides, array::insert<size_t, 2>( { i, j }, axis, 0 ) );
            auto index1 = nd::linearIndex( strides, array::insert<size_t, 2>( { i, j }, axis, 1 ) );

            std::swap( indexMap[index0], indexMap[index1] );
        }
    }

    transformEdges( indexMap );

    return indexMap;
}

auto rotateMap( size_t axis )
{
    auto vertexMap = std::array<size_t, 8> { };

    if( axis == 0 )
    {
        vertexMap = { 1, 3, 0, 2, 5, 7, 4, 6 };
    }
    else if( axis == 1 )
    {
        vertexMap = { 1, 5, 3, 7, 0, 4, 2, 6 };
    }
    else if( axis == 2 )
    {
        vertexMap = { 2, 3, 6, 7, 0, 1, 4, 5 };
    }

    auto indexMap = std::array<size_t, 20> { };

    std::copy( vertexMap.begin( ), vertexMap.end( ), indexMap.begin( ) );

    transformEdges( indexMap );

    return indexMap;    
}

MLHP_PURE
auto transformIndex( size_t index, const std::array<size_t, 20>& indexMap )
{
    auto result = size_t { 0 };

    for( size_t ivertex = 0; ivertex < 8; ++ivertex )
    {
        result |= index & utilities::binaryPow<size_t>( ivertex ) ? utilities::binaryPow<size_t>( indexMap[ivertex] ) : 0;
    }

    return result;
}

auto flip( size_t index, std::vector<size_t>& indices, size_t axis )
{
    auto indexMap = flipMap( axis );

    for( auto& ivertex : indices )
    {
        ivertex = indexMap[ivertex];
    }

    return transformIndex( index, indexMap );
}

auto rotate( size_t index, std::vector<size_t>& indices, size_t axis, size_t times )
{
    auto indexMap = rotateMap( axis );

    for( size_t i = 0; i < times; ++i )
    {
        for( auto& value : indices )
        {
            value = indexMap[value];
        }
    
        index = transformIndex( index, indexMap );
    }

    return index;
}

auto generateTetrahedraTable( )
{
    auto cases = std::vector<std::pair<size_t, std::vector<size_t>>>
    {
        { size_t { 0b00000000 }, { } },
        { size_t { 0b00000001 }, { 8, 16, 11, 0 } },
        { size_t { 0b11111110 }, { 16, 11, 8, 3, 16, 3, 1, 5, 16, 8, 5, 3, 3, 2, 11, 6, 6, 3, 11, 8, 7, 6, 3, 8, 7, 5, 3, 8, 6, 5, 4, 8, 7, 6, 5, 8 } },
        { size_t { 0b00000011 }, { 12, 11, 8, 0, 15, 11, 12, 1, 0, 1, 11, 12 } },
        { size_t { 0b11111100 }, { 11, 15, 12, 7, 8, 11, 12, 6, 11, 12, 6, 7, 6, 7, 2, 11, 7, 2, 3, 11, 7, 3, 11, 15, 6, 7, 5, 12, 6, 4, 5, 12, 6, 4, 8, 12 } },
        { size_t { 0b00000110 }, { 16, 12, 15, 1, 11, 19, 10, 2 } },
        { size_t { 0b11111001 }, { 16, 12, 15, 4, 11, 19, 10, 7, 11, 15, 7, 19, 15, 19, 3, 7, 0, 4, 11, 16, 4, 11, 16, 15, 15, 11, 4, 7, 15, 12, 7, 4, 12, 4, 5, 7, 11, 4, 7, 10, 10, 4, 6, 7 } },
        { size_t { 0b00011000 }, { 8, 9, 17, 4, 19, 15, 14, 3 } },
        { size_t { 0b11100111 }, { 8, 9, 17, 1, 19, 15, 14, 6, 0, 15, 19, 8, 0, 8, 1, 15, 8, 1, 15, 9, 1, 15, 5, 17, 1, 15, 17, 9, 17, 9, 7, 14, 6, 7, 14, 9, 8, 9, 15, 19, 9, 15, 19, 6, 15, 9, 14, 6, 9, 14, 15, 17, 14, 15, 5, 17, 5, 17, 14, 7, 9, 6, 2, 19, 8, 9, 2, 19, 0, 8, 2, 19 } }, // 19, 15, 6, 0, 15, 14, 6, 7, 19, 6, 2, 0, 8, 9, 0, 1, 0, 1, 15, 6, 0, 1, 9, 6 
        { size_t { 0b00010110 }, { 17, 8, 9, 4, 16, 12, 15, 1, 10, 11, 19, 2 } },
        { size_t { 0b11101001 }, { 17, 8, 9, 16, 16, 12, 15, 19, 10, 11, 19, 16, 0, 11, 8, 16, 9, 11, 8, 16, 9, 10, 11, 16, 12, 16, 17, 19, 16, 17, 9, 10, 16, 17, 10, 19, 9, 10, 7, 6, 9, 10, 7, 17, 10, 7, 17, 19, 7, 17, 19, 12, 7, 17, 12, 5, 7, 15, 19, 3, 7, 15, 19, 12 } },
        { size_t { 0b00000111 }, { 19, 12, 15, 0, 19, 10, 12, 0, 10, 8, 12, 0, 0, 1, 12, 15, 0, 2, 19, 10} },
        { size_t { 0b11111000 }, { 19, 12, 15, 7, 19, 10, 12, 7, 10, 8, 12, 4, 3, 7, 15, 19, 4, 5, 12, 10, 5, 12, 10, 7, 4, 5, 7, 10, 4, 6, 7, 10 } },
        { size_t { 0b00011001 }, { 16, 9, 17, 4, 16, 11, 9, 4, 19, 15, 14, 3, 0, 4, 11, 16 } },
        { size_t { 0b11100110 }, { 9, 14, 7, 17, 15, 14, 17, 5, 19, 14, 6, 9, 17, 5, 7, 14, 9, 14, 6, 7, 17, 5, 1, 15, 15, 16, 17, 1, 2, 19, 9, 6, 11, 2, 19, 9, 9, 17, 14, 15, 9, 17, 15, 16, 14, 15, 19, 9, 15, 19, 9, 11, 11, 15, 16, 9 } },
        { size_t { 0b00001111 }, { 8, 12, 10, 0, 12, 14, 10, 3, 0, 3, 10, 12, 0, 1, 3, 12, 0, 2, 3, 10 } },
        { size_t { 0b00010111 }, { 19, 15, 0, 10, 0, 12, 17, 15, 0, 10, 15, 17, 0, 10, 9, 17, 0, 4, 9, 17, 0, 1, 15, 12, 0, 2, 19, 10 } },
        { size_t { 0b00011011 }, { 19, 11, 12, 1, 17, 12, 0, 11, 0, 11, 1, 12, 0, 11, 4, 17, 19, 3, 1, 12, 12, 14, 19, 3, 4, 9, 17, 11, 11, 14, 12, 19, 11, 14, 12, 17} }, 
        { size_t { 0b00011110 }, { 4, 8, 9, 17, 1, 14, 16, 12, 10, 14, 11, 12, 10, 14, 11, 2, 11, 12, 16, 14, 2, 11, 3, 14, 11, 16, 3, 14, 16, 1, 3, 14 } },
        { size_t { 0b01011010 }, { 16, 12, 1, 14, 16, 1, 3, 14, 16, 19, 3, 14, 4, 8, 17, 18, 4, 6, 8, 18, 6, 8, 10, 18 } },
        { size_t { 0b01101001 }, { 0, 8, 11, 16, 3, 14, 15, 19, 5, 12, 17, 13, 6, 9, 10, 18 } },
        { size_t { 0b11111111 }, { 0, 1, 2, 4, 1, 2, 3, 7, 1, 2, 4, 7, 1, 4, 5, 7, 2, 4, 6, 7 } }
    };

    auto table = std::vector<std::vector<size_t>>( 256, std::vector<size_t> { } );

    for( auto [index, tets] : cases )
    {
        for( size_t irotation = 0; irotation < 4; ++irotation )
        {
            for( size_t jrotation = 0; jrotation < 4; ++jrotation )
            {
                for( size_t krotation = 0; krotation < 4; ++krotation )
                {
                    for( size_t iflip = 0; iflip < 2; ++iflip )
                    {
                        for( size_t jflip = 0; jflip < 2; ++jflip )
                        {
                            for( size_t kflip = 0; kflip < 2; ++kflip )
                            {
                                auto newTets = tets;
                                auto newIndex = index;

                                newIndex = rotate( newIndex, newTets, 0, irotation );
                                newIndex = rotate( newIndex, newTets, 1, jrotation );
                                newIndex = rotate( newIndex, newTets, 2, krotation );
                                
                                if( iflip ) newIndex = flip( newIndex, newTets, 0 );
                                if( jflip ) newIndex = flip( newIndex, newTets, 1 );
                                if( kflip ) newIndex = flip( newIndex, newTets, 2 );

                                if( table[newIndex].empty( ) && !newTets.empty( ) )
                                {
                                    table[newIndex] = newTets;
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    size_t count = 1;

    for( size_t index = 0; index < 256; ++index )
    {
        count += !table[index].empty( ) ? size_t { 1 } : size_t { 0 };
 
        std::cout << "    { ";
    
        if( !table[index].empty( ) )
        {
            std::cout << table[index].front( );
        }
    
        for( size_t i = 1; i < table[index].size( ); ++i )
        {
            std::cout << ", " << table[index][i];
        }
    
        std::cout << " }," << std::endl;
    }

    std::cout << count << " / 256 entries" << std::endl;

    return table;
}

TEST_CASE( "intersectTriangulationWithMesh_test1" )
{
    auto vertices = CoordinateList<3> { { 2.0, -3.0, 1.0 }, { 2.2, -3.1, 2.0 }, 
                                        { 2.0, -2.0, 1.0 }, { 2.2, -2.1, 2.0 },
                                        { 3.5, -3.0, 0.9 }, { 3.3, -3.1, 2.0 }, 
                                        { 3.5, -2.0, 0.9 }, { 3.3, -2.1, 2.0 },
                                        { 5.0, -3.0, 0.8 }, { 4.8, -3.1, 2.0 },
                                        { 5.0, -2.0, 0.8 }, { 4.8, -2.1, 2.0 } };

    auto cells = std::vector<size_t> { 0, 1, 2, 3, 4, 5, 6, 7, 4, 5, 6, 7, 8, 9, 10, 11 };
    auto offsets = std::vector<size_t> { 0, 8, 16 };

    auto mesh = UnstructuredMesh<3> { std::move( vertices ), std::move( cells ), std::move( offsets ) };

    auto triangulation = Triangulation<3>
    {  
        .vertices = { { 3.7, -2.9, -0.2 }, { 3.2, -2.6, 2.55 }, { 3.4, -2.1, 1.45 } },
        .triangles = { { 0, 1, 2 } }
    };

    auto [intersected, celldata] = intersectTriangulationWithMesh( mesh, triangulation, buildKdTree( triangulation ) );

    MLHP_CHECK( intersected.ntriangles( ) == 3, "" );

    //writeOutput( mesh, cellmesh::createGrid<3>( { 2, 2, 2 } ), CellProcessor<3> { }, VtuOutput { "mesh.vtu" } );
    //writeStl( triangulation, "triangle.stl" );
    //writeStl( intersected, "triangleIntersected.stl" );
}

TEST_CASE( "intersectTriangulationWithMesh_test2" )
{
    auto triangulation = Triangulation<3>
    {
        .vertices = { { -1.8, -4.0, -0.2 }, { -1.8, -2.6, 2.55 }, { -1.8, -2.1, 1.45 } },
        .triangles = { { 0, 1, 2 } }
    };

    // Unrefined
    auto mesh = makeRefinedGrid<3>( { 2, 1, 1 }, { 2.4, 1.8, 1.4 }, { -3.0, -4.0, 1.0 } );

    auto result = intersectTriangulationWithMesh( *mesh, triangulation, buildKdTree( triangulation ) );

    auto intersected = std::get<0>( result );
    auto celldata = std::get<1>( result );

    auto area = [&]( )
    {
        return spatial::triangleArea<3>( intersected.triangleVertices( 0 ) ) +
               spatial::triangleArea<3>( intersected.triangleVertices( 1 ) ) +
               spatial::triangleArea<3>( intersected.triangleVertices( 2 ) ) +
               spatial::triangleArea<3>( intersected.triangleVertices( 3 ) );
    };

    MLHP_CHECK( intersected.ntriangles( ) == 4, "" );
    MLHP_CHECK( std::abs( area( ) - 0.9687715311 ) < 1e-8, "" );

    // Right side refined
    mesh->refine( refineCellIndices<3>( { { 1 }, { 1, 3 } } ) );

    intersected = intersectTriangulationWithMesh( *mesh, triangulation, buildKdTree( triangulation ) ).first;

    MLHP_CHECK( intersected.ntriangles( ) == 4, "" );
    MLHP_CHECK( std::abs( area( ) - 0.9687715311 ) < 1e-8, "" );

    // Left side refined
    mesh = makeRefinedGrid<3>( { 2, 1, 1 }, { 2.4, 1.8, 1.4 }, { -3.0, -4.0, 1.0 } );

    mesh->refine( refineCellIndices<3>( { { 0 }, { 5, 7 } } ) );

    MLHP_CHECK( intersected.ntriangles( ) == 4, "" );
    MLHP_CHECK( std::abs( area( ) - 0.9687715311 ) < 1e-8, "" );
                        
    //writeOutput( *mesh, cellmesh::createGrid<3>( { 2, 2, 2 } ), CellProcessor<3> { }, VtuOutput { "mesh.vtu" } );
    //writeStl( triangulation, "triangle.stl" );
    //writeStl( intersected, "triangleIntersected.stl" );
}

TEST_CASE( "marchingCubesBoundary_test" )
{
    auto domain = implicit::halfspace<3>( { 4.0, 2.0, 3.1 }, { 3.0, 2.0, 5.0 } );
    auto mesh = makeRefinedGrid<3>( { 2, 1, 2 }, { 3.0, 2.5, 3.2 }, { 1.4, 0.9, 1.3 } );

    // We don't expect to get these exactly since the bisection algorithm 
    // terminates early. They were determined from using many iterations.
    auto expectedXyz = std::vector<std::array<double, 3>>
    {
        { 2.9, 2.15, 3.7 }, { 2.9, 0.9, 4.2 }, { 2.4, 0.9, 4.5 }, 
        { 47.0 / 30.0, 2.15, 4.5 }, { 1.4, 2.4, 4.5 }, { 1.4, 3.4, 4.1 }, 
        { 2.9, 3.4, 3.2 }, { 4.4, 2.15, 2.8 }, { 4.4, 1.9, 2.9 }, 
        { 127.0 / 30.0, 2.15, 2.9 }, { 4.4, 3.4, 2.3 }, { 3.4, 3.4, 2.9 },
        { 4.4, 1.9, 2.9 }, { 2.9, 2.15, 3.7 }, { 127.0 / 30.0, 2.15, 2.9 },
        { 4.4, 0.9, 3.3 }, { 2.9, 0.9, 4.2 }, { 2.9, 3.4, 3.2 }, 
        { 3.4, 3.4, 2.9 }
    };

    auto expectedTriangles = std::vector<std::array<size_t, 3>>
    {
        { 0,  1,  2, }, { 3,  0,  2, }, { 3,  4,  5, }, { 3,  5,  0, },
        { 0,  5,  6, }, { 7,  8,  9, }, { 10, 7,  9, }, { 11, 10, 9, },
        { 12, 13, 14 }, { 12, 15, 13 }, { 15, 16, 13 }, { 14, 17, 18 },
        { 13, 17, 14 },
    };

    auto expectedRst = std::vector<std::array<double, 3>>
    {
        { 1.0, 0.0, 0.0 }, { 1.0, -1.0, 0.625 }, { 1.0 / 3.0, -1.0, 1.0 },
        { -7.0 / 9.0, 0.0, 1.0 }, { -1.0, 0.2, 1.0 }, { -1.0, 1.0, 0.5 },
        { 1.0, 1.0, -0.625 }, { 1.0, 0.0, 0.875 }, { 1.0, -0.2, 1.0 },
        { 7.0 / 9.0, 0.0, 1.0 }, { 1.0, 1.0, 0.25 }, { -1.0 / 3.0, 1.0, 1.0 },
        { 1.0, -0.2, -1.0 }, { -1.0, 0.0, 0.0 }, { 7.0 / 9.0, 0.0, -1.0 },
        { 1.0, -1.0, -0.5 }, { -1.0, -1.0, 0.625 }, { -1.0, 1.0, -0.625 },
        { -1.0 / 3.0, 1.0, -1.0 }
    };

    auto expectedOffsets = std::vector<size_t> 
    { 
        0, 0, 5, 8, 13 
    };

    auto [triangulation, celldata] = marchingCubesBoundary( *mesh, domain, { 1, 2, 1 } );

    CHECK( triangulation.triangles == expectedTriangles );
    CHECK( celldata.offsets == expectedOffsets );

    CHECK( triangulation.vertices.size( ) == expectedXyz.size( ) );
    CHECK( celldata.rst.size( ) == expectedRst.size( ) );

    for( size_t ivertex = 0; ivertex < expectedRst.size( ); ++ivertex )
    {
        CHECK( spatial::distance( triangulation.vertices[ivertex], expectedXyz[ivertex] ) < 1.6e-3 );
        CHECK( spatial::distance( celldata.rst[ivertex], expectedRst[ivertex] ) < 2.0e-3 );
    }

    //auto output1 = VtuOutput { "outputs/marchingCubesBoundary_global_mesh" };
    //auto output2 = VtuOutput { "outputs/marchingCubesBoundary_global_triangles" };

    //writeOutput( *mesh, cellmesh::createGrid<3>( ), CellProcessor<3> { }, output1 );
    //writeOutput( *mesh, cellmesh::associatedTriangles( triangulation, celldata ), CellProcessor<3> { }, output2 );
}

//TEST_CASE( "MarchingCubesVolume_test" )
//{
    // auto tetTable = generateTetrahedraTable( );

    // auto indices1 = tetrahedra[63];
    // 
    // rotate( indices1, 1, 1 );
    // flip( indices1, 2 );
    // flip( indices1, 1 );
    // 
    // std::cout << "New indices: " << indices1.front( );
    // for( size_t i = 1; i < indices1.size( ); ++i )
    // {
    //     std::cout << ", " << indices1[i];
    // }
    // std::cout << std::endl;
    


    // =========================



    // std::vector<double> points
    // {
    //     -1.0, -1.0, -1.0, //  0
    //     -1.0, -1.0,  1.0, //  1
    //     -1.0,  1.0, -1.0, //  2
    //     -1.0,  1.0,  1.0, //  3
    //      1.0, -1.0, -1.0, //  4
    //      1.0, -1.0,  1.0, //  5
    //      1.0,  1.0, -1.0, //  6
    //      1.0,  1.0,  1.0, //  7
    //      0.0, -1.0, -1.0, //  8 { 0, 4 },
    //      1.0,  0.0, -1.0, //  9 { 4, 6 },
    //      0.0,  1.0, -1.0, // 10 { 6, 2 },
    //     -1.0,  0.0, -1.0, // 11 { 2, 0 },
    //      0.0, -1.0,  1.0, // 12 { 1, 5 },
    //      1.0,  0.0,  1.0, // 13 { 5, 7 },
    //      0.0,  1.0,  1.0, // 14 { 7, 3 },
    //     -1.0,  0.0,  1.0, // 15 { 3, 1 },
    //     -1.0, -1.0,  0.0, // 16 { 0, 1 },
    //      1.0, -1.0,  0.0, // 17 { 4, 5 },
    //      1.0,  1.0,  0.0, // 18 { 6, 7 },
    //     -1.0,  1.0,  0.0  // 19 { 2, 3 }
    // };
    // 
    // for( size_t index = 0; index < 256; ++index )
    // {
    //     std::vector<double> values( 8, 0.0 );
    // 
    //     for( size_t i = 0; i < 8; ++i )
    //     {
    //         values[i] = ( index & utilities::binaryPow<size_t>( i ) ) > 0 ? 1.0 : 0.0;
    //     }
    // 
    //     auto write = [&]( std::string name, auto indices, size_t n )
    //     {
    //         std::vector<std::int64_t> connectivity( indices.size( ) );
    //         std::vector<std::int64_t> offsets( indices.size( ) / n );
    //         std::vector<std::int8_t> types( indices.size( ) / n, n == 4 ? 10 : 5 );
    //         
    //         for( size_t itet = 0; itet < indices.size( ) / n; ++itet )
    //         {
    //             offsets[itet] = static_cast<std::int64_t>( ( itet + 1 ) * n );
    //         
    //             for( size_t ivertex = 0; ivertex < n; ++ivertex )
    //             {
    //                 connectivity[itet * n + ivertex] = static_cast<std::int64_t>( indices[itet * n + ivertex] );
    //             }
    //         }
    //         
    //         writeVtu( name + "_" + std::to_string( index ) + ".vtu", points, connectivity, offsets, types );
    //     };
    // 
    //     write( "tets", tetrahedra[index], 4 );
    // 
    //     auto triIndices = std::vector<size_t> { };
    // 
    //     for( size_t i = triangleIndices[index]; i < triangleIndices[index + 1]; ++i )
    //     {
    //         triIndices.push_back( triangleData[3 * i + 0] + 8 );
    //         triIndices.push_back( triangleData[3 * i + 1] + 8 );
    //         triIndices.push_back( triangleData[3 * i + 2] + 8 );
    //     }
    // 
    //     write( "triangles", triIndices, 3 );
    // 
    //     std::vector<double> corners( 3 * 8 );
    // 
    //     std::copy( points.begin( ), points.begin( ) + 3 * 8, corners.begin( ) );
    // 
    //     writeVtu( "box_" + std::to_string( index ) + ".vtu", corners, { 0, 1, 2, 3, 4, 5, 6, 7 }, { 8 }, { 11 }, values );
    // }
//}

} // namespace mlhp
