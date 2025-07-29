// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_MEMORY_HPP
#define MLHP_CORE_MEMORY_HPP

#include <cstdlib>
#include <memory>
#include <vector>

#include "mlhp/core/compilermacros.hpp"
#include "mlhp/core/config.hpp"

namespace mlhp::memory
{

template<typename T> [[nodiscard]]
constexpr auto assumeAligned( T* ptr )
{
    return std::assume_aligned<config::simdAlignment>( ptr );
}

template<typename T> [[nodiscard]]
constexpr auto assumeNoalias( T* ptr )
{
    return static_cast<T* MLHP_RESTRICT>( ptr );
}

template<typename T> [[nodiscard]]
constexpr auto assumeAlignedNoalias( T* ptr )
{
    return assumeNoalias( assumeAligned( ptr ) );
}

template<typename T>
constexpr size_t simdVectorSize( )
{
    return config::simdAlignment / sizeof( T );
}

template<typename T> 
constexpr size_t paddedNumberOfBlocks( size_t length )
{
    constexpr size_t simdSize = simdVectorSize<T>( );

    static_assert( simdSize > 0, "Simd over-alignment is smaller than sizeof(double)." );

    return length != 0 ? ( ( length - 1 ) / simdSize + 1 ) : 0;
}

template<typename T> 
constexpr size_t paddedLength( size_t length )
{
    return paddedNumberOfBlocks<T>( length ) * simdVectorSize<T>( );
}

template<typename T>
struct AlignedAllocator
{
    using value_type = T;

    static constexpr std::align_val_t alignment { config::simdAlignment };

    AlignedAllocator( ) noexcept = default;

    template<class U> 
    AlignedAllocator( const AlignedAllocator<U>& ) noexcept { }

    MLHP_MALLOC value_type* allocate( std::size_t n )
    {
        return static_cast<value_type*>( ::operator new( n * sizeof( T ), alignment ) );
    }

    void deallocate( value_type* p, std::size_t ) noexcept
    {
        ::operator delete( p, alignment );
    }

    bool operator==(const AlignedAllocator&) const { return true; } 
    bool operator!=(const AlignedAllocator&) const { return false; }
};

template<typename T>
using AlignedVector = std::vector<T, AlignedAllocator<T>>;

template<typename T> [[nodiscard]]
auto noaliasBegin( AlignedVector<T>& vector )
{
    return assumeAlignedNoalias( vector.data( ) );
}

template<typename T> [[nodiscard]]
auto noaliasBegin( const AlignedVector<T>& vector )
{
    return assumeAlignedNoalias( vector.data( ) );
}

//! Variable-ownership pointer that can be initialized by an std::shared_ptr
//! or an std::unique_ptr to hold an object and keep it alive. Alterantively,
//! it can be used like a raw pointer or reference (i.e. non-owning), in case 
//! ownership is not desired (or not possible in that context).
template<typename T>
class vptr
{
public:
    using type = std::remove_const_t<T>;

    explicit vptr( ) :
        raw_ { nullptr }
    { }

    vptr( T* obj ) :
        raw_{ obj } { }

    vptr( T& obj ) :
        vptr( &obj )
    { }

    template<typename T2>
    vptr( std::shared_ptr<T2>&& obj ) :
        raw_ { obj.get( ) }, shared_ { std::const_pointer_cast<type>( 
            std::static_pointer_cast<const type>( std::move( obj ) ) ) } { }
    
    template<typename T2>
    vptr( const std::shared_ptr<T2>& obj ) : vptr( std::shared_ptr { obj } ) { }
    
    template<typename T2>
    vptr( std::unique_ptr<T2>&& obj ) : vptr( std::shared_ptr { std::move( obj ) } ) { }
    
    const T* get( ) const { return raw_; }
    const T* operator->( ) const { return get( ); }
    const T& operator*( ) const { return *get( ); }
    
    T* get( ) { return raw_; }
    T* operator->( ) { return get( ); }
    T& operator*( ) { return *get( ); }

    auto shared( ) const { return shared_; }

private:
    T* raw_;
    std::shared_ptr<type> shared_;
};

} // mlhp::memory

namespace mlhp
{

using AlignedDoubleVector = memory::AlignedVector<double>;
using AlignedDoubleVectors = std::vector<AlignedDoubleVector>;

}

#endif // MLHP_CORE_MEMORY_HPP
