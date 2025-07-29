// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_INTEGRANDS_HPP
#define MLHP_CORE_INTEGRANDS_HPP

#include "mlhp/core/integrandtypes.hpp"
#include "mlhp/core/spatial.hpp"

#include <span>

namespace mlhp
{

// Standard linear system domain integrands

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2DomainIntegrand( const spatial::ScalarFunction<D>& rhs,
                                          size_t ifield = 0 );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2DomainIntegrand( const spatial::ScalarFunction<D>& mass,
                                          const spatial::ScalarFunction<D>& rhs,
                                          size_t ifield = 0 );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2DomainIntegrand( const spatial::VectorFunction<D>& rhs );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2DomainIntegrand( const spatial::VectorFunction<D>& mass,
                                          const spatial::VectorFunction<D>& rhs );


template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makePoissonIntegrand( const spatial::ScalarFunction<D>& conductivity,
                                         const spatial::ScalarFunction<D>& source );

template<size_t D>  MLHP_EXPORT
DomainIntegrand<D> makeAdvectionDiffusionIntegrand( const spatial::VectorFunction<D, D>& velocity,
                                                    const spatial::ScalarFunction<D>& diffusivity,
                                                    const spatial::ScalarFunction<D>& source );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeFunctionIntegrand( const spatial::ScalarFunction<D>& function );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeFunctionIntegrand( const spatial::VectorFunction<D>& function );

template<size_t D>
struct ConstitutiveEquation final
{
    using AnyCache = utilities::Cache<ConstitutiveEquation<D>>;

    using Create = AnyCache( const AbsBasis<D>& basis );

    using Prepare = void( AnyCache& anyCache,
                          const MeshMapping<D>& mapping,
                          const LocationMap& locationMap );

    using Evaluate = void( AnyCache& anyCache,
                           const BasisFunctionEvaluation<D>& shapes,
                           std::span<const double> strain,
                           std::span<double> stress,
                           std::span<double> tangent );

    std::function<Create> create = utilities::returnEmpty<AnyCache>( );
    std::function<Prepare> prepare = utilities::doNothing( );
    std::function<Evaluate> evaluate;

    size_t ncomponents = 0;   // size of material matrix
    bool symmetric = false;   // symmetry of material matrix
    bool incremental = false; // total strain or strain increment formulation
};

template<size_t D> MLHP_EXPORT
Kinematics<D> makeSmallStrainKinematics( );

MLHP_EXPORT
ConstitutiveEquation<3> makeIsotropicElasticMaterial( const spatial::ScalarFunction<3>& youngsModulus,
                                                      const spatial::ScalarFunction<3>& poissonRatio );

MLHP_EXPORT
ConstitutiveEquation<2> makePlaneStrainMaterial( const spatial::ScalarFunction<2>& youngsModulus,
                                                 const spatial::ScalarFunction<2>& poissonRatio );

MLHP_EXPORT
ConstitutiveEquation<2> makePlaneStressMaterial( const spatial::ScalarFunction<2>& youngsModulus,
                                                 const spatial::ScalarFunction<2>& poissonRatio );

//! Linear
template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeStaticDomainIntegrand( memory::vptr<const Kinematics<D>> kinematics,
                                              memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                              const spatial::VectorFunction<D, D>& force );

//! Nonlinear
template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeStaticDomainIntegrand( memory::vptr<const Kinematics<D>> kinematics,
                                              memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                              memory::vptr<const std::vector<double>> dofs,
                                              const spatial::VectorFunction<D, D>& force,
                                              bool integrateTangent = true );

// https://en.wikipedia.org/wiki/Elastic_modulus
struct ElasticConverter
{
    double lambda_, mu_;

    ElasticConverter( double E, double nu )
    {
        auto tmp1 = ( 1.0 - 2.0 * nu );
        auto tmp2 = E / ( ( 1.0 + nu ) * tmp1 );

        lambda_ = nu * tmp2;
        mu_ = 0.5 * tmp1 * tmp2;
    }

    auto lambda( ) const { return lambda_; } 
    auto mu( ) const { return mu_; }         
    auto lameParameters( ) const { return std::array { lambda( ), mu( ) }; }

    auto shearModulus( ) const { return mu_; }
    auto bulkModulus( ) const { return lambda_ + 2.0 / 3.0 * mu_; }
    auto bulkAndShearModuli( ) const { return std::array { bulkModulus( ), shearModulus( ) }; }
};

// E.g. in 3D: 
// S00  S01  S02
//      S11  S12  ->  [S00, S11, S22, S01, S12, S02]
//           S22
template<size_t D>
struct VoigtIndices
{
    //! Go from (i, j) to Voigt index
    static constexpr auto vector = []( )
    {
        auto ij = std::array<std::array<size_t, D>, D> { };
        auto index = size_t { 0 };

        for( size_t k = 0; k < D; ++k )
        {
            for( size_t l = 0; l < D - k; ++l )
            {
                ij[l][l + k] = index++;
                ij[l + k][l] = ij[l][l + k];
            }
        }

        return ij; 
    }( );

    //! Go from Voigt index to matrix index (i, j)
    static constexpr auto matrix = []( )
    {
        auto indices = std::array<std::array<size_t, 2>, ( D * ( D + 1 ) ) / 2> { };
        auto index = size_t { 0 };

        for( size_t k = 0; k < D; ++k )
        {
            for( size_t l = 0; l < D - k; ++l )
            {
                indices[index++] = { l, l + k };
            }
        }

        return indices; 
    }( );

    static constexpr auto size = matrix.size( );
};

// Standard scalar domain integrands

struct ErrorIntegrals
{
    double analyticalSquared = 0, numericalSquared = 0, differenceSquared = 0;

    double numerical( ) { return std::sqrt( numericalSquared ); }
    double analytical( ) { return std::sqrt( analyticalSquared ); }
    double difference( ) { return std::sqrt( differenceSquared ); }
    double relativeDifference( ) { return std::sqrt( differenceSquared / analyticalSquared ); }

    operator AssemblyTargetVector( ) { return { analyticalSquared, numericalSquared, differenceSquared }; }
};

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeL2ErrorIntegrand( memory::vptr<const std::vector<double>> solutionDofs,
                                         const spatial::ScalarFunction<D>& solutionFunction );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeEnergyErrorIntegrand( memory::vptr<const std::vector<double>> solutionDofs,
                                             const spatial::VectorFunction<D, D>& analyticalDerivatives );

template<size_t D> MLHP_EXPORT
DomainIntegrand<D> makeInternalEnergyIntegrand( memory::vptr<const std::vector<double>> solutionDofs,
                                                memory::vptr<const Kinematics<D>> kinematics,
                                                memory::vptr<const ConstitutiveEquation<D>> constitutive );

// Basis projection linear system domain integrands

template<size_t D> MLHP_EXPORT
BasisProjectionIntegrand<D> makeL2BasisProjectionIntegrand( memory::vptr<const std::vector<double>> oldDofs );

template<size_t D> MLHP_EXPORT
BasisProjectionIntegrand<D> makeTransientPoissonIntegrand( const spatial::ScalarFunction<D + 1>& capacity,
                                                           const spatial::ScalarFunction<D + 1>& diffusivity,
                                                           const spatial::ScalarFunction<D + 1>& source,
                                                           memory::vptr<const std::vector<double>> dofs0,
                                                           std::array<double, 2> timeStep,
                                                           double theta );

// Surface integrands

template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNeumannIntegrand( const spatial::ScalarFunction<D>& rhs, size_t ifield = 0 );

template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNeumannIntegrand( const spatial::VectorFunction<D>& rhs );

// Integrate the for given field index
// 1) M_ij = N_i(x) * mass(x) * N_j(x)
// 2) F_i  = N_i(x) * rhs(x)
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::ScalarFunction<D>& mass,
                                             const spatial::ScalarFunction<D>& rhs,
                                             size_t ifield = 0 );

// Integrate the for all solution fields (for each field component separately, so no interaction)
// 1) M_ij = N_i(x) * mass(x) * N_j(x)
// 2) F_i  = N_i(x) * rhs(x)
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::VectorFunction<D>& mass,
                                             const spatial::VectorFunction<D>& rhs );

// Integrate the for given field index 
// 1) M_ij = N_i(x) * mass(x) * N_j(x) if computeTangent is true
// 2) F_i  = N_i(x) * ( rhs(x) - mass(x) * N_j(x) * dofs_j )
// If !computeTangent, 2) will be assembled into target index 0
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::ScalarFunction<D>& mass,
                                             const spatial::ScalarFunction<D>& rhs,
                                             memory::vptr<const std::vector<double>> dofs,
                                             size_t ifield = 0,
                                             bool computeTangent = true );

// Integrate the for all solution fields (for each field component separately, so no interaction)
// 1) M_ij = N_i(x) * mass(x) * N_j(x) if computeTangent is true
// 2) F_i  = N_i(x) * ( rhs(x) - mass(x) * N_j(x) * dofs_j )
// If !computeTangent, 2) will be assembled into target index 0
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2BoundaryIntegrand( const spatial::VectorFunction<D>& mass,
                                             const spatial::VectorFunction<D>& rhs,
                                             memory::vptr<const std::vector<double>>,
                                             bool computeTangent = true );


template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNormalNeumannIntegrand( const spatial::ScalarFunction<D>& pressure );

//! Constrain m * <u, n> = r; for example in 3D: m * <(u0, u1, u2), n> = r
// The weak residual is <w, n> * (<u, n> - r); for example in 3D:
//     int m * N0_i * n0 * (u0 * n0 + u1 * n1 + u2 * n2 - r) dx
//     int m * N1_i * n1 * (u0 * n0 + u1 * n1 + u2 * n2 - r) dx
//     int m * N2_i * n2 * (u0 * n0 + u1 * n1 + u2 * n2 - r) dx
// Assembles matrix if mass != std::nullopt into first slot
// Assembles vector if rhs != std::nullopt into second slot (or first if no matrix)
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2NormalIntegrand( const std::optional<spatial::ScalarFunction<D>>& lhs,
                                           const std::optional<spatial::ScalarFunction<D>>& rhs );

//! Nonlinear (tangent/residual) version of the integrand above
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeL2NormalIntegrand( const std::optional<spatial::ScalarFunction<D>>& lhs,
                                           const std::optional<spatial::ScalarFunction<D>>& rhs,
                                           memory::vptr<const std::vector<double>> dofs );

//! Nitsche boundary integral
// Weak residual: beta * <w, u - f> - <w, <n, sigma(u)>> - <<sigma(w), n>, u - f>
// Element system: beta * N^T * N - N^T * (n^T * C * B) - (B^T * C^T * n) * N = beta * N^T * f - (B^T * C^T * n) * f
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNitscheIntegrand( memory::vptr<const Kinematics<D>> kinematics,
                                          memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                          const spatial::VectorFunction<D>& function,
                                          double beta );

//! Nonlinear (tangent/residual) version of the integrand above
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeNitscheIntegrand( memory::vptr<const Kinematics<D>> kinematics,
                                          memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                          memory::vptr<const std::vector<double>> dofs,
                                          const spatial::VectorFunction<D>& function,
                                          double beta );

// Integrate stress times surface normal direction
template<size_t D> MLHP_EXPORT
SurfaceIntegrand<D> makeReactionForceIntegrand( memory::vptr<const Kinematics<D>> kinematics,
                                                memory::vptr<const ConstitutiveEquation<D>> constitutive,
                                                memory::vptr<const std::vector<double>> dofs );

} // mlhp

#endif // MLHP_CORE_INTEGRANDS_HPP
