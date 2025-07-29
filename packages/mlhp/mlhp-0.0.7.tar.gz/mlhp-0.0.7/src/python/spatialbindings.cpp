// This file is part of the mlhp project. License: See LICENSE

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "src/python/pymlhpcore.hpp"
#include "mlhp/core/spatial.hpp"
#include "mlhp/core/triangulation.hpp"
#include "mlhp/core/postprocessing.hpp"
#include "mlhp/core/implicit.hpp"

namespace mlhp::bindings
{
namespace parser
{

// Define expressions
struct Constant
{
    double value;

    static std::optional<Constant> create( const std::vector<std::string>& expression, size_t )
    {
        return expression[0] == "Constant" ? std::optional<Constant> { Constant { std::stod( expression[1] ) } } : std::nullopt;
    }
};

struct Input
{
    size_t index;

    static std::optional<Input> create( const std::vector<std::string>& expression, size_t ndim )
    {
        if( expression[0] == "Input" )
        {
            auto index = std::stoi( expression[1] );
            auto intdim = static_cast<int>( ndim );

            MLHP_CHECK( index >= 0 && index < intdim, "Invalid input variable index " + std::to_string( index )
                + ". Must be at least 0 and smaller than ndim (" + std::to_string( ndim ) + ")." );

            return Input { static_cast<size_t>( index ) };
        }

        return std::nullopt;
    }
};

struct UnaryOp
{
    long index;
    std::function<double(double)> op;

    static std::optional<UnaryOp> create( const std::vector<std::string>& expr, size_t )
    {
        if( ( expr[0] == "Call" || expr[0] == "UnaryOp" ) && expr.size( ) == 3 )
        {
            using StdPair = std::pair<const char*, double(*)(double)>;

            auto stdfunctions = std::array
            {
                StdPair { "abs"   , std::abs    }, StdPair { "exp"   , std::exp    }, StdPair { "exp2"  , std::exp2  },
                StdPair { "expm1" , std::expm1  }, StdPair { "log"   , std::log    }, StdPair { "log10" , std::log10 },
                StdPair { "log2"  , std::log2   }, StdPair { "log1p" , std::log1p  }, StdPair { "sqrt"  , std::sqrt  },
                StdPair { "qbrt"  , std::cbrt   }, StdPair { "sin"   , std::sin    }, StdPair { "cos"   , std::cos   },
                StdPair { "tan"   , std::tan    }, StdPair { "asin"  , std::asin   }, StdPair { "acos"  , std::acos  },
                StdPair { "atan"  , std::atan   }, StdPair { "sinh"  , std::sinh   }, StdPair { "cosh"  , std::cosh  },
                StdPair { "tanh"  , std::tanh   }, StdPair { "asing" , std::asinh  }, StdPair { "acosh" , std::acosh },
                StdPair { "atanh" , std::atanh  }, StdPair { "erf"   , std::erf    }, StdPair { "erfc"  , std::erfc  },
                StdPair { "tgamma", std::tgamma }, StdPair { "lgamma", std::lgamma }, StdPair { "ceil"  , std::ceil  },
                StdPair { "floor" , std::floor  }, StdPair { "trunc" , std::trunc  }, StdPair { "round" , std::round },
            };
            
            auto id = std::stol( expr[2] );
            
            for( auto [name, ptr] : stdfunctions )
            {
                if( expr[1] == name ) return UnaryOp { id, ptr };
            }

            if( expr[1] == "sign"   ) return UnaryOp { id, []( double x ) noexcept { return x >= 0.0 ? 1.0 : 0.0; } };
            if( expr[1] == "UAdd"   ) return UnaryOp { id, []( double x ) noexcept { return +x; } };
            if( expr[1] == "USub"   ) return UnaryOp { id, []( double x ) noexcept { return -x; } };
            if( expr[1] == "Not"    ) return UnaryOp { id, []( double x ) noexcept { return x == 0.0; } };
            if( expr[1] == "Invert" ) return UnaryOp { id, []( double x ) noexcept { return x - 1.0; } };
        }

        return std::nullopt;
    }
};

struct BinaryOp
{
    long left, right;
    std::function<double(double, double)> op;

    static std::optional<BinaryOp> create( const std::vector<std::string>& expr, size_t )
    {
        if( ( expr[0] == "BinOp" || expr[0] == "Call" || expr[0] == "Compare" || expr[0] == "BoolOp" ) && expr.size( ) == 4 )
        {
            using StdPair = std::pair<const char*, double(*)(double, double)>;
            using CustomPair = std::pair<const char*, decltype( op )>;

            auto stdfunctions = std::array
            {
                StdPair { "pow" , std::pow }, StdPair { "Pow" , std::pow }, StdPair { "hypot" , std::hypot }, 
                StdPair { "atan2" , std::atan2 }, StdPair { "mod" , std::fmod }, StdPair { "remainder" , std::remainder },
            };
                      
            auto customfunctions = std::array 
            {
                CustomPair { "Add",   []( double l, double r ) noexcept { return l + r; } },
                CustomPair { "Sub",   []( double l, double r ) noexcept { return l - r; } },
                CustomPair { "Mult",  []( double l, double r ) noexcept { return l * r; } },
                CustomPair { "Div",   []( double l, double r ) noexcept { return l / r; } },
                CustomPair { "Eq",    []( double l, double r ) noexcept { return l == r; } },
                CustomPair { "NotEq", []( double l, double r ) noexcept { return l != r; } },
                CustomPair { "Lt",    []( double l, double r ) noexcept { return l < r; } },
                CustomPair { "LtE",   []( double l, double r ) noexcept { return l <= r; } },
                CustomPair { "Gt",    []( double l, double r ) noexcept { return l > r; } },
                CustomPair { "GtE",   []( double l, double r ) noexcept { return l >= r; } },
                CustomPair { "And",   []( double l, double r ) noexcept { return l && r; } },
                CustomPair { "Or",    []( double l, double r ) noexcept { return l || r; } },
                CustomPair { "Mod",   []( double l, double r ) noexcept { return std::fmod( l, r ); } },
                CustomPair { "max",   []( double l, double r ) { return std::max( l, r ); } },
                CustomPair { "min",   []( double l, double r ) { return std::min( l, r ); } }
            };
  
            auto id1 = std::stol( expr[2] );
            auto id2 = std::stol( expr[3] );
                        
            for( auto [name, ptr] : stdfunctions )
            {
                if( expr[1] == name ) return BinaryOp { id1, id2, ptr };
            }   

            for( auto [name, fn] : customfunctions )
            {
                if( expr[1] == name ) return BinaryOp { id1, id2, fn };
            }
        }

        return std::nullopt;
    }
};

struct Op3
{
    std::array<long, 3> ids;
    std::function<double(double, double, double)> op;

    static std::optional<Op3> create( const std::vector<std::string>& expr, size_t )
    {
        if( ( expr[0] == "Op3" || expr[0] == "Call" ) && expr.size( ) == 5 )
        {
            using CustomPair = std::pair<const char*, decltype( op )>;
      
            auto customfunctions = std::array 
            {
                CustomPair { "select", []( double cond, double v1, double v2 ) noexcept { return cond > 0.0 ? v1 : v2; } },
                CustomPair { "lerp", []( double a, double b, double t ) noexcept { return a + t * ( b - a ); } },
            };
  
            auto ids = std::array { std::stol( expr[2] ), std::stol( expr[3] ), std::stol( expr[4] ) };
                     
            for( auto [name, fn] : customfunctions )
            {
                if( expr[1] == name ) return Op3 { ids, fn };
            }
        }

        return std::nullopt;
    }
};

using Expression = std::variant<Constant, Input, UnaryOp, BinaryOp, Op3>;

// Parse input
Expression create( const std::vector<std::string>& expression, size_t ndim )
{
    MLHP_CHECK( !expression.empty( ), "Empty expression." );

    // Iterate over variant types
    auto iterate = [&]<size_t I = 0>( auto&& self ) -> Expression
    {
        // If index is within variant size
        if constexpr( I < std::variant_size_v<Expression> )
        {
            // Call create and return if successful, otherwise move to next index
            if( auto result = std::variant_alternative_t<I, Expression>::create( expression, ndim ); result )
            {
                return *result;
            }

            return self.template operator()<I + 1>( self );
        }

        auto message = std::string { "Unknown expression [" };

        for( auto& subexpr : expression )
        {
            message += "\"" + subexpr + "\", ";
        }

        message.erase( message.end( ) - 2, message.end( ) );

        MLHP_THROW( message + "]." );
    };

    return iterate( iterate );
}

// Dispatch during runtime using overload resolution
template<size_t D>
struct DispatchExpression 
{
    double call( long index ) const { return std::visit( *this, tree[static_cast<size_t>( index )] ); };

    double operator()( const Constant& node ) const noexcept { return node.value; }    
    double operator()( const Input& node ) const noexcept { return xyz[node.index]; }    
    double operator()( const UnaryOp& node ) const noexcept { return node.op( call( node.index ) ); }    
    double operator()( const BinaryOp& node ) const noexcept { return node.op( call( node.left ), call( node.right ) ); }
    double operator()( const Op3& node ) const noexcept { return node.op( call( node.ids[0] ), call( node.ids[1] ), call( node.ids[2] ) ); }

    const std::vector<Expression>& tree;
    const std::array<double, D>& xyz;
};

template<size_t D>
auto createExpressionList( std::vector<std::vector<std::string>>&& tree )
{
    MLHP_CHECK( !tree.empty( ), "Empty tree." );

    auto nodes = std::vector<parser::Expression> { };

    for( auto& node : tree )
    {
        nodes.push_back( parser::create( node, D ) );
    }

    return nodes;
}

} // parser

template<size_t D>
void defineVectorFunctionWrapper( pybind11::module& m )
{
    auto wrapper = pybind11::class_<spatial::VectorFunction<D>>( m, add<D>( "VectorFunction" ).c_str( ) );

    auto call = []( const spatial::VectorFunction<D>& function, std::array<double, D> xyz )
    {
        auto out = std::vector<double>( function.odim, 0.0 );

        function( xyz, out );

        return out;
    };

    wrapper.def( "__call__", call, pybind11::arg( "xyz" ) );
}

template<size_t D>
void defineFunctionWrappers( pybind11::module& m )
{
    auto s = defineFunctionWrapper<spatial::ScalarFunction<D>>( m, add<D>( "ScalarFunction" ), true );
    
    defineFunctionWrapper<QuadratureOrderDeterminor<D>>( m, add<D>( "QuadratureOrderDeterminor" ), true );
    defineVectorFunctionWrapper<D>( m );

    defineVectorization( *s );

    auto implicitF1 = []( const ScalarFunctionWrapper<D>& f, double threshold ) 
    { 
        return ImplicitFunctionWrapper<D> { implicit::threshold( f.get( ), threshold ) };
    };

    s->def( "asimplicit", implicitF1, pybind11::arg( "theshold" ) = 0.5 );

    if constexpr( D == config::maxdim )
    {
        auto sm = defineFunctionWrapper<spatial::ScalarFunction<D + 1>>( m, add<D + 1>( "ScalarFunction" ), true );
        
        defineVectorFunctionWrapper<D + 1>( m );
        defineVectorization( *sm );
    }
}

template<size_t D>
void defineTriangulation( pybind11::module& m )
{    
    auto triangulationC = pybind11::class_<Triangulation<D>,
        std::shared_ptr<Triangulation<D>>>( m, add<D>( "Triangulation" ).c_str( ) );
    
    auto associationC = pybind11::class_<TriangleCellAssociation<D>,
        std::shared_ptr<TriangleCellAssociation<D>>>( m, add<D>( "TriangleCellAssociation" ).c_str( ) );

    auto triangulationInit2 = []( CoordinateList<D>&& xyz, std::vector<std::array<size_t, 3>>&& triangles )
    {
        auto nvertices = xyz.size( );

        for( auto& triangle : triangles ) 
        {
            MLHP_CHECK( array::maxElement( triangle ) < nvertices, "Vertex index out of bounds." );
        }

        return std::make_shared<Triangulation<D>>( Triangulation<D> { std::move( xyz ), std::move( triangles ) } );
    };

    auto triangulationStr = []( const Triangulation<D>& triangulation )
    {
        auto sstream = std::stringstream { };
        auto memoryUsage = utilities::memoryUsageString( triangulation.memoryUsage( ) );

        sstream << "Triangulation" << D << "D (address " << &triangulation << ")" << std::endl;
        sstream << "    number of vertices  : " << triangulation.nvertices( ) << std::endl;
        sstream << "    number of triangles : " << triangulation.ntriangles( ) << std::endl;
        sstream << "    heap memory usage   : " << memoryUsage << std::endl;

        return sstream.str( );
    };

    auto associationInit = []( CoordinateList<D>&& rst, std::vector<size_t>&& offsets )
    {
        if( offsets.empty( ) ) 
        {
            offsets = { 0 };
        }

        return std::make_shared<TriangleCellAssociation<D>>( TriangleCellAssociation<D> { std::move( rst ), std::move( offsets ) } );
    };
    
    auto associationStr = []( const TriangleCellAssociation<D>& association )
    {
        auto sstream = std::stringstream { };
        auto memoryUsage = utilities::memoryUsageString( association.memoryUsage( ) );

        sstream << "TriangleCellAssociation" << D << "D (address " << &association << ")" << std::endl;
        sstream << "    number of vertices   : " << association.rst.size( ) << std::endl;
        sstream << "    number of triangles  : " << association.offsets.back( ) << std::endl;
        sstream << "    number of mesh cells : " << association.offsets.size( ) - 1 << std::endl;
        sstream << "    heap memory usage    : " << memoryUsage << std::endl;

        return sstream.str( );
    };

    auto boundingBoxF = []( Triangulation<D>& t, size_t itriangle )
    { 
        return t.boundingBox( itriangle );
    };

    auto transformF = []( Triangulation<D>& tri, const spatial::HomogeneousTransformation<D>& transform )
    {
        for( auto& v : tri.vertices )
        {
            v = transform( v );
        }
    };

    triangulationC.def( pybind11::init<>( ) );
    triangulationC.def( pybind11::init( triangulationInit2 ), pybind11::arg( "vertices" ), pybind11::arg( "triangles" ) );
    triangulationC.def( "__str__", triangulationStr );
    triangulationC.def( "ntriangles", &Triangulation<D>::ntriangles );
    triangulationC.def( "nvertices", &Triangulation<D>::nvertices );
    triangulationC.def( "triangleIndices", &Triangulation<D>::triangleIndices, pybind11::arg( "itriangle" ) );
    triangulationC.def( "triangleVertices", &Triangulation<D>::triangleVertices, pybind11::arg( "itriangle" ) );
    triangulationC.def( "boundingBox", []( Triangulation<D>& t ) { return t.boundingBox( ); } );
    triangulationC.def( "boundingBox", boundingBoxF, pybind11::arg( "itriangle" ) );
    triangulationC.def( "area", &Triangulation<D>::area );
    triangulationC.def( "transform", transformF, pybind11::arg( "transformation" ) );
    triangulationC.def_readwrite( "vertices", &Triangulation<D>::vertices );
    triangulationC.def_readwrite( "triangles", &Triangulation<D>::triangles );
    
    if constexpr( D <= 3 )
    {
        triangulationC.def( "writeVtu", static_cast<void(*)( const Triangulation<D>&, const std::string& )>(
            &writeVtu<D> ), pybind11::arg( "filename" ) = "triangulation.vtu" );
    }

    auto filterTriangulationF1 = []( const Triangulation<D>& triangulation, 
                                     const ImplicitFunctionWrapper<D>& function, 
                                     size_t nseedpoints )
    { 
        return std::make_shared<Triangulation<D>>( filterTriangulation( 
            triangulation, function.get( ), nseedpoints ) );
    };
    
    auto filterTriangulationF2 = []( const Triangulation<D>& triangulation, 
                                     const TriangleCellAssociation<D>& celldata,
                                     const ImplicitFunctionWrapper<D>& function, 
                                     size_t nseedpoints )
    { 
        auto [filteredTriangulation, filteredCelldata] = filterTriangulation( 
            triangulation, celldata, function.get( ), nseedpoints );

        return std::pair { std::make_shared<Triangulation<D>>( std::move( filteredTriangulation ) ),
                           std::make_shared<TriangleCellAssociation<D>>( std::move( filteredCelldata ) ) };
    };

    m.def( "filterTriangulation", filterTriangulationF1, pybind11::arg( "triangulation" ), 
        pybind11::arg( "function" ), pybind11::arg( "nseedpoints" ) = 2 );

    m.def( "filterTriangulation", filterTriangulationF2, pybind11::arg( "triangulation" ),
        pybind11::arg( "celldata" ), pybind11::arg( "function" ), pybind11::arg( "nseedpoints" ) = 2 );

    associationC.def( pybind11::init( associationInit ),
        pybind11::arg( "rst" ) = CoordinateList<D> { }, 
        pybind11::arg( "offsets" ) = std::vector<size_t>{ 0 } );
    associationC.def( "__str__", associationStr );
    associationC.def_readwrite( "rst", &TriangleCellAssociation<D>::rst );
    associationC.def_readwrite( "offsets", &TriangleCellAssociation<D>::offsets );

    if constexpr( D == 3 )
    {
        triangulationC.def( "integrateNormalComponents", integrateNormalComponents, pybind11::arg( "abs" ) = false );

        triangulationC.def( "writeStl", &writeStl, pybind11::arg( "filename" ) = "triangulation.stl", 
            pybind11::arg("solidname") = "Boundary");

        auto readStlF = []( std::string filename, bool correctOrdering )
        {
            return createTriangulation<3>( readStl( filename, correctOrdering) );
        };
        
        auto implicitTriangulationF1 = []( std::string filename )
        {
            auto triangulation = std::make_shared<Triangulation<D>>( createTriangulation<3>( readStl( filename ) ) );

            return ImplicitFunctionWrapper<D> { makeTriangulationDomain( triangulation ) };
        };

        auto implicitTriangulationF2 = []( std::shared_ptr<Triangulation<D>> t )
        {
            return ImplicitFunctionWrapper<D> { makeTriangulationDomain( t ) };
        };

        auto implicitTriangulationF3 = []( std::shared_ptr<Triangulation<D>> t,
                                           std::shared_ptr<KdTree<D>> tree )
        {
            return ImplicitFunctionWrapper<D> { makeTriangulationDomain( t, tree ) };
        };

        m.def( "readStl", readStlF, pybind11::arg( "filename" ), pybind11::arg( "correctOrdering" ) = false );
        m.def( "implicitTriangulation", implicitTriangulationF1, pybind11::arg( "filename" ) );
        m.def( "implicitTriangulation", implicitTriangulationF2, pybind11::arg( "triangulation" ) );
        m.def( "implicitTriangulation", implicitTriangulationF3, pybind11::arg( "triangulation" ), pybind11::arg( "kdtree" ) );

        auto intersectF1 = []( const AbsMesh<D>& mesh, const Triangulation<D>& triangulation, const KdTree<D>& tree )
        { 
            auto [intersected, celldata] = intersectTriangulationWithMesh( mesh, triangulation, tree );

            return std::pair { std::make_shared<Triangulation<D>>( std::move( intersected ) ),
                               std::make_shared<TriangleCellAssociation<D>>( std::move( celldata ) ) };
        };
        
        auto intersectF2 = [=]( const AbsMesh<D>& mesh, const Triangulation<D>& triangulation )
        { 
            return intersectF1( mesh, triangulation, buildKdTree( triangulation ) );
        };

        m.def( "intersectTriangulationWithMesh", intersectF1, pybind11::arg( "mesh" ), 
            pybind11::arg( "triangulation" ), pybind11::arg( "tree" ) );

        m.def( "intersectTriangulationWithMesh", intersectF2, pybind11::arg( "mesh" ), 
            pybind11::arg( "triangulation" ) );

        auto associatedTrianglesCellMeshF = []( const Triangulation<D>& triangulation,
                                                const TriangleCellAssociation<D>& celldata )
        { 
             return CellMeshCreatorWrapper<D> { cellmesh::associatedTriangles( triangulation, celldata ) };
        };

        m.def( "associatedTrianglesCellMesh", associatedTrianglesCellMeshF, 
            pybind11::arg( "triangulation" ), pybind11::arg( "celldata" ) );

        auto marchingCubesBoundaryF = []( const AbsMesh<D>& mesh,
                                          const ImplicitFunctionWrapper<D>& function,
                                          std::array<size_t, 3> resolution )
        {
            auto [intersected, celldata] = marchingCubesBoundary( mesh, function.get( ), resolution );

            return std::pair { std::make_shared<Triangulation<D>>( std::move( intersected ) ),
                               std::make_shared<TriangleCellAssociation<D>>( std::move( celldata ) ) };
        };

        m.def( "marchingCubesBoundary", marchingCubesBoundaryF, pybind11::arg( "mesh" ), 
            pybind11::arg( "function" ), pybind11::arg( "resolution" ) );
    }
}

template<size_t D>
void defineSpatialDimension( pybind11::module& m )
{
    defineFunctionWrappers<D>( m );

    auto sliceLastF = []( const ScalarFunctionWrapper<D + 1>& function, double value )
    {
        return ScalarFunctionWrapper<D>{ spatial::sliceLast( 
            static_cast<spatial::ScalarFunction<D + 1>>( function ), value ) };
    };

    m.def( "sliceLast", sliceLastF, pybind11::arg( "function" ), pybind11::arg( "value" ) = 0.0 );

    auto expandDimensionF = []( const ScalarFunctionWrapper<D>& function, size_t index )
    {
        return ScalarFunctionWrapper<D + 1>{ spatial::expandDimension( function.get( ), index ) };
    };

    m.def( "expandDimension", expandDimensionF, pybind11::arg( "function" ), pybind11::arg( "index" ) = D );

    auto scalarFieldFromVoxelDataF1 = []( std::shared_ptr<DoubleVector> data, 
                                          std::array<size_t, D> nvoxels, 
                                          std::array<double, D> lengths, 
                                          std::array<double, D> origin,
                                          std::optional<double> outside )
    {
        return ScalarFunctionWrapper<D> { spatial::voxelFunction<D, double>(
            data->getShared( ), nvoxels, lengths, origin, outside ) };
    };
    
    auto scalarFieldFromVoxelDataF2 = []( std::shared_ptr<FloatVector> data, 
                                          std::array<size_t, D> nvoxels, 
                                          std::array<double, D> lengths, 
                                          std::array<double, D> origin,
                                          std::optional<float> outside )
    {
        return ScalarFunctionWrapper<D> { spatial::voxelFunction<D, float>(
            data->getShared( ), nvoxels, lengths, origin, outside ) };
    };

    auto wrapVoxelField = [&]( auto&& function )
    {
        m.def( "scalarFieldFromVoxelData", function, pybind11::arg( "data" ),
            pybind11::arg( "nvoxels" ), pybind11::arg( "lengths" ), 
            pybind11::arg( "origin" ) = array::make<D>( 0.0 ),
            pybind11::arg( "outside" ) = std::nullopt );
    };

    wrapVoxelField( scalarFieldFromVoxelDataF1 );
    wrapVoxelField( scalarFieldFromVoxelDataF2 );

    using ImplicitScalarPair = std::pair<ImplicitFunctionWrapper<D>, std::variant<ScalarFunctionWrapper<D>, double>>;

    auto selectScalarFieldF = []( const std::vector<ImplicitScalarPair>& input,
                                  std::optional<double> defaultValue )
    {
        auto functions = std::make_shared<std::vector<std::pair<ImplicitFunction<D>, spatial::ScalarFunction<D>>>>( );

        if( defaultValue )
        {
            auto alwaysTrue = std::function { []( std::array<double, D> ) noexcept { return true; } };

            functions->push_back( std::pair { alwaysTrue, spatial::constantFunction<D>( *defaultValue ) } );
        }

        for( size_t i = 0; i < input.size( ); ++i )
        {
            functions->push_back( std::pair { input[i].first, std::holds_alternative<double>( input[i].second ) ?
                spatial::constantFunction<D>( std::get<double>( input[i].second ) ) : 
                std::get<ScalarFunctionWrapper<D>>( input[i].second ).get( ) } );
        }

        return ScalarFunctionWrapper<D> { [functions = std::move( functions )]( std::array<double, D> xyz )
        { 
            auto nfunctions = functions->size( );
            for( size_t i = 0; i < nfunctions; ++i )
            {
                if( auto& [implicit, spatial] = ( *functions )[nfunctions - 1 - i]; implicit( xyz ) )
                {
                    return spatial( xyz );
                }
            }

            MLHP_THROW( "No field defined at coordinates " + spatial::to_string( xyz ) + "." );
        } };
    };

    m.def( "selectScalarField", selectScalarFieldF, pybind11::arg( "domains" ), pybind11::arg( "default" ) = std::nullopt );

    defineTriangulation<D>( m );
}

template<size_t... D>
void defineSpatialDimensions( pybind11::module& m, std::index_sequence<D...>&& )
{
    [[maybe_unused]] std::initializer_list<int> tmp { ( defineSpatialDimension<D + 1>( m ), 0 )... };
}

template<size_t D>
using DynamicVectorFunction = spatial::VectorFunction<D, std::dynamic_extent>;

void bindSpatial( pybind11::module& m )
{
    defineSpatialDimensions( m, std::make_index_sequence<config::maxdim>( ) );
    
    using ScalarFunctionWrapperVariant = DimensionVariantPlus1<ScalarFunctionWrapper>;
    using VectorFunctionWrapperVariant = DimensionVariantPlus1<DynamicVectorFunction>;

    // From syntax tree
    {
        using Tree = std::vector<std::vector<std::string>>;

        auto createScalar = []<size_t D>( Tree&& tree ) -> ScalarFunctionWrapperVariant
        { 
            auto nodes = parser::createExpressionList<D>( std::move( tree ) );

            auto impl = [nodes = std::move( nodes )]( std::array<double, D> xyz )
            {
                return parser::DispatchExpression<D> { nodes, xyz }.call( 0 );
            };

            return ScalarFunctionWrapper<D> { std::move( impl ) };
        };

        auto scalarFieldFromTree = [createScalar = std::move( createScalar )]( size_t ndim, Tree tree )
        {
            return dispatchDimension<config::maxdim + 1>( createScalar, ndim, std::move( tree ) );
        };

        m.def( "_scalarFieldFromTree", scalarFieldFromTree,
            pybind11::arg( "ndim" ), pybind11::arg( "tree" ) );
                
        auto createVector = []<size_t D>( std::vector<Tree>&& tree ) -> VectorFunctionWrapperVariant
        { 
            auto nodes = std::vector<std::vector<parser::Expression>> { };

            for( auto& field : tree )
            {
                nodes.push_back( parser::createExpressionList<D>( std::move( field ) ) );
            }

            auto impl = [nodes = std::move( nodes )]( std::array<double, D> xyz, std::span<double> out )
            {
                for( size_t ifield = 0; ifield < nodes.size( ); ++ifield )
                {
                    out[ifield] = parser::DispatchExpression<D> { nodes[ifield], xyz }.call( 0 );
                }
            };

            return spatial::VectorFunction<D> { tree.size( ), std::move( impl ) };
        };

        auto vectorFieldFromTree = [createVector = std::move( createVector )]( size_t idim, std::vector<Tree> tree )
        {
            return dispatchDimension<config::maxdim + 1>( createVector, idim, std::move( tree ) );
        };

        m.def( "_vectorFieldFromTree", vectorFieldFromTree,
            pybind11::arg( "idim" ), pybind11::arg( "tree" ) );
    }

    // From function pointer
    {
        auto createScalar = []<size_t D>( std::uint64_t address ) -> ScalarFunctionWrapperVariant
        { 
            return ScalarFunctionWrapper<D> { spatial::ScalarFunction<D> { [address]( std::array<double, D> xyz )
            { 
                return reinterpret_cast<double(*)( double*, std::int64_t )>( address ) ( xyz.data( ), static_cast<std::int64_t>( D ) ); 
            } } };
        };

        auto scalarFieldFromAddress = [createScalar = std::move( createScalar )]( size_t ndim, std::uint64_t address )
        {
            return dispatchDimension<config::maxdim + 1>( createScalar, ndim, address );
        };

        m.def( "_scalarFieldFromAddress", scalarFieldFromAddress,
            pybind11::arg( "ndim" ), pybind11::arg( "address" ) );

        auto createVector = []<size_t D>( size_t odim, std::uint64_t address ) -> VectorFunctionWrapperVariant
        { 
            return spatial::VectorFunction<D> { odim, [address]( std::array<double, D> xyz, std::span<double> out )
            { 
                auto function = reinterpret_cast<void( * )( double*, double*, std::int64_t, std::int64_t )>( address );

                return function( xyz.data( ), out.data( ), static_cast<std::int64_t>( D ), static_cast<std::int64_t>( out.size( ) ) );
            } };
        };
        
        auto vectorFieldFromAddress = [createVector = std::move( createVector )]( size_t idim, size_t odim, std::uint64_t address )
        {
            return dispatchDimension<config::maxdim + 1>( createVector, idim, odim, address );
        };
        
        m.def( "_vectorFieldFromAddress", vectorFieldFromAddress, pybind11::arg( "idim" ),
            pybind11::arg( "odim" ), pybind11::arg( "address" ) );
    }

    // Singular solution
    {
        struct SingularSolution 
        { 
            ScalarFunctionWrapperVariant solution;
            ScalarFunctionWrapperVariant source;
            VectorFunctionWrapperVariant derivatives;
        };

        auto makeSingularSolution = pybind11::class_<SingularSolution>( m, "makeSingularSolution" );

        auto init = []( size_t ndim )
        {
            auto create = []<size_t D>( )
            { 
                return SingularSolution
                {
                    .solution = solution::singularSolution<D>( ),
                    .source = solution::singularSolutionSource<D>( ),
                    .derivatives = spatial::VectorFunction<D> { solution::singularSolutionDerivatives<D>( ) }
                };
            };

            return dispatchDimension( create, ndim );
        };

        makeSingularSolution.def( pybind11::init( init ), pybind11::arg( "ndim" ) );
        makeSingularSolution.def_readonly( "solution", &SingularSolution::solution );
        makeSingularSolution.def_readonly( "source", &SingularSolution::source );
        makeSingularSolution.def_readonly( "derivatives", &SingularSolution::derivatives );
    }

    // AM Solution
    {
        struct AmLinearSolution
        {
            ScalarFunctionWrapperVariant solution;
            ScalarFunctionWrapperVariant source;
        };

        auto makeAMSolution = pybind11::class_<AmLinearSolution>( m, "makeAmLinearSolution" );

        makeAMSolution.def_readwrite( "solution", &AmLinearSolution::solution );
        makeAMSolution.def_readwrite( "source", &AmLinearSolution::source );

        auto registerConstructor = [&]<size_t D>( )
        {
            auto init = []( std::array<double, D> begin_, std::array<double, D> end, double duration,
                            double capacity, double kappa, double sigma, double dt, double shift )
            {
                auto begin = begin_;

                auto path = [=]( double t ) noexcept { return spatial::interpolate<D>( begin, end, t / duration ); };
                auto intensity = [=]( double t ) noexcept { return std::min( t / 0.05, 1.0 ); };

                return AmLinearSolution
                {
                    .solution = solution::amLinearHeatSolution<D>( path,
                        intensity, capacity, kappa, sigma, dt, shift ),
                    .source = solution::amLinearHeatSource<D>( path, intensity, sigma )
                };
            };

            makeAMSolution.def( pybind11::init( init ), pybind11::arg( "begin" ), pybind11::arg( "end" ), 
                pybind11::arg( "duration" ), pybind11::arg( "capacity" ), pybind11::arg( "kappa" ), 
                pybind11::arg( "sigma" ), pybind11::arg( "dt" ), pybind11::arg( "shift" ) );
        };
        
        registerConstructor.template operator()<1>( );
        registerConstructor.template operator()<2>( );
        registerConstructor.template operator()<3>( );
    }
}

} // mlhp::bindings
