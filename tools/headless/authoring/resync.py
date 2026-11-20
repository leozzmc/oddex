"""Re-sync a long regression script after a ROM change shifted its RNG (new species, art, layout).

usage:
  resync.py prepare OLD_GAME WORK SCRIPT   flatten SCRIPT (includes inlined) into chunks, run them on the
                                           old ROM (OLD_GAME: a built game/ dir of the commit the script
                                           was recorded on, e.g. a git worktree) and the current one with a
                                           savestate after each chunk; print the first chunk that differs
  resync.py run WORK [FROM]                re-author chunks from the first divergence (or FROM) on;
                                           stops at a chunk it cannot fix (fix it by hand: write
                                           WORK/res/chunkK.txt and WORK/res/cpK.ss, then run again)
  resync.py shots WORK K NAME...           put 'shot shots/NAME.png' in chunk K after the frame closest
                                           to each baseline (tools/headless/baselines/*/NAME.png)
  resync.py assemble WORK                  rewrite the scripts in tools/headless/scripts from the chunks

A chunk ends before a comment block, at a file boundary and after 40 commands. A re-authored chunk is
accepted when it ends where the old one did (map, x, y; inside a message only if the old one was), the
lead is not lower, and it beat at least as many trainers as the old chunk (position alone once walked
past a gym leader). Strategies, in order: replay the old commands; finish what the replay left open
(battle presses / B); finish then autopilot or stepwalk to the old position; autopilot; stepwalk
(map data, then the live grid); autopilot to the door of the old map, then stepwalk inside; follow the
old run command by command (its per-command trace on the old ROM), finishing battles only the new run
has, skipping battle inputs only the old run needed and walking back onto the old path. Screenshots in
a re-authored chunk are dropped (the log says which): put them back with `shots`. A long grind is
better redone by hand (autopilot grind:) than chunk by chunk: write its result as the chunk and an
empty chunk file for each chunk it covers.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SCRIPTS = os.path.join(ROOT, "tools", "headless", "scripts")
BASELINES = os.path.join(ROOT, "tools", "headless", "baselines")
CHUNK = 40
FLAGS_OFFSET = 4720  # offsetof(struct SaveBlock1, flags) in this build; shortcut: hard-coded, re-measure if SaveBlock1 changes


def flatten(script, sdir=SCRIPTS):
    """[{'file', 'lines': [(lineno, text)]}] with includes inlined; comments are kept out of chunks."""
    chunks = [{"file": None, "lines": []}]

    def cut(name):
        if chunks[-1]["lines"]:
            chunks.append({"file": name, "lines": []})
        chunks[-1]["file"] = name

    def walk(name):
        cut(name)
        n = 0
        for i, l in enumerate(open(os.path.join(sdir, name)).read().split("\n")):
            if l.startswith("include "):
                walk(l.split()[1]); cut(name); n = 0
            elif l.startswith("#"):
                cut(name); n = 0
            elif l.strip():
                chunks[-1]["lines"].append((i, l))
                if not l.startswith("shot"):
                    n += 1
                    if n >= CHUNK:
                        cut(name); n = 0
    walk(script)
    return [c for c in chunks if c["lines"]]


def accept(new, old, need, old_free):
    """new/old: (map, x, y, free, level, trainers); need: trainers the new run must have by now."""
    return new[:3] == old[:3] and (new[3] or not old_free) and new[4] >= old[4] and new[5] >= need


def assemble(chunks, texts, first, sdir=SCRIPTS):
    """{file: new text}: chunks from `first` on replaced by texts[k] at their first line; comments kept."""
    owner = {(c["file"], i): k for k, c in enumerate(chunks) for i, _ in c["lines"]}
    out = {}
    for name in sorted({c["file"] for c in chunks[first:]}):
        res, done = [], set()
        for i, l in enumerate(open(os.path.join(sdir, name)).read().split("\n")):
            k = owner.get((name, i))
            if k is None or k < first:
                res.append(l)
            elif k not in done:
                done.add(k); res.extend(texts[k])
        out[name] = "\n".join(res)
    return out


def main():
    a = sys.argv[1:]
    ARGV, sys.argv = a, [os.path.join(HERE, "autopilot.py")]
    G = {"__file__": sys.argv[0], "__name__": "resync"}
    exec(compile(open(sys.argv[0]).read().replace("\nmain()\n", "\n"), sys.argv[0], "exec"), G)
    W, RUN = G["W"], G["RUN"]
    cmd, work = ARGV[0], os.path.abspath(ARGV[2] if ARGV[0] == "prepare" else ARGV[1])
    meta_path = os.path.join(work, "meta.json")

    def game_syms(game):
        out = {}
        for line in subprocess.run([W["NM"], game + "/pokeemerald.elf"], capture_output=True, text=True).stdout.splitlines():
            p = line.split()
            if len(p) == 3:
                out[p[2]] = int(p[0], 16)
        return out

    def game_names(game):
        groups = json.load(open(game + "/data/maps/map_groups.json"))
        return {(gi, mi): m for gi, g in enumerate(groups["group_order"]) for mi, m in enumerate(groups[g])}

    def sigfn(game):
        syms, names = game_syms(game), game_names(game)
        tbase = int(re.search(r"#define TRAINER_FLAGS_START\s+(0x\w+)", open(game + "/include/constants/flags.h").read()).group(1), 16)

        def sig(ss):
            st = W["state"](ss); rd = W["read"]
            sb1 = rd(st, syms["gSaveBlock1Ptr"], "<I")[0]
            if not sb1:
                return (None, 0, 0, False, 0, 0)
            x, y = rd(st, sb1, "<hh"); g, n = rd(st, sb1 + 4, "<bb")
            free = (rd(st, syms["gMain"] + 4, "<I")[0] & ~1) == (syms["CB2_Overworld"] & ~1) \
                and not rd(st, syms["sLockFieldControls"], "<B")[0] and rd(st, syms["sGlobalScriptContextStatus"], "<B")[0] != 0
            lvl = rd(st, syms["gParties"] + 84, "<B")[0]
            tr = sum(bin(b).count("1") for b in rd(st, sb1 + FLAGS_OFFSET + tbase // 8, "<110B"))
            return (names.get((g, n)), x, y, free, lvl, tr)
        return sig

    if cmd == "prepare":
        old_game, script = os.path.abspath(ARGV[1]), ARGV[3]
        chunks = flatten(script)
        os.makedirs(work + "/old", exist_ok=True); os.makedirs(work + "/new", exist_ok=True); os.makedirs(work + "/res", exist_ok=True)
        json.dump({"script": script, "old_game": old_game, "chunks": chunks}, open(meta_path, "w"))
        for side, rom in (("old", old_game + "/pokeemerald.gba"), ("new", G["ROM"])):
            with open(f"{work}/{side}/run.txt", "w") as f:
                for k, c in enumerate(chunks):
                    for _, l in c["lines"]:
                        f.write((f"shot {work}/{side}/{l.split()[1].split('/')[-1]}" if l.startswith("shot") else l) + "\n")
                    f.write(f"save {work}/{side}/cp{k:04d}.ss\n")
        procs = [subprocess.Popen([RUN, rom, f"{work}/{side}/run.txt"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                 for side, rom in (("old", old_game + "/pokeemerald.gba"), ("new", G["ROM"]))]
        for p in procs:
            p.wait()
        osig, nsig = sigfn(old_game), sigfn(os.path.dirname(G["ROM"]))
        sigs = [osig(f"{work}/old/cp{k:04d}.ss") for k in range(len(chunks))]
        json.dump(sigs, open(f"{work}/old_sig.json", "w"))
        for k in range(len(chunks)):
            if nsig(f"{work}/new/cp{k:04d}.ss") != tuple(sigs[k]):
                print(f"first difference: chunk {k} ({chunks[k]['file']}:{chunks[k]['lines'][0][0] + 1}) "
                      f"old {sigs[k]} new {nsig(f'{work}/new/cp{k:04d}.ss')}")
                break
        else:
            print("no difference")
        return

    meta = json.load(open(meta_path)); chunks = meta["chunks"]
    sigs = [tuple(s) for s in json.load(open(f"{work}/old_sig.json"))]
    nsig = sigfn(os.path.dirname(G["ROM"]))

    def text(k):
        p = f"{work}/res/chunk{k:04d}.txt"
        return [l for l in open(p).read().split("\n") if l.strip() and not l.startswith("# resync")] if os.path.exists(p) \
            else [l for _, l in chunks[k]["lines"]]

    if cmd == "assemble":
        first = min((k for k in range(len(chunks)) if os.path.exists(f"{work}/res/chunk{k:04d}.txt")), default=len(chunks))
        for name, t in assemble(chunks, {k: text(k) for k in range(len(chunks))}, first).items():
            open(os.path.join(SCRIPTS, name), "w").write(t)
            print("wrote", name)
        return

    def expand(cmds):
        out = []
        for c in cmds:
            m = re.match(r"repeat (\d+) (.*)", c)
            out += [m.group(2)] * int(m.group(1)) if m else [c]
        return out

    def start_of(k):
        p = f"{work}/res/cp{k - 1:04d}.ss"
        return p if os.path.exists(p) else f"{work}/new/cp{k - 1:04d}.ss"

    if cmd == "shots":
        from PIL import Image, ImageChops
        k, names = int(ARGV[2]), ARGV[3:]
        cmds = expand([l for l in text(k) if not l.startswith("shot") and not l.startswith("#")])
        d = f"{work}/scan{k}"; os.makedirs(d, exist_ok=True)
        with open(f"{d}/run.txt", "w") as f:
            f.write(f"load {start_of(k)}\n" + "".join(f"{c}\nshot {d}/{i:05d}.png\n" for i, c in enumerate(cmds)))
        subprocess.run([RUN, G["ROM"], f"{d}/run.txt"], capture_output=True)
        at = {}
        for n in names:
            base = Image.open(next(p for p in (os.path.join(BASELINES, b, n + ".png") for b in os.listdir(BASELINES))
                                   if os.path.exists(p))).convert("RGB")
            score = lambda i: ImageChops.difference(base, Image.open(f"{d}/{i:05d}.png").convert("RGB")).convert("L").point(
                lambda v: 255 if v else 0).histogram()[255]
            best = min(range(len(cmds)), key=score)
            at.setdefault(best, []).append(n); print(n, "after command", best, "differing pixels", score(best))
        out = []
        for i, c in enumerate(cmds):
            out.append(c); out += [f"shot shots/{n}.png" for n in at.get(i, [])]
        open(f"{work}/res/chunk{k:04d}.txt", "w").write("\n".join(G["compress"](out)) + "\n")
        return

    # run
    def first_diff():
        for k in range(len(chunks)):
            if not os.path.exists(f"{work}/res/cp{k:04d}.ss") and nsig(f"{work}/new/cp{k:04d}.ss") != sigs[k]:
                return k
        return len(chunks)
    k0 = int(ARGV[2]) if len(ARGV) > 2 else first_diff()
    osig = sigfn(meta["old_game"])
    for k in range(k0, len(chunks)):
        if os.path.exists(f"{work}/res/cp{k:04d}.ss") and os.path.exists(f"{work}/res/chunk{k:04d}.txt"):
            continue  # fixed by hand or an earlier run
        lines = [l for _, l in chunks[k]["lines"]]
        cmds, shots = [l for l in lines if not l.startswith("shot")], [l for l in lines if l.startswith("shot")]
        ss, old = start_of(k), sigs[k]
        need = old[5] - (sigs[k - 1][5] if k else 0) + nsig(ss)[5]
        ok = lambda e: e and accept(nsig(e), old, need, old[3])
        tag = f"{work}/res/k{k:04d}"
        replay = tag + "_replay.ss"; G["run"](ss, cmds, replay)

        cache = {}

        def fin(start, prefix):
            if start in cache:
                return cache[start]
            cache[start] = fin1(start, prefix)
            return cache[start]

        def fin1(start, prefix):
            cur, out = start, []
            for i in range(900):
                if G["where"](cur)[3] == "CB2_Overworld" and G["controls_free"](cur):
                    return cur, prefix + G["compress"](out)
                c = G["battle_press"](cur) if G["where"](cur)[3] != "CB2_Overworld" else "press B 2 30"
                nxt = f"{tag}_f{i:03d}.ss"; G["run"](cur, [c], nxt); cur = nxt; out.append(c)
            return None, []

        def tool(start, name, args, env=None):
            r = subprocess.run([sys.executable, "-I", os.path.join(HERE, name), start, f"{tag}_{name[:2]}", *args],
                               capture_output=True, text=True, env={**os.environ, **(env or {})})
            m = re.search(r"# end \(.*\) facing \w+ state (\S+)", r.stderr)
            return (m.group(1), [l for l in r.stdout.split("\n") if l.strip()]) if m else (None, [])

        def ap(start, mp, x, y):
            return tool(start, "autopilot.py", ["DOWN", f"{mp}:{x}:{y}"], {"AP_PARTIAL": "1"})

        def sw(start, mp, x, y, live=False):
            return tool(start, "stepwalk.py", [mp, str(x), str(y)] + (["--live"] if live else []))

        def then(first, f):
            e1, c1 = first
            if not e1:
                return None, []
            e2, c2 = f(e1)
            return (e2, c1 + c2) if e2 else (None, [])

        def door(start):
            main = old[0].split("_")[0]
            if main == old[0] or main not in G["ID2NAME"].values():
                return None, []
            for w in G["load"](main)["json"]["warp_events"]:
                if G["ID2NAME"].get(w["dest_map"]) == old[0]:
                    for walk in (lambda: ap(start, main, w["x"], w["y"] + 1), lambda: sw(start, main, w["x"], w["y"] + 1, True)):
                        e, c = then(walk(), lambda e1: sw(e1, *old[:3]))
                        if ok(e):
                            return e, c
            return None, []

        def follow(start):
            trace_run = f"{tag}_trace.txt"; ex = expand(cmds)
            with open(trace_run, "w") as f:
                f.write(f"load {work}/old/cp{k - 1:04d}.ss\n" + "".join(f"{c}\nsave {tag}_o{i:05d}.ss\n" for i, c in enumerate(ex)))
            subprocess.run([RUN, meta["old_game"] + "/pokeemerald.gba", trace_run], capture_output=True)
            trace = [sigs[k - 1]] + [osig(f"{tag}_o{i:05d}.ss") for i in range(len(ex))]
            cur, out, n = start, [], [0]

            def step(c):
                nonlocal cur
                n[0] += 1; nxt = f"{tag}_s{n[0]:05d}.ss"; G["run"](cur, [c], nxt); cur = nxt; out.append(c)

            def settle():
                for _ in range(900):
                    s = nsig(cur)
                    if s[3]:
                        return
                    step(G["battle_press"](cur) if G["where"](cur)[3] != "CB2_Overworld" else "press B 2 30")

            def goto(mp, x, y):
                nonlocal cur
                if nsig(cur)[:3] == (mp, x, y):
                    return True
                for e, c in (sw(cur, mp, x, y), sw(cur, mp, x, y, True), ap(cur, mp, x, y)):
                    if e and nsig(e)[:3] == (mp, x, y):
                        cur = e; out.extend(c); return True
                return False

            for i, c in enumerate(ex):
                before = trace[i]
                if before[3]:                                      # the old run was walking here
                    settle()
                    if not goto(*before[:3]):
                        return None, []
                    step(c)
                elif not (nsig(cur)[3] and c.startswith("press") and " 2 " in c):
                    step(c)                                        # else: nothing to answer on the new run
            settle()
            if not goto(*old[:3]):
                return None, []
            return cur, out

        strategies = [
            ("replay", lambda: (replay, cmds)),
            ("finish", lambda: fin(replay, cmds)),
            ("finish+autopilot", lambda: then(fin(replay, cmds), lambda e: ap(e, *old[:3]))),
            ("finish+stepwalk", lambda: then(fin(replay, cmds), lambda e: sw(e, *old[:3], nsig(e)[0] == old[0]))),
            ("autopilot", lambda: ap(ss, *old[:3])),
            ("stepwalk", lambda: sw(ss, *old[:3])),
            ("stepwalk --live", lambda: sw(ss, *old[:3], True)),
            ("door", lambda: door(ss)),
            ("follow", lambda: follow(ss)),
        ]
        for name, f in strategies:
            end, out = f()
            if end and not old[3] and nsig(end)[3] and nsig(end)[:3] == old[:3] and name != "replay":
                # The old chunk ended inside an interaction: redo its inputs after its last walk.
                last = max([i for i, c in enumerate(cmds) if c.startswith("hold")], default=-1)
                t = f"{tag}_tail.ss"; G["run"](end, cmds[last + 1:], t); end, out = t, out + cmds[last + 1:]
            if ok(end):
                kept = lines if name == "replay" else out
                open(f"{work}/res/chunk{k:04d}.txt", "w").write(
                    (f"# resync {name}; shots dropped: {' '.join(s.split('/')[-1] for s in shots)}\n" if shots and name != "replay" else "")
                    + "\n".join(kept) + "\n")
                subprocess.run(["cp", end, f"{work}/res/cp{k:04d}.ss"])
                print(f"{name} {k} {nsig(end)}" + (f" SHOTS DROPPED {len(shots)}" if shots and name != "replay" else ""), flush=True)
                break
        else:
            print(f"STUCK at chunk {k} ({chunks[k]['file']}:{chunks[k]['lines'][0][0] + 1}): old {old}, replay {nsig(replay)}")
            sys.exit(1)


if __name__ == "__main__":
    main()
