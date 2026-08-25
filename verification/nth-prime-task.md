# XFeng unbounded nth-prime computation

Implement an XFeng 1.0 program mapping `(n,0)` to `(p_n,0)` for every
integer `n>=1` under the language's unbounded-integer and unbounded-stack
semantics.

Acceptance checks:

- no prime table, Goedel-number encoding, or prime-power packing;
- at most 41 non-comment source lines and at most 14 characters per such line;
- exact execution checkpoints for all indices 1 through 500 agree with an
  independent Eratosthenes sieve;
- input `(500,0)` halts at `(3571,0)` on this computer;
- the source terminates for every finite `n>=1` given enough resources;
- the repository unit-test suite passes.
