#!/bin/sh
# Builds a local-only ROM with private art (e.g. realistic likenesses) laid over the public sprites.
# The private art and this build live outside the repo and must never be committed.
#   ~/oddex-private/likeness/<dir>/...  mirrors game/graphics/pokemon/oddex/<dir>/
#   output: ~/oddex-private/oddex-private.gba
# Usage: tools/oddex/build_private.sh [git-ref]   (default: HEAD)
set -e
. "$(dirname "$0")/../env.sh"
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PRIV="${ODDEX_PRIVATE:-$HOME/oddex-private}"
ART="$PRIV/likeness"
TREE="$PRIV/build-tree"
REF=$(git -C "$ROOT" rev-parse "${1:-HEAD}")

if [ ! -d "$TREE/.git" ] && [ ! -f "$TREE/.git" ]; then
	git -C "$ROOT" worktree add -q --detach "$TREE" "$REF"
else
	# The overlay is the only local change in this tree, so a forced checkout just resets it.
	git -C "$TREE" checkout -q -f --detach "$REF"
fi

if [ -d "$ART" ]; then
	rsync -a "$ART"/ "$TREE/game/graphics/pokemon/oddex/"
	echo "overlaid private art from $ART"
else
	echo "no private art at $ART; building the public sprites"
fi

cd "$TREE/game"
make -j"$(sysctl -n hw.ncpu)" >"$PRIV/build-private.log" 2>&1 || { tail -20 "$PRIV/build-private.log"; exit 1; }
cp pokeemerald.gba "$PRIV/oddex-private.gba"
echo "built $PRIV/oddex-private.gba from $(git -C "$TREE" rev-parse --short HEAD)"
