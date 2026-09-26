"""Small wikitext helpers: strip references and notes, flatten links and templates, split tables and templates."""
import re

MONTHS = ["January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


def balanced(s, i):
    """Return the end index of the {{...}} template that starts at s[i]."""
    depth, j = 0, i
    while j < len(s):
        if s.startswith("{{", j):
            depth += 1
            j += 2
        elif s.startswith("}}", j):
            depth -= 1
            j += 2
            if depth == 0:
                return j
        else:
            j += 1
    return j


def strip_templates(s, names):
    """Remove {{name ...}} templates, nested braces allowed, for the given lowercase names."""
    out, i, low = [], 0, s.lower()
    while i < len(s):
        if s.startswith("{{", i) and any(
                low.startswith("{{" + n, i) and low[i + 2 + len(n):i + 3 + len(n)] in ("|", "}", " ", "\n", "")
                for n in names):
            i = balanced(s, i)
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def strip_refs(s):
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<ref[^>/]*/>", "", s)
    return re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)


def clean(s):
    """Plain text of a wikitext fragment."""
    s = strip_refs(s)
    s = strip_templates(s, ["efn", "sfn", "dagger", "hash-tag", "‡", "anchor", "refn", "cn", "citation needed"])
    s = re.sub(r"\{\{sort\|[^|{}]*\|([^{}]*)\}\}", r"\1", s, flags=re.I)
    s = re.sub(r"\{\{(?:small|nowrap|abbr)\|([^|{}]*)(?:\|[^{}]*)?\}\}", r"\1", s, flags=re.I)
    s = re.sub(r"\{\{N/A\|([^{}]*)\}\}", r"\1", s, flags=re.I)
    s = re.sub(r"\{\{arr\.?\}\}", "arr.", s, flags=re.I)
    s = re.sub(r"<br\s*/?>", "; ", s)
    s = re.sub(r"</?(small|span|sup|i|b)[^>]*>", "", s)
    s = re.sub(r"\[\[(?:[^|\]]*\|)?([^\]]*)\]\]", r"\1", s)
    s = s.replace("'''", "").replace("''", "").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", s).strip(" ;")


def links(s):
    """Link targets in order, without anchors, first letter upper case, underscores as spaces."""
    out = []
    for m in re.finditer(r"\[\[([^\]|#]*)", s):
        t = m.group(1).replace("_", " ").strip()
        if t:
            out.append(t[0].upper() + t[1:])
    return out


def cell_text(line):
    """Split a table cell line into its attribute part and its content."""
    body, depth = line[1:], 0
    for k, ch in enumerate(body):
        two = body[k:k + 2]
        if two in ("[[", "{{"):
            depth += 1
        elif two in ("]]", "}}"):
            depth -= 1
        elif ch == "|" and depth == 0 and two != "||":
            head = body[:k]
            if "=" in head and "[[" not in head and "{{" not in head:
                return head, body[k + 1:]
            break
    return "", body


def table_rows(tab):
    """Yield each row of a wikitext table as a list of cell lines (continuation lines joined)."""
    tab = tab[tab.index("\n|-"):]
    end = re.search(r"^\|\}", tab, flags=re.M)
    tab = tab[:end.start()] if end else tab
    for part in re.split(r"\n\|-[^\n]*", tab):
        cells, cur = [], None
        for line in part.split("\n"):
            if line.startswith(("|", "!")) and not line.startswith(("|}", "|+")):
                if cur is not None:
                    cells.append(cur)
                cur = line
            elif cur is not None:
                cur += "\n" + line
        if cur is not None:
            cells.append(cur)
        if cells:
            yield cells


def infobox_field(text, name):
    m = re.search(r"^\|\s*" + name + r"\s*=(.*?)(?=^\|\s*\w+\s*=|^\}\})", text, flags=re.M | re.S)
    return m.group(1) if m else ""


def dates(s):
    """Every full date in a fragment, as YYYY-MM-DD, from start-date templates and written dates."""
    s = strip_refs(s)
    out = []
    for m in re.finditer(r"\{\{\s*start ?date\s*((?:\|[^|{}]*)*)\}\}", s, flags=re.I):
        nums = [p.strip() for p in m.group(1).split("|") if p.strip() and "=" not in p]
        if len(nums) >= 3 and all(n.isdigit() for n in nums[:3]):
            out.append(f"{int(nums[0]):04d}-{int(nums[1]):02d}-{int(nums[2]):02d}")
    mon = "|".join(MONTHS)
    for m in re.finditer(r"\b(\d{1,2}) (" + mon + r"),? (\d{4})\b", s):
        out.append(f"{m.group(3)}-{MONTHS.index(m.group(2)) + 1:02d}-{int(m.group(1)):02d}")
    for m in re.finditer(r"\b(" + mon + r") (\d{1,2}),? (\d{4})\b", s):
        out.append(f"{m.group(3)}-{MONTHS.index(m.group(1)) + 1:02d}-{int(m.group(2)):02d}")
    return out
