// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_KDTREE_HPP
#define MLHP_CORE_KDTREE_HPP

#include "mlhp/core/coreexport.hpp"
#include "mlhp/core/alias.hpp"
#include "mlhp/core/mesh.hpp"

namespace mlhp
{
namespace kdtree 
{ 

struct Parameters
{
    size_t maxdepth = 20;
    double KT = 1.0;
    double KL = 2.0;
    double emptyCellBias = 0.8;
};

} // kdtree

template<size_t D> MLHP_EXPORT
KdTree<D> buildKdTree( const kdtree::ObjectProvider<D>& provider,
                       const kdtree::Parameters& parameters = { } );

template<size_t D> MLHP_EXPORT
KdTree<D> buildKdTree( const kdtree::ObjectProvider<D>& provider,
                       const spatial::BoundingBox<D>& bounds,
                       const kdtree::Parameters& parameters = { } );

template<size_t D>
class KdTree final : public AbsMesh<D>
{
public:
    struct Node
    {
        std::uint8_t axis = NoValue<std::uint8_t>;
        std::uint8_t nitems = 0;
        std::int16_t state = 0;

        CellIndex leafOrChild = 0;

        union { double position; size_t offset = 0; } data;
    };

    MLHP_EXPORT
    explicit KdTree( spatial::BoundingBox<D> bounds,
                     std::vector<Node>&& nodes,
                     std::vector<size_t>&& data );
    
    MLHP_EXPORT MeshUniquePtr<D> clone( ) const override;

    // General info
    MLHP_EXPORT MLHP_PURE CellIndex nfull( ) const;
    MLHP_EXPORT MLHP_PURE CellIndex nleaves( ) const;
    MLHP_EXPORT MLHP_PURE CellIndex ncells( ) const override;
    MLHP_EXPORT MLHP_PURE size_t maxdepth( ) const;
    MLHP_EXPORT MLHP_PURE size_t memoryUsage( ) const override;
    MLHP_EXPORT MLHP_PURE spatial::BoundingBox<D> boundingBox( ) const;
      
    // Kdtree intersection
    using LeafCallback = std::function<void( std::span<const size_t> items )>;

    MLHP_EXPORT
    void intersect( const spatial::BoundingBox<D>& bounds,
                    const LeafCallback& callback ) const;

    MLHP_EXPORT
    void intersect( const std::array<double, D>& rayOrigin,
                    const std::array<double, D>& rayDirection,
                    const LeafCallback& callback ) const;
   
    MLHP_EXPORT MLHP_PURE CellIndex fullIndexAt( std::array<double, D> xyz ) const;
    MLHP_EXPORT MLHP_PURE std::span<const size_t> itemsLeaf( CellIndex ileaf ) const;
    MLHP_EXPORT MLHP_PURE std::span<const size_t> itemsFull( CellIndex ifull ) const;

    MLHP_EXPORT 
    void stateFull( CellIndex ifull, std::int16_t state );

    MLHP_EXPORT MLHP_PURE 
    std::int16_t stateFull( CellIndex ifull ) const;

    // Leaf info
    MLHP_EXPORT MLHP_PURE CellType cellType( CellIndex icell ) const override;
    MLHP_EXPORT MLHP_PURE spatial::BoundingBox<D> boundingBox( CellIndex ileaf ) const;

    MLHP_EXPORT
    void neighbours( CellIndex icell, size_t iface, std::vector<MeshCellFace>& target ) const override; // not implemented
  
    // Mapping
    MLHP_EXPORT MeshMapping<D> createMapping( ) const override;
    MLHP_EXPORT void prepareMapping( CellIndex icell, MeshMapping<D>& mapping ) const override;
    MLHP_EXPORT BackwardMappingFactory<D> createBackwardMappingFactory( ) const override; // Not implemented

    // Hierarchy functions
    MLHP_EXPORT MLHP_PURE CellIndex isLeaf( CellIndex ifull ) const;
    MLHP_EXPORT MLHP_PURE CellIndex child( CellIndex ifull, LocalPosition position ) const;
    MLHP_EXPORT MLHP_PURE LocalPosition localPosition( CellIndex ifull ) const;

    MLHP_EXPORT MLHP_PURE std::pair<std::uint8_t, double> split( CellIndex ifull ) const;

    MLHP_EXPORT MLHP_PURE CellIndex fullIndex( CellIndex ileaf ) const;
    MLHP_EXPORT MLHP_PURE CellIndex leafIndex( CellIndex ifull ) const;

private:

    spatial::BoundingBox<D> bounds_;
    std::vector<Node> nodes_;
    std::vector<size_t> data_;
    std::vector<CellIndex> fullIndices_;
    std::vector<CellIndex> parents_;
};

template<size_t D> MLHP_EXPORT
void print( const KdTree<D>& tree, std::ostream& os );

namespace kdtree
{

template<size_t D> MLHP_EXPORT
void accumulateItems( const KdTree<D>& tree, 
                      const spatial::BoundingBox<D>& bounds,
                      std::vector<size_t>& target );

template<size_t D> MLHP_EXPORT
std::vector<size_t> accumulateItems( const KdTree<D>& tree,
                                     const spatial::BoundingBox<D>& bounds );

template<size_t D> MLHP_EXPORT
void accumulateItems( const KdTree<D>& tree, 
                      const std::array<double, D>& rayOrigin,
                      const std::array<double, D>& rayDirection,
                      std::vector<size_t>& target );

template<size_t D> MLHP_EXPORT
std::vector<size_t> accumulateItems( const KdTree<D>& tree,
                                     const std::array<double, D>& rayOrigin,
                                     const std::array<double, D>& rayDirection );

}

// Kdtree implementational details
namespace kdtree
{
    
struct Event
{
    // In the paper they also use:          -           |           +
    enum class Type : std::uint8_t { Ends = 0, Planar = 1, Starts = 2 };

    size_t itriangle;
    double position;
    std::uint8_t axis;
    Type type;
};

template<size_t D> MLHP_EXPORT
std::vector<Event> createSortedEventList( const kdtree::ObjectProvider<D>& provider,
                                          const spatial::BoundingBox<D>& bounds );

template<size_t D> MLHP_EXPORT
std::array<double, 3> computeSurfaceAreaRatios( spatial::BoundingBox<D> bounds,
                                                size_t normal, double position );

using Plane = std::tuple<double, std::uint8_t, std::uint8_t, double>;

template<size_t D> MLHP_EXPORT
Plane findPlane( size_t N, 
                 const spatial::BoundingBox<D>& V, 
                 std::span<const Event> E,
                 const Parameters& parameters );

MLHP_EXPORT
std::vector<size_t> classifyTriangles( std::span<const size_t> indices,
                                       std::span<const Event> E,
                                       Plane plane );

template<size_t D> MLHP_EXPORT 
std::array<spatial::BoundingBox<D>, 2> splitBoundingBox( spatial::BoundingBox<D> bounds, 
                                                         std::uint8_t axis, double position );

} // kdtree
} // mlhp

#endif // MLHP_CORE_KDTREE_HPP
