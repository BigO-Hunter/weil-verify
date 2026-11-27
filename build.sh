#!/bin/bash
# Weil verification bootstrap — deps, Mathlib cache, target build, axiom check.
# Portable: all paths derive from this script's location or CLI args.
#   ./build.sh [WEIL_DIR] [LOG_FILE]
# Defaults: WEIL_DIR=<script dir>/Weil, LOG_FILE=<script dir>/build.log
# Requires elan/lake on PATH (toolchain pinned by Weil/lean-toolchain).
set -u
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEIL_DIR="${1:-$SCRIPT_DIR/Weil}"
LOG="${2:-$SCRIPT_DIR/build.log}"
cd "$WEIL_DIR" || { echo "no Weil checkout at $WEIL_DIR" >&2; exit 1; }
echo "=== START $(date) ===" >> "$LOG"

# 1. Bootstrap remaining deps (batteries/aesop/Qq/...) + Weil.Attr
lake build Weil.Attr >> "$LOG" 2>&1
echo "=== attr exit $? $(date) ===" >> "$LOG"

# 2. Mathlib cache (network-bound, ~2-4GB)
lake exe cache get >> "$LOG" 2>&1
echo "=== cache exit $? $(date) ===" >> "$LOG"

# 3. Decisive build: target module closure (retry up to 3 attempts).
#    NOTE: DeligneWeilConjecture drags in the full ~19.4k-module Stacks closure
#    (days single-job). For the long resumable build use serial_build_multi.py
#    with LAKE_JOBS=1 instead; this step is the bootstrap-era attempt.
for i in 1 2 3; do
  LAKE_JOBS=4 LEAN_NUM_THREADS=2 lake build \
    Weil.AlgebraicGeometry.EtaleCohomology.Trace.WeilEstimateFromPurityAllEmbeddings \
    Weil.AlgebraicGeometry.EtaleCohomology.Trace.DeligneWeilConjecture \
    >> "$LOG" 2>&1
  RC=$?
  echo "=== target build attempt $i exit $RC $(date) ===" >> "$LOG"
  [ $RC -eq 0 ] && break
  sleep 20
done

# 4. Axiom check (decisive for sorry/axiom audit)
CHECK_LEAN="$(mktemp "${TMPDIR:-/tmp}/check_axioms.XXXXXX.lean")"
cat > "$CHECK_LEAN" <<'EOF'
import Weil.AlgebraicGeometry.EtaleCohomology.Trace.WeilEstimateFromPurityAllEmbeddings
import Weil.AlgebraicGeometry.EtaleCohomology.Trace.DeligneWeilConjecture
#print axioms Stacks.EtaleCohomology.isAlgebraic_and_norm_eq_of_forall_isCharpolyPureOfWeight
#print axioms Stacks.EtaleCohomology.isWeilNumber_of_forall_isCharpolyPureOfWeight
#print axioms Weil.satisfiesWeilEstimate
EOF
lake env lean "$CHECK_LEAN" >> "$LOG" 2>&1
echo "=== axioms exit $? $(date) ===" >> "$LOG"
rm -f "$CHECK_LEAN"

# 5. Full library (stretch goal)
LAKE_JOBS=4 LEAN_NUM_THREADS=2 lake build >> "$LOG" 2>&1
echo "=== full build exit $? $(date) ===" >> "$LOG"
echo "=== DONE $(date) ===" >> "$LOG"
