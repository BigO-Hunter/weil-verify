#!/bin/bash
# Weil repo verification build — detached, retrying, logged.
export PATH="/opt/homebrew/bin:$PATH"
cd /Users/dmitri.arkhipov/bigo-campaign/weil-verify/Weil
LOG=/Users/dmitri.arkhipov/bigo-campaign/weil-verify/build.log
echo "=== START $(date) ===" >> "$LOG"

# 1. Bootstrap remaining deps (batteries/aesop/Qq/...) + Weil.Attr
lake build Weil.Attr >> "$LOG" 2>&1
echo "=== attr exit $? $(date) ===" >> "$LOG"

# 2. Mathlib cache (network-bound, ~2-4GB)
lake exe cache get >> "$LOG" 2>&1
echo "=== cache exit $? $(date) ===" >> "$LOG"

# 3. Decisive build: target module closure (retry once on failure)
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
cat > /Users/dmitri.arkhipov/bigo-campaign/weil-verify/check_axioms.lean <<'EOF'
import Weil.AlgebraicGeometry.EtaleCohomology.Trace.WeilEstimateFromPurityAllEmbeddings
import Weil.AlgebraicGeometry.EtaleCohomology.Trace.DeligneWeilConjecture
#print axioms Stacks.EtaleCohomology.isAlgebraic_and_norm_eq_of_forall_isCharpolyPureOfWeight
#print axioms Stacks.EtaleCohomology.isWeilNumber_of_forall_isCharpolyPureOfWeight
#print axioms Weil.satisfiesWeilEstimate
EOF
lake env lean /Users/dmitri.arkhipov/bigo-campaign/weil-verify/check_axioms.lean >> "$LOG" 2>&1
echo "=== axioms exit $? $(date) ===" >> "$LOG"

# 5. Full library (stretch goal)
LAKE_JOBS=4 LEAN_NUM_THREADS=2 lake build >> "$LOG" 2>&1
echo "=== full build exit $? $(date) ===" >> "$LOG"
echo "=== DONE $(date) ===" >> "$LOG"
