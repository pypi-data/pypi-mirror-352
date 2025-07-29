// This file is part of the mlhp project. License: See LICENSE

#include "tests/core/core_test.hpp"

#include "mlhp/core/dense.hpp"
#include "mlhp/core/compilermacros.hpp"
#include "mlhp/core/memory.hpp"
#include "mlhp/core/spatial.hpp"

#include<array>

namespace mlhp
{
namespace linalg
{
//
//TEST_CASE( "outerProduct_1D_test" )
//{
//    size_t paddedSize = MLHP_SIMD_ALIGNMENT / sizeof( double );
//
//    memory::AlignedVector<double> N { 1.0, 2.0, 3.0 };
//    memory::AlignedVector<double> target( 3 * paddedSize, -0.6 );
//
//    CHECK_NOTHROW( dense::outerProductFull<1>( target.data( ), N.data( ), 2.3, 3 ) );
//
//    for( size_t i = 0; i < 3; ++i )
//    {
//        for( size_t j = 0; j < 3; ++j )
//        {
//            CHECK( target[i * paddedSize + j] == Approx( N[i] * N[j] * 2.3 - 0.6 ).epsilon( 1e-12 ) );
//        }
//    }
//}
//
//TEST_CASE( "outerProduct_2D_test" )
//{
//    size_t paddedSize = MLHP_SIMD_ALIGNMENT / sizeof( double );
//
//    memory::AlignedVector<double> N ( 2 * paddedSize, 0.0 );
//    memory::AlignedVector<double> target( 3 * paddedSize, -0.6 );
//
//    N[0] = 1.0;
//    N[1] = 2.0;
//    N[2] = 3.0;
//    N[paddedSize + 0] = 4.0;
//    N[paddedSize + 1] = 5.0;
//    N[paddedSize + 2] = 6.0;
//
//    CHECK_NOTHROW( outerProductFull<2>( target.data( ), N.data( ), 2.3, 3 ) );
//
//    for( size_t i = 0; i < 3; ++i )
//    {
//        for( size_t j = 0; j < 3; ++j )
//        {
//            double expectedValue = ( N[i] * N[j] + N[paddedSize + i] * N[paddedSize + j] ) * 2.3 - 0.6;
//
//            CHECK( target[i * paddedSize + j] == Approx( expectedValue ).epsilon( 1e-12 ) );
//        }
//    }
//}

TEST_CASE( "lu_test" )
{

    // -------------------- test lu ----------------------

    double M[] = 
    {
        -6.57236887,  0.84564944, -1.02177673,  3.75118371,  2.67678544,
         9.64342431, -1.2257033,   4.58716922, -5.83018145, -7.51428046,
         5.68716742,  2.04974341,  0.10133382, -9.21934916,  9.65478781,
        -9.0823581,   6.64997405, -8.45984082, -9.00872702, -2.79864918,
        -8.70517483,  6.64140389, -9.14154383,  1.50739727,  5.46489685 
    };

    size_t P[5] = { };

    CHECK_NOTHROW( lu( M, P, 5 ) );

    double expectedLU[] = 
    {  
        9.64342430e+00, -1.22570330e+00,  4.58716921e+00, -5.83018145e+00, -7.51428045e+00, // LU(0, j)
       -9.02705776e-01,  5.53495443e+00, -5.00067967e+00, -3.75554119e+00, -1.31828751e+00, // LU(1, j)
       -6.81538907e-01,  1.85818261e-03,  2.11384974e+00, -2.15333300e-01, -2.44203943e+00, // LU(2, j)
       -9.41818778e-01,  9.92886884e-01,  3.90543631e-01, -1.06867767e+01, -7.61310628e+00, // LU(3, j)
        5.89745637e-01,  5.00924916e-01, -4.68170311e-02,  3.65859817e-01,  1.74176656e+01, // LU(4, j)
    };

    size_t expectedP[] = { 1, 4, 0, 3, 2 };

    for( size_t i = 0; i < 5; ++i )
    {
        CHECK( P[i] == expectedP[i] );

        for( size_t j = 0; j < 5; ++j )
        {
            CHECK( M[i * 5 + j] == Approx( expectedLU[i * 5 + j] )
                   .epsilon( 1e-7 ).margin( 1e-7 ) );
        }
    }

    // --------------- test substitution -----------------

    double rhs[] = { -5.73507895,  6.63643545,  3.95315262, -0.00832055,  0.47981328 };

    double solution[5] = { };

    CHECK_NOTHROW( luSubstitute( expectedLU, expectedP, 5, rhs, solution ) );

    double expectedSolution[] =
    {
        1.04182070e+00,  4.82824712e-01, -7.91224906e-01,  1.10071363e-01, -1.93329855e-01
    };

    for( size_t i = 0; i < 5; ++i )
    {
        CHECK( solution[i] == Approx( expectedSolution[i] ).epsilon( 1e-8 ) );
    }


    // ----------------- test inverse --------------------

    double inverse[25] = { };

    CHECK_NOTHROW( luInvert( expectedLU, expectedP, 5, inverse ) );

    double expectedInverse[] =
    {
        -1.47601385e-01,  2.57481231e-02, -4.20978210e-03, -5.96623725e-02,  8.45846450e-02,
         4.63548835e-01,  4.30408775e-01,  4.20831567e-02, -8.74995005e-02,  2.45605207e-01,
         4.88585129e-01,  2.65933738e-01,  6.21603209e-02, -3.22741026e-02, -1.00033493e-06,
         2.87857519e-02,  5.86061643e-02, -4.09001788e-02, -7.86098520e-02,  9.84851204e-02,
         1.08913134e-02, -5.33723617e-02,  5.74129749e-02, -2.10051005e-02, -7.92413881e-03
    };

    for( size_t i = 0; i < 5; ++i )
    {
        for( size_t j = 0; j < 5; ++j )
        {
            CHECK( inverse[i * 5 + j] == Approx( expectedInverse[i * 5 + j] )
                   .epsilon( 2e-9 ).margin( 2e-9 ) );
        }
    }
}

TEST_CASE( "lu_test2" )
{
    auto J = std::array { 0.0, 0.02, 0.02, 0.0 };
    auto P = std::array<size_t, 2> { };

    lu( J.data( ), P.data( ), 2 );

    auto r = std::array { 4.2, 7.4 };
    auto x = std::array<double, 2> { };

    luSubstitute( J.data( ), P.data( ), 2, r.data( ), x.data( ) );

    CHECK( x[0] == Approx( 370.0 ).epsilon( 1e-8 ) );
    CHECK( x[1] == Approx( 210.0 ).epsilon( 1e-8 ) );
}

TEST_CASE( "elementLhs_test" )
{
    auto allsize = size_t { 13 };

    auto offset0 = size_t { 3 };
    auto size0 = size_t { 4 };
    
    auto offset1 = size_t { 5 };
    auto size1 = size_t { 3 };

    // Unsymmetric
    {
        auto target = memory::AlignedVector<double>( linalg::denseMatrixStorageSize<linalg::UnsymmetricDenseMatrix>( allsize ), 1.3 );
        auto expr = []( size_t i, size_t j ) { return i * 100.0 + j + 5.1; };

        linalg::elementLhs<linalg::UnsymmetricDenseMatrix>( target.data( ), allsize, offset0, size0, offset1, size1, expr );

        auto index = size_t { 0 };
        auto allpadded = memory::paddedLength<double>( allsize );

        for( size_t i = 0; i < allsize; ++i )
        {
            for( size_t j = 0; j < allpadded; ++j )
            {
                auto inblock = i >= offset0 && i < offset0 + size0 && j >= offset1 && j < offset1 + size1;
                auto expected = ( inblock ? ( i - offset0 ) * 100.0 + ( j - offset1 ) + 5.1 : 0.0 ) + 1.3;

                CHECK( target[index] == Approx( expected ) );

                index += 1;
            }
        }

        CHECK( index == target.size( ) );
    }

    // Symmetric
    {
        auto target = memory::AlignedVector<double>( linalg::denseMatrixStorageSize<linalg::SymmetricDenseMatrix>( allsize ), 1.3 );
        auto expr = []( size_t i, size_t j ) { return i + j + 5.1; };

        linalg::elementLhs<linalg::SymmetricDenseMatrix>( target.data( ), allsize, offset0, size0, offset1, size1, expr );

        auto index = size_t { 0 };

        for( size_t i = 0; i < allsize; ++i )
        {
            for( size_t j = 0; j < memory::paddedLength<double>( i + 1 ); ++j )
            {
                auto inblock = i >= offset0 && i < offset0 + size0 && j >= offset1 && j < offset1 + size1;
                auto expected = ( inblock ? ( i - offset0 ) + ( j - offset1 ) + 5.1 : 0.0 ) + 1.3;
                    
                CHECK( target[index] == Approx( expected ) );

                index += 1;
            }
        }

        CHECK( index == target.size( ) );
    }
}

TEST_CASE( "qr_test" )
{
    auto M = std::array
    {
        0.18, -8.96, -0.65, -6.35,
       -3.97,  0.94, -6.15,  4.61,
       -9.05, -2.54,  4.74,  4.64,
       -9.49, -1.36,  7.41, -7.18,
       -2.77, -1.75, -9.13,  1.38,
       -6.06,  9.11, -5.52,  9.14
    };

    static constexpr auto m = size_t { 6 }, n = size_t { 4 };

    auto Q = std::array<double, m * m> { };
    auto R = std::array<double, m * n> { };

    linalg::qr( M.data( ), Q.data( ), R.data( ), m, n, false );

    // Test if R is triangular
    for( size_t i = 1; i < m; ++i )
    {
        for( size_t j = 0; j < std::min( i, n ); ++j )
        {
            CHECK( std::abs( R[i * n + j] ) < 1e-14 );
        }
    }

    // Check if columns of Q are orthonormal
    for( size_t icol = 0; icol < m; ++icol )
    {
        for( size_t jcol = 0; jcol <= icol; ++jcol )
        {
            auto dot = 0.0;

            for( size_t irow = 0; irow < m; ++irow )
            {
                dot += Q[irow * m + icol] * Q[irow * m + jcol];
            }

            CHECK( std::abs( dot - ( icol == jcol ) ) < 1e-12 );
        }
    }

    // Check if we get M back from QR
    auto recoveredM = std::array<double, m * n> { };

    linalg::mmproduct( Q.data( ), R.data( ), recoveredM.data( ), m, m, n );

    CHECK( spatial::distance( M, recoveredM ) < 1e-12 );

    // =========== Same again for reduced form ===========
    std::fill( Q.begin( ), Q.end( ), 0.0 );
    std::fill( R.begin( ), R.end( ), 0.0 );
    std::fill( recoveredM.begin( ), recoveredM.end( ), 0.0 );

    linalg::qr( M.data( ), Q.data( ), R.data( ), m, n, true );

    // Test if R is triangular
    for( size_t i = 1; i < n; ++i )
    {
        for( size_t j = 0; j < i; ++j )
        {
            CHECK( std::abs( R[i * n + j] ) < 1e-14 );
        }
    }

    // Check if columns of Q are orthonormal
    for( size_t icol = 0; icol < n; ++icol )
    {
        for( size_t jcol = 0; jcol <= icol; ++jcol )
        {
            auto dot = 0.0;

            for( size_t irow = 0; irow < m; ++irow )
            {
                dot += Q[irow * n + icol] * Q[irow * n + jcol];
            }

            CHECK( std::abs( dot - ( icol == jcol ) ) < 1e-12 );
        }
    }

    // Check if we get M back from QR
    linalg::mmproduct( Q.data( ), R.data( ), recoveredM.data( ), m, n, n );

    CHECK( spatial::distance( M, recoveredM ) < 1e-12 );
}

TEST_CASE( "hessenberg_form_test" )
{
    // https://docs.scipy.org/doc/scipy/reference/generated/scipy.linalg.hessenberg.html

    static constexpr size_t n = 6;

    auto A = std::array
    {  
       -9.39,  2.51,  5.41, -0.23,  7.6 , -2.4 ,
        3.23, -5.47,  4.74,  7.04, -7.32, -4.57,
       -6.86,  6.09,  9.38,  5.83,  8.63,  4.99,
       -1.51,  9.02,  7.86, -4.62, -2.89,  1.67,
        4.33,  7.53, -4.21, -0.22,  2.33,  5.12,
       -1.95,  0.53,  3.58, -9.96, -9.08,  4.02,
    };

    auto Q = std::array<double, n * n> { };
    auto tmp = std::array<double, 2 * n> { };

    linalg::hessenberg( A.data( ), tmp.data( ), n, Q.data( ) );

    auto expectedH = std::array
    {
        -9.39            ,  -0.98421102785897,  1.41785053586788, // Row 0
        -6.14455824113947,  -6.86273392750086,  3.36294745307650, // _____
        -9.07325740845040,   3.61246262329333, -3.46724841477661, // Row 1
        -6.59677816414984,  -5.40860018141443,  7.87219986230652, // _____
         0.0             , -12.85680085723422, -1.15708820687125, // Row 2
        -5.89120384831946,   3.08495431185226,  4.35144792556196, // _____
         0.0             ,   0.0             , 12.21708200631897, // Row 3
         0.51217144678394,   4.46861989599124, -8.61248011779762, // _____
         0.0             ,   0.0             ,  0.0             , // Row 4
        14.96274020275835,   1.37443213482733,  6.66008528133276, // _____
         0.0             ,   0.0             ,  0.0             , // Row 5
         0.0             ,   4.73480539308627,  1.29802200196665  // _____
    };

    auto expectedQ = std::array
    {
         1.0             ,   0.0             ,  0.0             , // Row 0
         0.0             ,   0.0             ,  0.0             , // _____
         0.0             ,  -0.35599122284261, -0.81667168706311, // Row 1
         0.00330949504086,  -0.44707092724501,  0.08021370246651, // _____
         0.0             ,   0.75606804603724, -0.00909111489433, // Row 2
        -0.25309875273312,  -0.53837399711828,  0.27271399300959, // _____
         0.0             ,   0.16642314132890, -0.24109252311440, // Row 3
        -0.62644135429132,   0.17763233135141, -0.70013978448655, // _____
         0.0             ,  -0.47722662381068,  0.32573200959968, // Row 4
        -0.71049774404572,  -0.15369056691080,  0.37111396200764, // _____
         0.0             ,   0.21491730171612, -0.41077702029199, // Row 5
        -0.19670855077275,   0.67461617957211,  0.53969579332760  // _____
    };

    CHECK( spatial::distance( A, expectedH ) < 1e-12 );
    CHECK( spatial::distance( Q, expectedQ ) < 1e-12 );
}

TEST_CASE( "eigh_test" )
{
    auto A = std::array
    {
        28.9444, -4.292 ,  33.0485,  18.326 , 48.4529,
        -4.292 , 54.9081,  -7.8997,  -1.6762, -9.4482,
        33.0485, -7.8997,  43.6921, -19.0256, 41.7231,
        18.326 , -1.6762, -19.0256,  87.9844, -3.614 ,
        48.4529, -9.4482,  41.7231,  -3.614 , 16.3216
    };

    static constexpr size_t n = 5;

    auto tmp = std::array<double, 3 * n * n> { };
    auto U = std::array<double, n * n> { };
    auto lambda = std::array<double, n> { };

    linalg::eigh( A.data( ), lambda.data( ), tmp.data( ), n, U.data( ) );

    auto expectedLambda = std::array { -29.298747624363, -1.4828826479754,
        52.450211750614, 115.05134407397, 95.130674447754 };

    CHECK( spatial::distance( lambda, expectedLambda ) < 1e-10 );

//    std::cout << "Eigenvalues: ";
//    for( size_t i = 0; i < n; ++i )
//    {
//        std::cout << lambda[i] << ", ";
//    }
//    std::cout << std::endl;
}

} // namespace linalg
} // namespace mlhp
