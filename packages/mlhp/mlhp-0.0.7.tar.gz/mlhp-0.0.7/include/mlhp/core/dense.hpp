// This file is part of the mlhp project. License: See LICENSE

#ifndef MLHP_CORE_DENSE_HPP
#define MLHP_CORE_DENSE_HPP

#include "mlhp/core/memory.hpp"
#include "mlhp/core/coreexport.hpp"

#include <cstddef>
#include <span>

namespace mlhp::linalg
{

//! In-place row-major LU decomposition with partial pivoting
MLHP_EXPORT void lu( double* M, size_t* p, size_t size );

//! Forward and backward substitution using lu decomposition
MLHP_EXPORT void luSubstitute( const double* LU, const size_t* p, size_t size, const double* b, double* u );

//! Inverse computation using lu decomposition
MLHP_EXPORT void luInvert( double* LU, size_t* p, size_t size, double* I );

//! Compute determinant based on LU decomposition (product of diagonal entries)
MLHP_EXPORT MLHP_PURE double luDeterminant( const double* LU, size_t size );

//! Inverts row major dense (size, size) matrix
MLHP_EXPORT void invert( const double* source, double* target, size_t size );

//! QR decomposition of an m x n matrix (with m >= n). 
//! Q will be (m x n) if reduce is true, otherwise (m, m). It always needs (m, m) storage though!
//! R will be (m x n), where all rows below n are zero, so effectively it's an (n, n) matrix
//! Also the reduced form will recover M = Q*R, since the values in R below n are zero
MLHP_EXPORT void qr( const double* M, double* Q, double* R, size_t m, size_t n, bool reduce = true );

//! In-place reduces the n x n matrix A with row-major storage to its Hessenberg form H 
//! (means making it "almost triangular"). The Hessenberg decomposition of a matrix full-
//! fills A = Q * H * Q^T. The matrix H only has one sub-diagonal directly below the main 
//! diagonal. This forms the first step of the QR-algorithm for eigendecomposition.
//! 
//! A: The input n x n matrix will be modified in place 
//! tmp: Required temporary storage of size 2 * n
//! Q: Optional target for also calculating the n x n matrix Q 
MLHP_EXPORT void hessenberg( double* A, double* tmp, size_t n, double* Q = nullptr );

//! Computes eigenvalues and optionally eigenvectors of a symmetric matrix using the Hessenberg 
//! QR algorithm with Wilkinson shift and deflation.
//! A: symmetric n x n matrix in row-major format (using full instead of symmetric half storage)
//! eigenvalues: vector of size n to hold eigenvalues
//! tmp: Required temporary storage of size 3 * n^2 (to hold H, Q, and R)
//! eigenvectors: n x n matrix with rows as eigenvectors if not nullptr
MLHP_EXPORT void eigh( const double* A, double* eigenvalues, double* tmp, size_t n, double* eigenvectors = nullptr );

//! Matrix multiplication for square row-major matrices
void mmproduct( const double* left, const double* right, double* target, size_t size );

//! Matrix multiplication for non-square row-major matrices
void mmproduct( const double* left, const double* right, double* target, size_t leftM, size_t leftN, size_t rightN );

//! Matrix vector products
void mvproduct( const double* M, const double* v, double* target, size_t size1, size_t size2 );
void mvproduct( const double* M, const double* v, double* target, size_t size );

template<size_t D1, size_t D2>
std::array<double, D1> mvproduct( const double* M, std::array<double, D2> v );

template<size_t D>
std::array<double, D> mvproduct( const double* M, std::array<double, D> v );

template<size_t D1, size_t D2>
std::array<double, D1> mvproduct( const std::array<double, D1 * D2>& M, std::array<double, D2> v );

// Assumptions: Aligned, padded, no aliasing
struct SymmetricDenseMatrix { };
struct UnsymmetricDenseMatrix { };

template<bool Symmetric>
struct DenseMatrixTypeHelper { using type = SymmetricDenseMatrix; };

template<>
struct DenseMatrixTypeHelper<false> { using type = UnsymmetricDenseMatrix; };

template<bool Symmetric>
using DenseMatrixType = typename DenseMatrixTypeHelper<Symmetric>::type;

template<typename MatrixType>
inline constexpr bool isSymmetricDense = std::is_same_v<MatrixType, SymmetricDenseMatrix>;

template<typename MatrixType>
inline constexpr bool isUnsymmetricDense = std::is_same_v<MatrixType, UnsymmetricDenseMatrix>;

template<typename DenseMatrixType>
constexpr size_t denseRowIncrement( size_t iRow, size_t paddedLength );

template<typename T = double>
auto symmetricNumberOfBlocks( size_t iRow );

template<typename T = double>
auto symmetricDenseOffset( size_t rowI, size_t columnJ );

template<typename MatrixType, typename T>
auto indexDenseMatrix( T* matrix, size_t i, size_t j, size_t paddedSize );

template<typename MatrixType, typename T = double>
auto denseMatrixStorageSize( size_t size );

template<typename TargetMatrixType, typename MatrixExpr>
void elementLhs( double* target, size_t size, size_t nblocks, MatrixExpr&& expression );

// Write block into dense matrix (symmetric version only writes lower trianglular part)
template<typename TargetMatrixType, typename MatrixExpr> inline
void elementLhs( double* target, size_t allsize1, 
                 size_t offset0, size_t size0, 
                 size_t offset1, size_t size1, 
                 MatrixExpr&& expression );

template<typename MatrixExpr>
void unsymmetricElementLhs( double* target, size_t size, size_t nblocks, MatrixExpr&& function );

// Same as above but assuming upper storage
template<typename MatrixExpr>
void symmetricElementLhs( double* target, size_t size, size_t nblocks, MatrixExpr&& function );

// In-place addition of a vector with a given expression, assuming no aliasing.
template<typename VectorExpr = void>
void elementRhs( double* target, size_t size, size_t nblocks, VectorExpr&& function );

template<typename T>
auto adapter( T&& span, size_t size1 );

} // namespace mlhp::linalg

#include "mlhp/core/dense_impl.hpp"

#endif // MLHP_CORE_DENSE_HPP
