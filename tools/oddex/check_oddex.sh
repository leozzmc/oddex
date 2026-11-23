#!/usr/bin/env bash
# `make check-oddex`: the gates for what the compiler cannot catch. Disabled vanilla species
# still compile (their SPECIES_* constants exist), so leftovers only show up as vanilla
# references in content or as debug-build crash screens at run time.
#
# Scopes marked `strict = true` in content/migration_scope.toml must have no vanilla references.
#
# Environment:
#   ODDEX_REGRESSION_SCRIPTS space-separated names under tools/headless/scripts/
#   ODDEX_BASELINE_SCRIPTS   scripts whose baselines are compared (default: the scripts run); a script
#                            only included by a run one is covered by that run's shots
#   ODDEX_SHOTS_BASELINE     dir with <script>/<shot>.png to compare pixel-exactly
#                            (default tools/headless/baselines; set empty to skip)
#   ODDEX_RUN                headless runner (default ~/oddex-toolchain/bin/oddex-run)
set -uo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
ROM="$ROOT/game/pokeemerald.gba"
OUT="$ROOT/game/build/oddex-check"
RUN="${ODDEX_RUN:-$HOME/oddex-toolchain/bin/oddex-run}"
SCRIPTS="${ODDEX_REGRESSION_SCRIPTS:-oddex_title to_littleroot to_starter oddex_gallery oddex_dex to_petalburg to_dolls}"
ODDEX_SHOTS_BASELINE="${ODDEX_SHOTS_BASELINE-$ROOT/tools/headless/baselines}"
BASELINES="${ODDEX_BASELINE_SCRIPTS:-$SCRIPTS}"  # whose baselines to compare (default: the scripts run)
fail=0

echo "== tool unit tests"
for t in "$ROOT"/tools/oddex/test_*.py; do
    python3 -W error::ResourceWarning "$t" -q 2>&1 | tail -1 | sed "s|^|$(basename "$t"): |"
    [ "${PIPESTATUS[0]}" -eq 0 ] || fail=1
done

echo "== generated species files are up to date"
python3 "$ROOT/tools/oddex/gen_species.py" --check || fail=1

echo "== vanilla species references (all content, counts only)"
python3 "$ROOT/tools/oddex/check_species_refs.py" --summary

echo "== migrated scopes must be free of vanilla species (content/migration_scope.toml, strict = true)"
python3 "$ROOT/tools/oddex/check_species_refs.py" --strict-scopes || fail=1

echo "== map checks (new findings fail; accepted ones are in tools/oddex/check_maps_baseline.json)"
python3 "$ROOT/tools/oddex/check_maps.py" || fail=1

echo "== headless regression scripts (any crash screen or game reset fails)"
if [ ! -x "$RUN" ]; then
    echo "oddex-run not found at $RUN; build it with tools/headless/build.sh"
    exit 1
fi
# gMain.vblankCounter1 (offset 0x20) only drops when the game resets, which shows no crash screen.
gmain=$(arm-none-eabi-nm "$ROOT/game/pokeemerald.elf" | awk '$3 == "gMain" { print $1 }')
if [ -z "$gmain" ]; then
    echo "gMain not found in pokeemerald.elf; cannot watch for resets"
    exit 1
fi
export ODDEX_RESET_WATCH=$(printf '0x%x' $((0x$gmain + 0x20)))
# Each script runs from boot in its own directory, so they can all run at once.
for name in $SCRIPTS; do
    dir="$OUT/$name"
    rm -rf "$dir" && mkdir -p "$dir"
    (cd "$dir" && "$RUN" "$ROM" "$ROOT/tools/headless/scripts/$name.txt" > run.log 2> err.log; echo $? > status) &
done
wait
dirs=""
for name in $SCRIPTS; do
    dir="$OUT/$name"
    if [ "$(cat "$dir/status")" != 0 ]; then
        echo "$name: runner failed (see $dir/err.log)"
        fail=1
    elif grep -q -E 'ODDEX_CRASH_SCREEN|ODDEX_RESET' "$dir/err.log"; then
        echo "$name: crash screen or game reset"
        grep -E 'ODDEX_CRASH_SCREEN|ODDEX_RESET' "$dir/err.log" | sort | uniq -c
        fail=1
    else
        dirs="$dirs $dir"
        echo "$name: ran, $(find "$dir" -name '*.png' | wc -l | tr -d ' ') shots"
    fi
done
# A script that includes another (to_winona includes to_norman ... to_starter) takes the included
# script's shots too; shot names are unique across baselines, so one run covers every prefix.
for name in $BASELINES; do
    [ -n "${ODDEX_SHOTS_BASELINE:-}" ] && [ -d "$ODDEX_SHOTS_BASELINE/$name" ] || continue
    diffs=0
    for base in "$ODDEX_SHOTS_BASELINE/$name"/*.png; do
        shot=$([ -n "$dirs" ] && find $dirs -name "$(basename "$base")" | head -1)
        if [ -z "$shot" ] || ! cmp -s "$base" "$shot"; then
            echo "$name: differs from baseline: $(basename "$base")"
            diffs=$((diffs + 1))
        fi
    done
    [ "$diffs" -eq 0 ] || fail=1
    echo "$name: $diffs baseline differences"
done

exit $fail
