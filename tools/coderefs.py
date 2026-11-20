"""Align the code and API references of the report editions to a target DraCor release.

The book is not changed. Results go to coderefs/ (machine readable):

  code-links.csv     one row per occurrence of a GitHub permalink into dracor-api,
                     dracor-frontend or dracor-metrics: where it occurs, the code unit
                     (function/component) at the referenced lines, and where that unit
                     is in the target release (status, similarity, target permalink,
                     releases/commits that changed it since the report commit)
  code-units.csv     one row per referenced code unit with all passages that cite it
  api-refs.csv       one row per occurrence of an API reference (API URL, Swagger deep
                     link dracor.org/doc/api#/public/<operationId>, or an endpoint path
                     in code spans): the operation it meant and the matching path and
                     operationId in the target API spec
  summary.json       counts

Targets (edit TARGET below): dracor-api 1.5.0-rc.1, dracor-frontend 3.0.0-rc.1
(TypeScript rewrite; components also searched in dracor-react 1.11.0), dracor-metrics 1.6.0.
For dracor-api, the target unit is also compared with main (HEAD of the fetched clone),
so changes after the release candidate show up.

Needs clones of the repos (with tags) in $CODEREFS_REPOS (default .cache/repos):
  git clone https://github.com/dracor-org/<repo>.git .cache/repos/<repo>

usage: .venv/bin/python tools/coderefs.py
"""
import collections
import csv
import difflib
import json
import os
import re
import subprocess
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
OUT = ROOT / "coderefs"
REPOS = Path(os.environ.get("CODEREFS_REPOS", ROOT / ".cache/repos"))
TARGET = {"dracor-api": "1.5.0-rc.1", "dracor-frontend": "3.0.0-rc.1", "dracor-metrics": "1.6.0"}
REACT = ("dracor-react", "1.11.0")
FORMAT_ONLY = re.compile(r"\b(prettier|[Ff]ormat(ting)?\b.*\bcode\b|[Rr]eformat)")
API_MAIN = "gh/main"  # remote-tracking ref of dracor-api main in the clone (optional)
# publication dates: links to a branch (e.g. blob/main/...) are resolved to the branch
# state at that date
REPORT_DATE = {"clsinfra-d71": "2023-02-27", "clsinfra-d72": "2023-04-28",
               "clsinfra-d73": "2024-02-27", "clsinfra-d74": "2025-07-10"}
OLD_SPECS = ["v0.87.1", "v1.0.0", "v1.1.0", "1.4.1"]  # report-era specs, for old path templates
LINK = re.compile(r"https://github\.com/dracor-org/(dracor-api|dracor-frontend|dracor-metrics)/(?:blob|tree)/"
                  r"([\w.-]+)/([^\s)>\]#]+)(?:#L(\d+)(?:-L(\d+))?)?")
MDLINK = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


def git(repo, *a):
    r = subprocess.run(["git", "-C", str(REPOS / repo), *a], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else None


def vkey(v):
    return [int(x) if x.isdigit() else 0 for x in re.split(r"[.-]", v)]


# ---------------------------------------------------------------- code units
def pats_for(path):
    if path.endswith((".xqm", ".xq", ".xql")):
        return [r"declare\s+(?:%[^\n]*\s+)*function\s+([\w-]+:[\w-]+)\s*\(", r"^\s*function\s+([\w-]+:[\w-]+)\s*\("]
    if path.endswith((".js", ".jsx", ".ts", ".tsx")):
        return [r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)",
                r"^\s*(?:export\s+)?const\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s*)?\(",
                r"^\s*(?:export\s+)?const\s+(\w+)\s*(?::[^=]+)?=\s*(?:async\s+)?\w+\s*=>",
                r"^\s*(?:export\s+default\s+)?class\s+(\w+)"]
    if path.endswith(".py"):
        return [r"^\s*(?:async\s+)?def\s+(\w+)", r"^\s*class\s+(\w+)"]
    return []


def decl_at(lines, i, pats):
    for p in pats:
        m = re.search(p, lines[i])
        if m:
            return m.group(1)
    return None


def find_unit(lines, a, b, pats):
    for i in range(a - 1, min(b + 6, len(lines))):
        n = decl_at(lines, i, pats)
        if n:
            return n, i
    for i in range(min(a - 2, len(lines) - 1), max(a - 300, -1), -1):
        n = decl_at(lines, i, pats)
        if n:
            return n, i
    return None, None


def unit_end(lines, start, pats):
    ind = len(lines[start]) - len(lines[start].lstrip())
    for j in range(start + 1, len(lines)):
        l = lines[j]
        if l.strip() and len(l) - len(l.lstrip()) <= ind and decl_at(lines, j, pats):
            k = j
            while k - 1 > start and (not lines[k - 1].strip() or
                                     lines[k - 1].lstrip().startswith(("%", "(:", ":)", "//", "#", "*", "/*", "@"))):
                k -= 1
            return k
    return len(lines)


def all_units(lines, pats):
    starts = [(decl_at(lines, i, pats), i) for i in range(len(lines))]
    return [(n, i, unit_end(lines, i, pats)) for n, i in starts if n]


def norm(block):
    """Token sequence of a code block, without comments and layout: a reformatting
    (e.g. prettier on the XQuery code in 1.5.0-beta.1) does not count as a change."""
    t = "\n".join(block)
    t = re.sub(r"\(:.*?:\)", " ", t, flags=re.S)       # XQuery comments
    t = re.sub(r"/\*.*?\*/", " ", t, flags=re.S)        # JS block comments
    t = re.sub(r"(?m)^\s*(//|#).*$", " ", t)             # line comments
    toks = re.findall(r"\w[\w:.-]*|\S", t)
    # trailing commas and optional semicolons are layout, too
    return [x for x in toks if x not in (";",)]


def sim(a, b):
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    return round(sm.ratio(), 2)


def xq_params(lines, start):
    text = "\n".join(lines[start:start + 40])
    m = re.search(r"function\s+[\w-]+:[\w-]+\s*\(", text)
    i = m.end(); depth = 1; j = i
    while j < len(text) and depth:
        depth += {"(": 1, ")": -1}.get(text[j], 0); j += 1
    inner = re.sub(r"\(:.*?:\)", "", text[i:j - 1], flags=re.S)
    parts, depth, cur = [], 0, ""
    for ch in inner:
        if ch == "," and depth == 0:
            parts.append(cur); cur = ""; continue
        depth += {"(": 1, ")": -1}.get(ch, 0); cur += ch
    if cur.strip():
        parts.append(cur)
    return [p.strip() for p in parts if p.strip()]


def xq_type(param):
    m = re.search(r"\bas\s+(.+)$", param, re.S)
    if not m:
        return "item()"
    t = re.sub(r"\s+", "", m.group(1))
    t = re.sub(r"[*?+]$", "", t)
    t = re.sub(r"^(element|attribute|document-node|processing-instruction)\(.*\)$", r"\1()", t)
    t = re.sub(r"^map\(.*\)$", "map(*)", t)
    t = re.sub(r"^array\(.*\)$", "array(*)", t)
    t = re.sub(r"^function\(.*$", "function(*)", t)
    return t


def signature(name, lines, start, path):
    if path.endswith((".xqm", ".xq", ".xql")):
        return f"{name}({', '.join(xq_type(p) for p in xq_params(lines, start))})"
    return name


# ---------------------------------------------------------------- occurrences
def book_pages():
    for f in sorted(BOOK.glob("clsinfra-d7*/*.md")):
        text = f.read_text(encoding="utf8")
        yield f.parent.name, f.stem, text


def locate_lines(text):
    """For every line: (section label, paragraph label, footnote number)."""
    lines = text.split("\n")
    fm = re.search(r"^label:\s*(\S+)", text, re.M)
    sec, para, fn_ref, res = (fm.group(1) if fm else ""), None, {}, []
    for ln in lines:
        m = re.match(r"^\((\S+)\)=\s*$", ln)
        if m:
            lab = m.group(1)
            if re.search(r"-p\d+$", lab):
                para = lab
            elif not re.search(r"-note\d+$", lab):
                sec, para = lab, None
        if not ln.startswith("[^"):
            for r in re.findall(r"\[\^([\w-]+)\](?!:)", ln):
                fn_ref.setdefault(r, para or sec)
        res.append([sec, para or "", ""])
    cur_fn = None
    for i, ln in enumerate(lines):
        m = re.match(r"^\[\^([\w-]+)\]:", ln)
        if m:
            cur_fn = m.group(1)
        elif cur_fn and not (ln.startswith("    ") or not ln.strip()):
            cur_fn = None
        if cur_fn:
            res[i][2] = cur_fn
            res[i][1] = fn_ref.get(cur_fn, "")
    return lines, res


def link_text(line, url):
    for m in MDLINK.finditer(line):
        if m.group(2).replace("\\", "") == url:
            return m.group(1).replace("\\", "")
    return ""


# ---------------------------------------------------------------- tracing
cache = {}


def releases_containing(repo, commits):
    rels = []
    for c in commits:
        t = (git(repo, "describe", "--contains", c) or "").strip()
        t = re.sub(r"-(alpha|beta|rc)\.\d+$", "", re.sub(r"^v", "", re.split(r"[~^]", t)[0]))
        if t and t not in rels:
            rels.append(t)
    return sorted(rels, key=vkey)


def units_in(repo, tag, path_filter=None):
    out = []
    for f in (git(repo, "ls-tree", "-r", "--name-only", tag) or "").split():
        p = pats_for(f)
        if not p or "test" in f or "stories" in f or (path_filter and not path_filter(f)):
            continue
        src = git(repo, "show", f"{tag}:{f}")
        if src is None:
            continue
        nl = src.split("\n")
        out.extend((repo, tag, f, n, s, e, nl) for n, s, e in all_units(nl, p))
    return out


_units_cache = {}


def target_units(repo):
    if repo not in _units_cache:
        u = units_in(repo, TARGET[repo])
        if repo == "dracor-frontend":
            u += units_in(*REACT, path_filter=lambda f: f.startswith("src/"))
        _units_cache[repo] = u
    return _units_cache[repo]


def trace(url, report, repo, ref, path, a, b):
    key = (url, report)
    if key in cache:
        return cache[key]
    tag = TARGET[repo]
    pinned = bool(re.fullmatch(r"[0-9a-f]{7,40}", ref))
    resolved = ref
    if not pinned:
        for br in (f"gh/{ref}", f"origin/{ref}", ref):
            c = (git(repo, "rev-list", "-1", f"--before={REPORT_DATE[report]}T23:59:59", br) or "").strip()
            if c:
                resolved = c
                break
    r = {"repo": repo, "ref": ref, "pinned": pinned,
         "resolved_ref": "" if pinned else (resolved[:10] if resolved != ref else ""), "path": path,
         "line_from": a or "", "line_to": b or a or "", "kind": "", "unit": "", "signature_report": "",
         "target_release": f"{repo}@{tag}", "status": "", "match": "", "similarity": "", "target_unit": "",
         "target_url": "", "changed_in_releases": "", "change_commits": "", "main_differs": "", "action": ""}
    cache[key] = r
    ref = resolved
    old = git(repo, "show", f"{ref}:{path}")
    if old is None and git(repo, "cat-file", "-e", f"{ref}^{{tree}}") is None and not pinned:
        r["kind"] = "branch ref (gone)"; r["status"] = "unresolvable"; r["action"] = "check by hand"; return r
    if old is None:
        # a directory (tree link) or a missing file
        if git(repo, "cat-file", "-e", f"{ref}:{path}") is not None:
            r["kind"] = "directory"
            ok = git(repo, "cat-file", "-e", f"{tag}:{path}") is not None
            r["status"] = "directory exists" if ok else "directory removed"
            r["target_url"] = f"https://github.com/dracor-org/{repo}/tree/{tag}/{path}" if ok else ""
            r["action"] = "keep" if ok else "note"
        else:
            r["kind"] = "file not found at ref"; r["status"] = "unresolvable"; r["action"] = "check by hand"
        return r
    if not pinned:
        r["kind"] = "unpinned (branch)"
    pats = pats_for(path)
    if not a:
        r["kind"] = r["kind"] or "file"
        if git(repo, "cat-file", "-e", f"{tag}:{path}") is not None:
            r["status"] = "file exists"; r["match"] = "same path"
            r["target_url"] = f"https://github.com/dracor-org/{repo}/blob/{tag}/{path}"
            r["action"] = "keep"
            return r
        base = re.sub(r"\.(jsx?|tsx?|py|xqm)$", "", path.rsplit("/", 1)[-1])
        pairs = [(repo, tag)] + ([REACT] if repo == "dracor-frontend" else [])
        for rp, tg in pairs:
            hits = [f for f in (git(rp, "ls-tree", "-r", "--name-only", tg) or "").split()
                    if re.sub(r"\.(jsx?|tsx?|py|xqm)$", "", f.rsplit("/", 1)[-1]) == base
                    and "stories" not in f and "test" not in f]
            if hits:
                r["status"] = "file moved/renamed"; r["match"] = "same file stem"
                r["target_release"] = f"{rp}@{tg}"
                r["target_url"] = f"https://github.com/dracor-org/{rp}/blob/{tg}/{hits[0]}"
                r["action"] = "repoint"
                return r
        r["status"] = "file removed"; r["action"] = "note"
        return r
    a, b = int(a), int(b or a)
    ol = old.split("\n")
    name, st = find_unit(ol, a, b, pats) if pats else (None, None)
    if not name:
        r["kind"] = r["kind"] or "lines (no unit)"
        return window_match(r, repo, tag, path, ol[a - 1:b])
    r["kind"] = r["kind"] or "unit"
    r["unit"] = name
    en = unit_end(ol, st, pats)
    r["signature_report"] = signature(name, ol, st, path)
    body = norm(ol[st:en])

    # 1. same name (prefer same signature, then same path, then highest similarity)
    best = None
    for (rp, tg, f, n, s, e, nl) in target_units(repo):
        if n != name:
            continue
        sig = signature(n, nl, s, f)
        score = (sig == r["signature_report"], f == path, sim(body, norm(nl[s:e])))
        if best is None or score > best[0]:
            best = (score, rp, tg, f, n, s, e, nl, sig)
    if best:
        r["match"] = "same name" + ("" if best[0][0] else ", other signature")
    else:
        # 2. renamed? best body similarity among all units of the target (>= 0.5)
        for (rp, tg, f, n, s, e, nl) in target_units(repo):
            sc = sim(body, norm(nl[s:e]))
            if sc >= 0.5 and (best is None or sc > best[0][2]):
                best = ((False, f == path, sc), rp, tg, f, n, s, e, nl, signature(n, nl, s, f))
        if best:
            r["match"] = "renamed? (body similarity)"
    if not best:
        r["status"] = "gone"; r["action"] = "note"
        return r
    _, rp, tg, f2, n2, s2, e2, nl, sig2 = best
    nb = norm(nl[s2:e2])
    r["target_release"] = f"{rp}@{tg}"
    r["target_unit"] = sig2 if sig2 != r["signature_report"] else ""
    r["similarity"] = sim(body, nb)
    r["status"] = "unchanged" if body == nb else "changed"
    r["target_url"] = f"https://github.com/dracor-org/{rp}/blob/{tg}/{f2}#L{s2 + 1}-L{e2}"
    if rp == repo and r["status"] == "changed":
        log = git(repo, "log", "--format=@@%h %s", f"{ref}..{tg}", "-L", f"{s2 + 1},{e2}:{f2}") or ""
        cs = [l[2:] for l in log.splitlines() if l.startswith("@@") and not l.startswith("@@ ")]
        r["changed_in_releases"] = " ".join(releases_containing(repo, [c.split()[0] for c in cs if not FORMAT_ONLY.search(c)]))
        r["change_commits"] = " | ".join(cs)
    if repo == "dracor-api" and git(repo, "rev-parse", "-q", "--verify", API_MAIN):
        src = git(repo, "show", f"{API_MAIN}:{f2}")
        if src is None:
            r["main_differs"] = "file gone on main"
        else:
            ml = src.split("\n")
            mu = [(s, e) for n, s, e in all_units(ml, pats_for(f2)) if n == n2]
            r["main_differs"] = "unit gone on main" if not mu else (
                "" if norm(ml[mu[0][0]:mu[0][1]]) == nb else "yes")
    if r["status"] == "unchanged":
        r["action"] = "repoint (same code)"
    elif r["match"].startswith("renamed"):
        r["action"] = "repoint + note (renamed)"
    elif r["similarity"] >= 0.6:
        r["action"] = "repoint, check text"
    else:
        r["action"] = "note (rewritten)"
    return r


def window_match(r, repo, tag, path, block):
    """Referenced lines that are not inside a function (module prolog, variables,
    type declarations): best window of the same length in the target file."""
    stem = re.sub(r"\.(jsx?|tsx?)$", "", path)
    want = norm(block)
    best = None
    for f in dict.fromkeys([path] + [stem + e for e in (".js", ".jsx", ".ts", ".tsx")]):
        src = git(repo, "show", f"{tag}:{f}")
        if src is None:
            continue
        nl = src.split("\n")
        n = max(len(block), 1)
        for i in range(0, max(len(nl) - n + 1, 1)):
            for k in (n - 2, n, n + 2, n + 6):
                if k < 1:
                    continue
                sc = sim(want, norm(nl[i:i + k]))
                if best is None or sc > best[0]:
                    best = (sc, f, i, i + k)
    if not best or best[0] < 0.5:
        r["status"] = "gone"; r["action"] = "note"
        return r
    sc, f, i, j = best
    r["match"] = "line window"
    r["similarity"] = sc
    r["status"] = "unchanged" if sc == 1.0 else "changed"
    r["target_url"] = f"https://github.com/dracor-org/{repo}/blob/{tag}/{f}#L{i + 1}-L{j}"
    r["action"] = "repoint (same code)" if sc == 1.0 else ("repoint, check text" if sc >= 0.6 else "note (rewritten)")
    return r


# ---------------------------------------------------------------- API references
def load_spec(tag):
    src = git("dracor-api", "show", f"{tag}:api.yaml")
    spec = yaml.safe_load(src)
    ops = {}
    for p, item in spec.get("paths", {}).items():
        for meth, op in item.items():
            if isinstance(op, dict) and "operationId" in op:
                ops.setdefault(op["operationId"], []).append((meth.upper(), p))
    return spec, ops


def template_re(p):
    return re.compile("^" + re.sub(r"\\\{[^}]+\\\}", r"[^/]+", re.escape(p)) + "$")


def api_refs():
    tag = TARGET["dracor-api"]
    _, new_ops = load_spec(tag)
    new_paths = {p: oid for oid, l in new_ops.items() for m, p in l if m == "GET"} | \
                {p: oid for oid, l in new_ops.items() for m, p in l}
    old_ops = collections.OrderedDict()
    for t in OLD_SPECS:
        try:
            _, ops = load_spec(t)
        except Exception:
            continue
        for oid, l in ops.items():
            for m, p in l:
                old_ops.setdefault(p, (oid, t))
    # RESTXQ paths actually implemented in the target (some are not in api.yaml)
    rest_paths = set()
    for f in (git("dracor-api", "ls-tree", "-r", "--name-only", tag, "modules") or "").split():
        for m in re.finditer(r'%rest:path\("(?:/v1)?([^"]+)"\)', git("dracor-api", "show", f"{tag}:{f}") or ""):
            rest_paths.add(re.sub(r"\{\$", "{", m.group(1)))
    renamed_ops = {"get-cast": "get-characters", "get-cast-csv": "get-characters-csv",
                   "corpus-metadata-csv": "corpus-metadata-csv-endpoint"}

    def new_path_for(p):
        q = re.sub(r"/play/", "/plays/", p)
        q = re.sub(r"/cast(/|$)", r"/characters\1", q)
        q = q.replace("/metadata.csv", "/metadata/csv")
        for np in new_paths:
            if template_re(np).match(q):
                return np
        return None

    def resolve_path(p):
        """API-relative path (no /api, version prefix stripped) -> row fields."""
        p = re.sub(r"\{[?&][^}]*\}", "", p)        # URI template query parts
        p = p.split("?")[0].rstrip("/.,;:'`") or "/"
        old = next(((tp, *old_ops[tp]) for tp in old_ops if template_re(tp).match(p)), None)
        np = new_path_for(p)
        d = {"path": p, "old_template": old[0] if old else "", "old_operationId": old[1] if old else "",
             "old_spec": old[2] if old else "", "target_template": np or "",
             "target_operationId": new_paths.get(np, "") if np else ""}
        return d

    rows = []
    url_re = re.compile(r"https?://(?:www\.|staging\.|dev\.)?dracor\.org/(api|doc/api)([^\s)>\]\"'`]*)")
    code_re = re.compile(r"`(/(?:api/)?(?:v[01]/)?(?:corpora|info|id|character|characters|dts|wikidata)\b[^`\s]*)`")
    for report, page, text in book_pages():
        lines, loc = locate_lines(text)
        for i, ln in enumerate(lines):
            clean = ln.replace("\\", "").replace("**", "").replace("\u200b", "")
            found = []
            for m in url_re.finditer(clean):
                found.append(("url", m.group(0).rstrip(".,;:'"), m.group(1), m.group(2)))
            for m in code_re.finditer(clean):
                if "dracor.org" in clean[max(0, m.start() - 30):m.start()]:
                    continue
                found.append(("code path", m.group(1), "api", m.group(1)))
            for kind, raw, base, rest in dict.fromkeys(found):
                sec, para, fn = loc[i]
                row = {"report": report, "page": page, "section": sec, "paragraph": para, "footnote": fn,
                       "kind": kind, "reference": raw, "host": "", "api_version": "", "path": "",
                       "old_template": "", "old_operationId": "", "old_spec": "", "target_template": "",
                       "target_operationId": "", "status": "", "note": ""}
                hm = re.match(r"https?://([^/]+)", raw)
                row["host"] = hm.group(1) if hm else ""
                if base == "doc/api":
                    frag = rest.split("#", 1)[1] if "#" in rest else ""
                    om = re.match(r"/?\w+/([\w-]+)", frag)
                    if not om:
                        row.update(kind="api doc", status="page", note="Swagger UI → Scalar with front end 3; "
                                   "Swagger UI stays at swagger.dracor.org")
                    else:
                        oid = om.group(1)
                        row["kind"] = "swagger deep link"
                        row["old_operationId"] = oid
                        tgt = oid if oid in new_ops else renamed_ops.get(oid, "")
                        if tgt in new_ops:
                            row["target_operationId"] = tgt
                            row["target_template"] = new_ops[tgt][0][1]
                            row["status"] = "operation exists" if tgt == oid else "operation renamed"
                        else:
                            row["status"] = "operation removed"
                        row["note"] = ("deep link breaks with Scalar (front end 3); works on "
                                       f"https://swagger.dracor.org/#/public/{oid}")
                    rows.append(row); continue
                p = rest
                vm = re.match(r"(?:/api)?/(v\d+)(/.*|$)", p) if kind == "code path" else re.match(r"/(v\d+)(/.*|$)", p)
                if kind == "code path":
                    p = re.sub(r"^/api", "", p)
                    vm = re.match(r"/(v\d+)(/.*|$)", p)
                if vm:
                    row["api_version"] = vm.group(1); p = vm.group(2) or "/"
                else:
                    row["api_version"] = "unversioned" if kind == "url" else ""
                if kind == "code path":
                    p = p.replace("…", "").replace("...", "")
                row.update(resolve_path(p))
                if page == "6-2" and re.search(r"/poems|/ids$", row["path"]):
                    row["status"] = "PoeCor API (not DraCor)"
                elif not row["target_template"] and any(
                        template_re(rp).match(re.sub(r"/play/", "/plays/", row["path"])) for rp in rest_paths):
                    row["status"] = "served, not in api.yaml"
                elif not row["target_template"] and row["old_operationId"]:
                    row["status"] = "endpoint removed"
                elif not row["target_template"] and re.search(r"[…]|\.\.\.", raw):
                    row["status"] = "path pattern (elided)"
                elif not row["target_template"]:
                    row["status"] = "no match in target"
                elif row["api_version"] in ("v0", "unversioned"):
                    row["status"] = "legacy (v0 shutdown, #15)"
                elif row["path"] != row["target_template"] and not template_re(row["target_template"]).match(row["path"]):
                    row["status"] = "path changed"
                else:
                    row["status"] = "ok"
                if row["host"].startswith("staging") and "/dts" in row["path"]:
                    row["note"] = "staging DTS (D7.4 used DTS 1-alpha); DTS 1.0 in 1.5.0-rc.1"
                rows.append(row)
    return rows


# ---------------------------------------------------------------- main
def main():
    OUT.mkdir(exist_ok=True)
    rows = []
    for report, page, text in book_pages():
        lines, loc = locate_lines(text)
        for i, ln in enumerate(lines):
            clean = ln.replace("\\", "").replace("\u200b", "")
            seen = set()
            for m in LINK.finditer(clean):
                url = m.group(0)
                if url in seen:  # written-out URL: link text and target
                    continue
                seen.add(url)
                sec, para, fn = loc[i]
                t = dict(trace(url, report, *m.groups()))
                rows.append({"report": report, "page": page, "section": sec, "paragraph": para, "footnote": fn,
                             "link_text": link_text(clean, url), "url": url, **t})
    cols = list(rows[0].keys())
    with open(OUT / "code-links.csv", "w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, cols); w.writeheader(); w.writerows(rows)

    units = collections.OrderedDict()
    for r in rows:
        if not r["unit"]:
            continue
        key = (r["repo"], r["signature_report"])
        u = units.setdefault(key, {"repo": r["repo"], "unit": r["unit"], "signature_report": r["signature_report"],
                                   "report_refs": set(), "passages": [], "status": r["status"], "match": r["match"],
                                   "target_unit": r["target_unit"], "similarity": r["similarity"],
                                   "target_url": r["target_url"], "changed_in_releases": set(),
                                   "main_differs": r["main_differs"]})
        u["report_refs"].add(r["ref"][:7])
        u["passages"].append(f"{r['report']}:{r['paragraph'] or r['section']}" + (f" fn{r['footnote']}" if r["footnote"] else ""))
        u["changed_in_releases"].update(r["changed_in_releases"].split())
        if r["status"] == "changed":
            u["status"] = "changed"
    with open(OUT / "code-units.csv", "w", newline="", encoding="utf8") as fh:
        w = csv.writer(fh)
        w.writerow(["repo", "unit", "signature_report", "report_refs", "n_passages", "passages", "status", "match",
                    "target_unit", "similarity", "changed_in_releases", "main_differs", "target_url"])
        for u in units.values():
            w.writerow([u["repo"], u["unit"], u["signature_report"], " ".join(sorted(u["report_refs"])),
                        len(u["passages"]), " ; ".join(dict.fromkeys(u["passages"])), u["status"], u["match"],
                        u["target_unit"], u["similarity"], " ".join(sorted(u["changed_in_releases"], key=vkey)),
                        u["main_differs"], u["target_url"]])

    arows = api_refs()
    with open(OUT / "api-refs.csv", "w", newline="", encoding="utf8") as fh:
        w = csv.DictWriter(fh, list(arows[0].keys())); w.writeheader(); w.writerows(arows)

    C = collections.Counter
    summary = {
        "targets": {**TARGET, REACT[0]: REACT[1]},
        "api_main": (git("dracor-api", "log", "-1", "--format=%h %cs", API_MAIN) or "").strip(),
        "code_links": {"occurrences": len(rows), "unique": len({r["url"] for r in rows}),
                       "by_report_repo": {f"{k[0]} {k[1]}": v for k, v in C((r["report"], r["repo"]) for r in rows).items()},
                       "by_kind": dict(C(r["kind"] for r in rows)),
                       "by_status": dict(C(r["status"] for r in rows)),
                       "by_action": dict(C(r["action"] for r in rows))},
        "units": {"count": len(units),
                  "by_repo_status": {f"{k[0]} {k[1]}": v for k, v in C((u["repo"], u["status"]) for u in units.values()).items()},
                  "by_match": dict(C(u["match"] for u in units.values())),
                  "api_changed_per_release": dict(sorted(C(x for u in units.values() if u["repo"] == "dracor-api"
                                                           for x in u["changed_in_releases"]).items(), key=lambda kv: vkey(kv[0]))),
                  "api_main_differs": sum(1 for u in units.values() if u["main_differs"])},
        "api_refs": {"occurrences": len(arows), "by_kind": dict(C(r["kind"] for r in arows)),
                     "by_status": dict(C(r["status"] for r in arows))},
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


main()
