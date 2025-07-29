// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_TRIANGULATION_HPP
#define MLHP_CORE_TRIANGULATION_HPP

#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/alias.hpp"
#include "mlhp/core/mesh.hpp"
#include "mlhp/core/partitioning.hpp"
#include "mlhp/core/kdtree.hpp"

namespace mlhp
{

template<size_t D>
struct Triangulation
{
    auto ntriangles( ) const { return triangles.size( ); }
    auto nvertices( ) const { return vertices.size( ); }

    MLHP_EXPORT MLHP_PURE
    std::array<size_t, 3> triangleIndices( size_t itriangle ) const;
    
    MLHP_EXPORT MLHP_PURE
    spatial::Triangle<D> triangleVertices( size_t itriangle ) const;

    MLHP_EXPORT
    spatial::BoundingBox<D> boundingBox( ) const;
    
    MLHP_EXPORT
    spatial::BoundingBox<D> boundingBox( size_t itriangle ) const;

    MLHP_EXPORT
    double area( ) const;

    MLHP_EXPORT MLHP_PURE
    size_t memoryUsage( ) const;

    std::vector<std::array<double, D>> vertices;
    std::vector<std::array<size_t, 3>> triangles;
};

MLHP_EXPORT
std::array<double, 3> integrateNormalComponents( const Triangulation<3>& triangulation, bool abs );

//! Read stl into vertex list
MLHP_EXPORT
CoordinateList<3> readStl( const std::string& filename,
                           bool flipOnOppositeNormal = false );

//! Create triangulation from vertex list
template<size_t D> MLHP_EXPORT
Triangulation<D> createTriangulation( CoordinateConstSpan<D> vertices );

MLHP_EXPORT
size_t countIntersections( const KdTree<3>& tree,
                           const Triangulation<3>& triangulation,
                           const std::array<double, 3>& rayOrigin,
                           const std::array<double, 3>& rayDirection,
                           std::vector<size_t>& triangleTarget );

class TriangulationDomain
{
public:
    using TriangulationPtr = memory::vptr<Triangulation<3>>;
    using KdTreePtr = memory::vptr<KdTree<3>>;

    MLHP_EXPORT
    TriangulationDomain( const TriangulationPtr& triangulation,
                         const KdTreePtr& kdTree );

    MLHP_EXPORT
    bool inside( std::array<double, 3> xyz, std::vector<size_t>&) const;

private:
    TriangulationPtr triangulation_;
    KdTreePtr kdtree_;
};

MLHP_EXPORT
ImplicitFunction<3> makeTriangulationDomain( memory::vptr<Triangulation<3>> triangulation,
                                             memory::vptr<KdTree<3>> kdtree );

MLHP_EXPORT
ImplicitFunction<3> makeTriangulationDomain( memory::vptr<Triangulation<3>> triangulation );

MLHP_EXPORT
ImplicitFunction<3> makeTriangulationDomain( const std::string& stlfile );

template<size_t D> MLHP_EXPORT
KdTree<D> buildKdTree( const Triangulation<D>& triangulation,
                       const kdtree::Parameters& parameters = { } );

template<size_t D> MLHP_EXPORT
KdTree<D> buildKdTree( const Triangulation<D>& triangulation,
                       const spatial::BoundingBox<D>& bounds,
                       const kdtree::Parameters& parameters = { } );

template<size_t D>
struct TriangleCellAssociation
{
    MLHP_EXPORT MLHP_PURE
    size_t memoryUsage( ) const;

    //! Local coordinates corresponding to Triangulation<D>::vertices
    std::vector<std::array<double, D>> rst;

    //! For each cell gives the range of triangles in Triangulation<D>::triangles.
    //! In other words: a given cell with index icell is associated with the 
    //! triangles with indices in the range [offsets[icell], offsets[icell + 1])
    std::vector<size_t> offsets;
};

template<size_t D>
using CellAssociatedTriangulation = std::pair<Triangulation<D>, TriangleCellAssociation<D>>;

MLHP_EXPORT
CellAssociatedTriangulation<3> intersectTriangulationWithMesh( const AbsMesh<3>& mesh,
                                                               const Triangulation<3>& triangulation,
                                                               const KdTree<3>& tree );

MLHP_EXPORT
CellAssociatedTriangulation<3> marchingCubesBoundary( const AbsMesh<3>& mesh,
                                                      const ImplicitFunction<3>& function,
                                                      std::array<size_t, 3> resolution );

// Only instantiated for D = 3
template<size_t D>
class TriangulationQuadrature : public AbsQuadratureOnMesh<D>
{
public:
    MLHP_EXPORT
    TriangulationQuadrature( memory::vptr<Triangulation<D>> triangulation,
                             memory::vptr<TriangleCellAssociation<D>> celldata,
                             size_t degree );
      
    MLHP_EXPORT
    std::any initialize( ) const override { return { }; }

    MLHP_EXPORT
    void distribute( const MeshMapping<D>& mapping,
                     CoordinateList<D>& rst,
                     CoordinateList<D>& normals,
                     std::vector<double>& weights,
                     std::any& cache ) const override;

private:
    memory::vptr<Triangulation<D>> triangulation_;
    memory::vptr<TriangleCellAssociation<D>> celldata_;

    std::vector<std::array<double, 2>> rs_;
    std::vector<double> weights_;
};

template<size_t D> MLHP_EXPORT
Triangulation<D> filterTriangulation( const Triangulation<D>& triangulation,
                                      const ImplicitFunction<D>& function,
                                      size_t nseedpoints = 2 );


template<size_t D> MLHP_EXPORT
CellAssociatedTriangulation<D> filterTriangulation( const Triangulation<D>& triangulation,
                                                    const TriangleCellAssociation<D>& celldata,
                                                    const ImplicitFunction<D>& function,
                                                    size_t nseedpoints = 2 );

namespace kdtree
{

template<size_t D> MLHP_EXPORT
kdtree::ObjectProvider<D> makeTriangleProvider( const Triangulation<D>& triangulation, bool clip = true );

}

//! Standard marching cubes
MLHP_EXPORT
Triangulation<3> marchingCubes( const ImplicitFunction<3>& function,
                                std::array<size_t, 3> ncells,
                                std::array<double, 3> lengths,
                                std::array<double, 3> origin = { } );

// Concepts to replace linker errors due to missing instantiation with compiler errors.
template <typename T>
concept MarchingCubesIndex = std::is_same_v<T, size_t> ||
                             std::is_same_v<T, std::int64_t>;

// Marching cubes in local coordinates. Creates actual cube shapes for uncut cubes.
template<MarchingCubesIndex IndexType> MLHP_EXPORT
void marchingCubesBoundary( const AbsMapping<3>& mapping,
                            const ImplicitFunction<3>& function,
                            const std::vector<bool>& evaluations,
                            const CoordinateGrid<3>& rstGrid,
                            std::array<size_t, 3> resolution,
                            CoordinateList<3>& rstList,
                            std::vector<IndexType>& triangles,
                            std::any& anyCache );

template<MarchingCubesIndex IndexType> MLHP_EXPORT
void marchingCubesVolume( const AbsMapping<3>& mapping,
                          const ImplicitFunction<3>& function,
                          const std::vector<bool>& evaluations,
                          const CoordinateGrid<3>& rstGrid,
                          std::array<size_t, 3> resolution,
                          CoordinateList<3>& rstList,
                          std::vector<IndexType>& connectivity,
                          std::vector<IndexType>& offsets,
                          bool meshBothSides,
                          std::any& anyCache );

//using CellAssociatedTriangles = std::pair<std::vector<double>, std::vector<CellIndex>>;
//
////! Marching cubes on mesh cells
//MLHP_EXPORT
//CellAssociatedTriangles marchingCubes( const ImplicitFunction<3>& function,
//                                       const AbsMesh<3>& mesh, 
//                                       size_t ncellsPerDirection );


// Marching cubes implementational details
namespace marchingcubes
{

MLHP_EXPORT
extern std::vector<std::vector<size_t>> tetrahedra;

MLHP_EXPORT
extern std::array<std::uint8_t, 2460> triangleData;

MLHP_EXPORT
extern std::array<std::uint16_t, 257> triangleIndices;

MLHP_EXPORT
extern std::array<std::uint16_t, 256> edgeTable;

MLHP_EXPORT
extern std::array<std::array<size_t, 2>, 12> numbering;

MLHP_EXPORT
std::array<double, 3> interpolate( const ImplicitFunction<3>& function,
                                   std::array<double, 3> c1, bool v1,
                                   std::array<double, 3> c2, bool v2 );

MLHP_EXPORT
std::array<double, 3> interpolate( const ImplicitFunction<3>& function,
                                   const AbsMapping<3>& mapping,
                                   std::array<double, 3> c1, bool v1,
                                   std::array<double, 3> c2, bool v2 );

MLHP_EXPORT
void evaluateGrid( const AbsMapping<3>& mapping,
                   const ImplicitFunction<3>& function,
                   std::array<size_t, 3> resolution,
                   std::array<std::vector<double>, 3>& rstGrid,
                   std::vector<bool>& evaluations );

} // marchingcubes
} // mlhp

#endif // MLHP_CORE_TRIANGULATION_HPP
