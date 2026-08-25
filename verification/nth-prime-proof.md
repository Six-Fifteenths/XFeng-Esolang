# `nth-prime.xfeng` correctness argument

## Contract

Under the XFeng 1.0 semantics in `doc.md`, for every integer `n>=1`, starting
the program with `(L,R)=(n,0)` halts with `(L,R)=(p_n,0)`, where `p_n` is the
`n`-th prime and `p_1=2`.

No integer encodes a tuple or a list.  During the search, `L` is the current
candidate and `R` is the current trial divisor.  Recursion is used only as
ordinary unary control memory while values are restored.

## Arithmetic lemmas

All claims below have the indicated incoming direction and nonnegative
registers used by their callers.

1. `A` maps `(l,r,+)` to `(l+r,r,+)`.  It recursively decrements `R`; every
   returning frame increments both `L` and `R`.  It is self-mirrored: entered
   with `h=+1` it uses the right half, and with `h=-1` the left half, whose
   return path climbs above and loops around to the shared `E`, preserving
   the incoming direction `h`.
2. `G` maps `(p,d,+)` as follows for `p>=0,d>0`:

   - if `p<d`, it returns `(p,d,-)`;
   - if `p>=d`, it returns `(p-d,d,+)`.

   Proof is induction on `min(p,d)`.  Each recursive level decrements both
   registers.  `H` selects the first zero.  On return, the `p<d` branch
   restores both decrements, while the `p>=d` branch restores only `R`.
3. `D` maps `(p,d,+)` to `(p,d,h)`, where `h=+` exactly when `d` divides `p`.
   For `p=0` this is immediate.  Otherwise `G` either proves `p<d`, giving a
   nonzero remainder, or produces `p-d`.  In the latter case `D` recurses on
   itself and uses `A` to add `d` back (the recursion-and-restore loop that
   used to be a separate function `B` now lives inside `D`).  `D`'s spatial
   funnel reverses the recursive Boolean direction once, so the caller
   receives the original Boolean.  Induction on `floor(p/d)` proves the claim
   and proves that both registers are restored.

## Prime-search invariant

`X` starts with `(p,0,+)` and examines integers strictly larger than `p`.
For a candidate `c`, it sets `R=2` and invokes `D(c,R)` for consecutive
divisors `2,3,...`.  When `D` says divisible, `K` uses `G` to distinguish
`R=c` from `R<c`, restoring the subtracted value with `A`:

- `R=c` means no integer in `2..c-1` divided `c`, so `c` is prime;
- `R<c` supplies a proper divisor, so `c` is composite and `X` continues
  with `c+1`.

For every `c>=2`, the divisor loop terminates no later than `R=c`, since
`c` divides itself.  Euclid's theorem ensures a prime greater than every
finite `p`; therefore each call of `X` terminates and returns the least prime
strictly greater than its input, with `R=0`.

## N-th-prime induction

`F` recursively decrements the input `n` to zero.  Its base path sets
`(L,R)=(1,0)`.  Each of the `n` returning frames calls `X` once.  By the
prime-search invariant, the successive values are `2,3,5,...`; induction on
the number of returned frames gives `L=p_n`.  `main` then halts and outputs
`L`, while `R` remains zero.

Thus every finite input `n>=1` halts with the required result, assuming the
unbounded integer and call-stack resources specified by XFeng.  The separate
500-checkpoint run is an exact bounded implementation check; it is not used
as the proof of the universal statement.
