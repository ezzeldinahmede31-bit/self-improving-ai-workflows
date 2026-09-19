---
name: strang-linear-algebra
description: "Applies Gilbert Strang's Linear Algebra as the working language of data: the four subspaces, elimination, orthogonality, least squares, and eigenvalues. Use when the user says 'solve Ax=b', 'least squares', 'eigenvalues', 'SVD', 'PCA', 'four subspaces', 'column space', 'nullspace', 'orthogonal', 'Gram-Schmidt', 'QR', 'diagonalization', 'positive definite', 'Strang', or when any data/model question reduces to matrices."
---

# Strang Linear Algebra

Distilled from Gilbert Strang's *Introduction to Linear Algebra* (18.06):
five ideas that answer nearly every applied matrix question.

## Purpose

Turn "what does this matrix do" into geometry: which equations are solvable,
what is the closest solvable one, and along which axes does the
transformation act.

## The five ideas (in dependency order)

1. **Solvability = column space.** Ax=b solvable iff b is a combination of
   columns. Elimination produces PA=LU; a zero row in U with nonzero b means
   no solution. Rank r = #pivots = dim(column space) = dim(row space).
2. **The four subspaces.** dim C(A)=dim C(A^T)=r; dim N(A)=n-r; dim N(A^T)=m-r.
   N(A) is orthogonal to the row space; N(A^T) to the column space. Draw the
   big picture before computing: it predicts the answer's shape.
3. **Orthogonality computes.** Gram-Schmidt: independent vectors ->
   orthonormal q's. QR: A=QR with Q orthonormal, R triangular. Least squares:
   A^TA x^=A^Tb, i.e. project b onto C(A); residual is orthogonal to every
   column. Prefer QR over normal equations numerically.
4. **Determinants test.** det=0 iff singular (a zero pivot). det = product of
   pivots = product of eigenvalues. Volume interpretation: |det| scales volumes.
5. **Eigen-structure acts.** Ax=lx: diagonalize A=SLS^-1 when n independent
   eigenvectors exist. Symmetric matrices: real eigenvalues, orthonormal
   eigenvectors, A=QLQ^T. SVD A=USV^T: the universal factorization — rank,
   norms, pseudoinverse, PCA all fall out of the singular values.

## Numerical honesty

- Never form A^TA explicitly for large/ill-conditioned problems; use QR/SVD.
- Positive definite check: all pivots > 0, or all eigenvalues > 0, or x^TAx>0.
- Condition number k(A) measures sensitivity: relative error <= k x data error.

## Verification

Answer with: the subspace picture, the factorization used, and the numerical
caveat. Then test on a 2x2 or 3x3 instance by hand.

## Pairs with

- `mathematics-for-machine-learning` (ML-side linear algebra),
  `think-stats`/`data-analysis` (least squares in practice),
  `formal-math-logic-verification-engine` (symbolic check with sympy).
