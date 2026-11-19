#!/usr/bin/env bash
# `make check-oddex`: the gates for what the compiler cannot catch. Disabled vanilla species
# still compile (their SPECIES_* constants exist), so leftovers only show up as vanilla
# references in content or as debug-build crash screens at run time.
#
# Scopes marked `strict = true` in content/migration_scope.toml must have no vanilla references.
#
# Environment:
#   ODDEX_REGRESSION_SCRIPTS space-separated names under tools/headless/scripts/
#   ODDEX_SHOTS_BASELINE     dir with <script>/<shot>.png to compare pixel-exactly
#                            (default tools/headless/baselines; set empty to skip)
#   ODDEX_RUN                headless runner (default ~/oddex-toolchain/bin/oddex-run)
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
ROM="$ROOT/game/pokeemerald.gba"
OUT="$ROOT/game/build/oddex-check"
RUN="${ODDEX_RUN:-$HOME/oddex-toolchain/bin/oddex-run}"
SCRIPTS="${ODDEX_REGRESSION_SCRIPTS:-to_littleroot to_starter oddex_gallery to_petalburg}"
ODDEX_SHOTS_BASELINE="${ODDEX_SHOTS_BASELINE-$ROOT/tools/headless/baselines}"
fail=0

echo "== generated species files are up to date"
python3 "$ROOT/tools/oddex/gen_species.py" --check || fail=1

echo "== vanilla species references (all content, counts only)"
python3 "$ROOT/tools/oddex/check_species_refs.py" --summary

echo "== migrated scopes must be free of vanilla species (content/migration_scope.toml, strict = true)"
python3 "$ROOT/tools/oddex/check_species_refs.py" --strict-scopes || fail=1

echo "== map checks (new findings fail; accepted ones are in tools/oddex/check_maps_baseline.json)"
python3 "$ROOT/tools/oddex/check_maps.py" || fail=1

echo "== headless regression scripts (any crash screen fails)"
if [ ! -x "$RUN" ]; then
    echo "oddex-run not found at $RUN; build it with tools/headless/build.sh"
    exit 1
fi
for name in $SCRIPTS; do
    dir="$OUT/$name"
    rm -rf "$dir" && mkdir -p "$dir"
    if ! (cd "$dir" && "$RUN" "$ROM" "$ROOT/tools/headless/scripts/$name.txt" > run.log 2> err.log); then
        echo "$name: runner failed (see $dir/err.log)"
        fail=1
        continue
    fi
    if grep -q ODDEX_CRASH_SCREEN "$dir/err.log"; then
        echo "$name: crash screen"
        grep ODDEX_CRASH_SCREEN "$dir/err.log" | sort | uniq -c
        fail=1
        continue
    fi
    shots=$(find "$dir" -name '*.png' | wc -l | tr -d ' ')
    if [ -n "${ODDEX_SHOTS_BASELINE:-}" ] && [ -d "$ODDEX_SHOTS_BASELINE/$name" ]; then
        diffs=0
        for base in "$ODDEX_SHOTS_BASELINE/$name"/*.png; do
            shot=$(find "$dir" -name "$(basename "$base")" | head -1)
            if [ -z "$shot" ] || ! cmp -s "$base" "$shot"; then
                echo "$name: differs from baseline: $(basename "$base")"
                diffs=$((diffs + 1))
            fi
        done
        [ "$diffs" -eq 0 ] || fail=1
        echo "$name: $shots shots, $diffs baseline differences"
    else
        echo "$name: ok ($shots shots)"
    fi
done

exit $fail
