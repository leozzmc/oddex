"""Load and validate content/migration_scope.toml (shared by apply_replacements and check_species_refs)."""
import fnmatch
import glob
import json
import os
import re
import tomllib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCOPE_FILE = os.path.join(ROOT, "content", "migration_scope.toml")
FIELDS = {"description", "strict", "wild_maps", "wild_kinds", "trainers", "maps", "exclude_maps", "exclude_refs", "c_files"}


class Scope:
    def __init__(self, name, data, game):
        self.name = name
        self.strict = bool(data.get("strict", False))
        self.wild_maps = set(data.get("wild_maps", []))
        self.wild_kinds = set(data.get("wild_kinds", []))
        self.trainers = set(data.get("trainers", []))
        self.maps = list(data.get("maps", []))
        self.exclude_maps = list(data.get("exclude_maps", []))
        self.exclude_refs = set(data.get("exclude_refs", []))
        self.c_files = set(data.get("c_files", []))
        self._validate(data, game)

    def _validate(self, data, game):
        errors = [f"unknown field {k}" for k in data if k not in FIELDS]
        names = set()
        for path in glob.glob(os.path.join(game, "data/maps/*/map.json")):
            with open(path, encoding="utf-8") as f:
                names.add(json.load(f)["name"])
        for m in self.wild_maps - names:
            errors.append(f"wild_maps: no map named {m}")
        for pattern in self.maps + self.exclude_maps:
            if not fnmatch.filter(names, pattern):
                errors.append(f"maps: {pattern} matches no map")
        with open(os.path.join(game, "src/data/trainers.party"), encoding="utf-8") as f:
            defined = set(re.findall(r"^=== (TRAINER_\w+) ===", f.read(), re.M))
        for t in sorted(self.trainers - defined):
            errors.append(f"trainers: {t} is not in trainers.party")
        for ref in self.exclude_refs:
            path = ref.rsplit(":", 1)[0]
            if not os.path.exists(os.path.join(game, path)):
                errors.append(f"exclude_refs: {path} does not exist")
        for c in self.c_files:
            if not os.path.exists(os.path.join(game, c)):
                errors.append(f"c_files: {c} does not exist")
        if errors:
            raise SystemExit(f"{os.path.relpath(SCOPE_FILE, ROOT)} [{self.name}]: " + "; ".join(errors))

    def has_map(self, name):
        return any(fnmatch.fnmatchcase(name, p) for p in self.maps) and not any(fnmatch.fnmatchcase(name, p) for p in self.exclude_maps)

    def has_wild(self, map_name, kind):
        return map_name in self.wild_maps and (not self.wild_kinds or kind in self.wild_kinds)

    def excludes(self, path, species):
        return f"{path}:{species}" in self.exclude_refs


def load(game, path=SCOPE_FILE):
    with open(path, "rb") as f:
        data = tomllib.load(f)
    return {name: Scope(name, body, game) for name, body in data.items() if isinstance(body, dict)}


def get(game, names, path=SCOPE_FILE):
    scopes = load(game, path)
    missing = [n for n in names if n not in scopes]
    if missing:
        raise SystemExit(f"unknown scope {', '.join(missing)}; defined: {', '.join(scopes)}")
    return [scopes[n] for n in names]
