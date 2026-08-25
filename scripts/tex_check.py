#!/usr/bin/env python3
"""Quality checker for exam-paper-formater generated .tex files.

Adapted from the markdown quality checker of
haitanghuaweimianTom/exam-paper-skill (MIT), extended with the
layout-parameter checks of elangan1997-cmyk/exam-prompt-skill's
self-check list (paper size, column count, seal line, figure completeness).

Usage:
    python scripts/tex_check.py exam.tex \
        [--paper 420x297]   # expected paperwidth x paperheight in mm
        [--cols 3]          # expected body columns (1 = no multicols body)
        [--seal on|off]     # expected seal-line (密封线) presence
        [--lang zh|en]      # expected language mode (zh -> ctex, en -> article)

Exit code: 1 if any ERROR-level issue, 0 otherwise.
"""

import argparse
import os
import re
import sys


FIG_KEYWORDS_ZH = [
    "如图", "如下图", "见右图", "见下图", "见图", "如图所示",
    "函数图像", "函数图象", "统计图", "装置图", "电路图", "光路图",
    "示意图", "受力图", "三视图",
]
FIG_KEYWORDS_EN = [
    "as shown in the figure", "as shown in fig", "shown below",
    "in the figure", "figure below", "fig. ",
]
FIG_RE = re.compile(r"\\(?:tikzpicture|begin\{tikzpicture\}|includegraphics)")

CTRL_CHARS = {
    "\x07": "BEL (corrupted \\alpha-family command, e.g. \\a)",
    "\x08": "BS (corrupted \\beta-family command, e.g. \\b)",
    "\x0b": "VT (corrupted \\varepsilon-family command, e.g. \\v)",
    "\x0c": "FF (corrupted \\forall/\\frac-family command, e.g. \\f)",
}

UNICODE_LOGIC = {
    "\u2227": "\\land", "\u2228": "\\lor", "\u00AC": "\\neg",
    "\u2192": "\\rightarrow", "\u2194": "\\leftrightarrow",
    "\u2200": "\\forall", "\u2203": "\\exists",
}

SUBSUP_RE = re.compile(r"[\u00B2\u00B3\u00B9\u2070-\u209F]")


class TexChecker:
    def __init__(self, content, paper=None, cols=None, seal=None, lang=None,
                 base_dir="."):
        self.raw_lines = content.splitlines()
        self.content = content
        self.base_dir = base_dir
        self.paper = paper
        self.cols = cols
        self.seal = seal
        self.lang = lang
        self.issues = []
        # Comment-stripped lines (same count as raw_lines)
        self.lines = [self._strip_comment(l) for l in self.raw_lines]
        self.code_text = "\n".join(self.lines)

    # ---------- helpers ----------

    def add(self, line_no, severity, message):
        self.issues.append((line_no, severity, message))

    @staticmethod
    def _strip_comment(line):
        """Remove a % comment (unescaped, outside math) from a line."""
        in_math = False
        i = 0
        while i < len(line):
            ch = line[i]
            if ch == "\\" and i + 1 < len(line):
                i += 2
                continue
            if ch == "$":
                in_math = not in_math
            elif ch == "%" and not in_math:
                return line[:i]
            i += 1
        return line

    def _find_line(self, snippet):
        for i, line in enumerate(self.raw_lines, start=1):
            if snippet in line:
                return i
        return 0

    # ---------- checks ----------

    def check_documentclass(self):
        m = re.search(r"\\documentclass(?:\[[^\]]*\])?\{([^}]+)\}", self.code_text)
        if not m:
            self.add(1, "ERROR", "\\documentclass not found")
            return
        cls = m.group(1).strip()
        line = self._find_line(m.group(0))
        if self.lang == "en" and "ctex" in cls:
            self.add(line, "ERROR",
                     f"English paper must use article class, found \\documentclass{{{cls}}}")
        if self.lang == "zh" and not ("ctex" in cls or "xeCJK" in self.code_text
                                      or "CJK" in cls):
            self.add(line, "ERROR",
                     f"Chinese paper needs ctex class or xeCJK, found \\documentclass{{{cls}}}")

    def check_paper(self):
        if not self.paper:
            return
        m = re.search(r"\\usepackage\s*\[([^\]]*)\]\s*\{\s*geometry\s*\}", self.code_text)
        if not m:
            self.add(0, "ERROR", "\\usepackage[...]{geometry} not found")
            return
        opts = m.group(1)
        pw = re.search(r"paperwidth\s*=\s*([\d.]+)\s*(mm|cm)", opts)
        ph = re.search(r"paperheight\s*=\s*([\d.]+)\s*(mm|cm)", opts)
        line = self._find_line("geometry")
        if not pw or not ph:
            self.add(line, "ERROR",
                     "geometry must set paperwidth and paperheight explicitly, e.g. "
                     "paperwidth=420mm,paperheight=297mm")
            return
        val = lambda mm_unit: float(mm_unit[0]) * (10 if mm_unit[1] == "cm" else 1)
        got = (round(val(pw.groups())), round(val(ph.groups())))
        want = tuple(self.paper)
        if got != want:
            self.add(line, "ERROR",
                     f"paper size is {got[0]}x{got[1]}mm, expected {want[0]}x{want[1]}mm "
                     "(check orientation!)")

    def check_columns(self):
        if self.cols is None:
            return
        # body multicols = the first multicols that begins before the first \section
        body_start = self.code_text.find("\\begin{document}")
        if body_start < 0:
            body_start = 0
        section_pos = self.code_text.find("\\section", body_start)
        first_multicols = re.search(r"\\begin\{multicols\}\{(\d+)\}",
                                    self.code_text[body_start:])
        body_multicols = None
        if first_multicols and (section_pos < 0
                                or body_start + first_multicols.start() < section_pos):
            body_multicols = int(first_multicols.group(1))
        if self.cols == 1:
            if body_multicols is not None:
                self.add(self._line_at(body_start + first_multicols.start()),
                         "ERROR",
                         "1-column paper must not wrap the body in multicols")
        else:
            if body_multicols is None:
                self.add(self._line_at(body_start), "ERROR",
                         f"{self.cols}-column paper needs a body-wide "
                         f"\\begin{{multicols}}{{{self.cols}}} before the first section")
            elif body_multicols != self.cols:
                self.add(self._line_at(body_start + first_multicols.start()), "ERROR",
                         f"body is multicols{{{body_multicols}}}, expected multicols{{{self.cols}}}")

    def _line_at(self, pos):
        return self.code_text[:pos].count("\n") + 1

    def check_seal_line(self):
        if self.seal is None:
            return
        has_zh = "密封线" in self.code_text
        has_en = bool(re.search(r"seal line", self.code_text, re.I))
        has = has_zh or has_en
        if self.seal == "on" and not has:
            self.add(0, "ERROR", "seal line (密封线 / seal line) expected but not found")
        if self.seal == "off" and has:
            self.add(self._find_line("密封线" if has_zh else "seal line"),
                     "ERROR", "seal line should be off for this paper")

    def check_environments(self):
        begins = re.findall(r"\\begin\{([a-zA-Z*]+)\}", self.code_text)
        ends = re.findall(r"\\end\{([a-zA-Z*]+)\}", self.code_text)
        for env in sorted(set(begins)):
            b, e = begins.count(env), ends.count(env)
            if b != e:
                self.add(self._find_line(f"\\begin{{{env}}}"), "ERROR",
                         f"unbalanced environment {env}: {b} \\begin vs {e} \\end")

    def check_math_balance(self):
        without_display = re.sub(r"\$\$.*?\$\$", "", self.code_text, flags=re.DOTALL)
        n = without_display.count("$")
        if n % 2 != 0:
            self.add(self._find_line("$"), "ERROR",
                     f"unclosed inline math: {n} $ delimiters (odd)")

    def check_packages(self):
        if "tikzpicture" in self.code_text and "\\usepackage{tikz}" not in self.code_text:
            self.add(self._find_line("tikzpicture"), "ERROR",
                     "tikzpicture used but \\usepackage{tikz} missing")
        if "multicols" in self.code_text and "\\usepackage{multicol}" not in self.code_text:
            self.add(self._find_line("multicols"), "ERROR",
                     "multicols used but \\usepackage{multicol} missing")

    def check_control_chars(self):
        for idx, line in enumerate(self.lines, start=1):
            for ch, desc in CTRL_CHARS.items():
                if ch in line:
                    self.add(idx, "ERROR", f"control character {desc} in file")
            if "\t" in line:
                self.add(idx, "WARNING",
                         "tab character found (possible corrupted \\theta/\\times); "
                         "use raw strings when generating .tex from Python")

    def check_unicode(self):
        for idx, line in enumerate(self.lines, start=1):
            if SUBSUP_RE.search(line):
                self.add(idx, "WARNING",
                         "Unicode subscript/superscript found; use LaTeX $_n$ / $^n$ "
                         "(e.g. H$_2$O)")
            for sym, repl in UNICODE_LOGIC.items():
                if sym in line:
                    self.add(idx, "WARNING",
                             f"Unicode symbol '{sym}' found; use `{repl}`")

    def check_straight_quotes(self):
        if self.lang == "en":
            return

        def is_cjk(ch):
            return "\u4e00" <= ch <= "\u9fff"

        for idx, line in enumerate(self.lines, start=1):
            if "$" in line:
                continue
            for j, ch in enumerate(line):
                if ch in "\"'":
                    prev_cjk = j > 0 and is_cjk(line[j - 1])
                    next_cjk = j < len(line) - 1 and is_cjk(line[j + 1])
                    if prev_cjk or next_cjk:
                        self.add(idx, "WARNING",
                                 "straight quote adjacent to Chinese text; use “”")
                        break

    def check_chinese_in_math(self):
        if self.lang == "en":
            return
        parts = re.split(r"(?<!\$)\$(?!\$)", self.code_text)
        seen = set()
        for idx in range(1, len(parts), 2):
            math_part = parts[idx]
            cleaned = re.sub(r"\\text\{[^}]*\}", "", math_part)
            for ch in cleaned:
                if "\u4e00" <= ch <= "\u9fff":
                    marker = "$" + math_part[:40] + "$"
                    ln = self._find_line(math_part[:40])
                    if ln not in seen:
                        seen.add(ln)
                        self.add(ln, "ERROR",
                                 f"Chinese character '{ch}' inside math mode; "
                                 "wrap with \\text{...}")
                    break

    def check_figure_completeness(self):
        """Every question that mentions a figure must be followed by one.

        Quoted spans (“…”/“...”/「…」) are stripped before matching: a
        figure keyword inside quotes is a quoted name (e.g. the chart
        title a student sets — “某高校师资情况统计图”), not a reference
        to a figure that belongs in the paper.
        """
        keywords = FIG_KEYWORDS_EN if self.lang == "en" else FIG_KEYWORDS_ZH
        lines = self.lines
        n = len(lines)
        for i, line in enumerate(lines):
            unquoted = re.sub(r"“[^”]*”|\"[^\"]*\"|「[^」]*」", "", line)
            hit = next((k for k in keywords if k.lower() in unquoted.lower()), None)
            if not hit:
                continue
            # Creation instructions (绘制/生成/画出… + 图名词) need no embedded
            # figure — the student produces it (e.g. an on-computer task
            # “根据数据绘制统计图”) — unless the line also references an
            # existing figure (如图/下图/图1 …), which must still exist.
            if self.lang != "en" and re.search(
                    r"绘制|生成|画出|画一|作出|描出|制作|补全|补出", unquoted) \
                    and not re.search(
                        r"如图|如下图|下图|上图|图中|图\s*\d|图\s*[一二三四五六七八九十]",
                        unquoted):
                continue
            # search for a figure from this line to the next \item / \section
            j = i
            found = False
            while j < n:
                l = lines[j]
                if FIG_RE.search(l):
                    found = True
                    break
                if j > i and re.search(r"\\(item|section|end\{enumerate\}|end\{multicols\})", l):
                    break
                j += 1
            if not found:
                self.add(i + 1, "ERROR",
                         f"question mentions a figure ('{hit}') but no "
                         "tikzpicture/includegraphics follows before the next question")

    def check_orphan_figures(self):
        """Figures not referenced by any nearby question text -> warning.

        Preamble TikZ (e.g. the seal-line shipout/background hook) is never
        counted; the search window is +/-40 lines because figure code often
        sits a few paragraphs after the question that references it.
        """
        # apparatus/experiment context also counts as a reference: 实验题
        # 装置图 often has no explicit "如图" in the question stem.
        keywords = FIG_KEYWORDS_ZH + FIG_KEYWORDS_EN + [
            "图", "实验", "装置", "测量", "连接",
        ]
        body_start = self.code_text.find("\\begin{document}")
        if body_start < 0:
            body_start = 0
        for m in re.finditer(r"\\begin\{tikzpicture\}", self.code_text[body_start:]):
            ln = self._line_at(body_start + m.start())
            lo, hi = max(0, ln - 40), min(len(self.raw_lines), ln + 40)
            window = "\n".join(self.raw_lines[lo:hi])
            if not any(k.lower() in window.lower() for k in keywords):
                self.add(ln, "WARNING",
                         "TikZ figure not referenced by nearby question text "
                         "(orphan figure?)")

    def check_included_images(self):
        for m in re.finditer(r"\\includegraphics\s*(?:\[[^\]]*\])?\{([^}]+)\}",
                             self.code_text):
            path = m.group(1)
            full = os.path.normpath(os.path.join(self.base_dir, path))
            if not os.path.exists(full):
                self.add(self._line_at(m.start()), "ERROR",
                         f"\\includegraphics target not found: {path}")

    def check_score_table(self):
        """Score-table columns must cover every 大题 in the body (red line 5).

        Only fires when a recognizable score-table header row exists
        (题号+总分 / Part+Total); a paper without such a table is left alone.
        """
        body_start = self.code_text.find("\\begin{document}")
        if body_start < 0:
            return
        body = self.code_text[body_start:]
        # 大题 = \section*（单级卷）或 \subsection*（两级「部分/大题」卷，
        # 部分行用 \section* 且以「第」开头，不会被误计）。
        sections = re.findall(
            r"^\s*\\(?:section|subsection)\*?\{\s*[一二三四五六七八九十\d]{1,3}\s*[、\.．]",
            body, re.M)
        if not sections:
            return
        header = None
        for i, line in enumerate(self.lines):
            if "题号" in line and "总分" in line and "&" in line:
                header = i
                break
            low = line.lower()
            if "total" in low and re.search(r"\b(part|section)\b", low) \
                    and "&" in line:
                header = i
                break
        if header is None:
            return
        cols = self.lines[header].count("&") + 1
        if cols - 2 < len(sections):
            self.add(header + 1, "ERROR",
                     f"score table has {cols - 2} question-type column(s) "
                     f"but the body has {len(sections)} 大题 — "
                     "a question type is missing from the score table")

    def _balanced(self, i):
        """i points at '{'; return (content, pos_after_closing_brace)."""
        depth = 0
        j = i
        n = len(self.code_text)
        while j < n:
            ch = self.code_text[j]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return self.code_text[i + 1:j], j + 1
            j += 1
        return None, i

    def check_table_width(self):
        """tabular 固定 cm/mm/pt 列宽总和不得超栏宽（red line 13）。

        实测教训：11 列固定 m{} 宽得分表（22.4cm）超 A3 横 2 栏栏宽
        （183mm）89mm，溢出被画到栏沟与邻栏、与邻栏题干文字交错。
        比例列宽（\\linewidth / \\dimexpr）自动适配，不检查。
        仅在同时给出 --paper 与 --cols 时启用。
        """
        if not self.paper or self.cols is None:
            return
        left = 32.0 if self.seal == "on" else 18.0
        right = 12.0
        sep = {1: 0.0, 2: 10.0, 3: 8.0}[self.cols]
        col_w = (self.paper[0] - left - right - (self.cols - 1) * sep) / self.cols
        scale = {"mm": 1.0, "cm": 10.0, "pt": 25.4 / 72.0}
        for m in re.finditer(r"\\begin\{tabular\*?\}", self.code_text):
            name = m.group(0)
            pos = m.end()
            n = len(self.code_text)
            while pos < n and self.code_text[pos] in " \t\n":
                pos += 1
            if pos < n and self.code_text[pos] == "[":
                pos = self.code_text.find("]", pos) + 1
                while pos < n and self.code_text[pos] in " \t\n":
                    pos += 1
            if pos >= n or self.code_text[pos] != "{":
                continue
            g1, pos2 = self._balanced(pos)
            spec = g1
            if name.endswith("*}"):  # tabular*: first group is width, second is spec
                while pos2 < n and self.code_text[pos2] in " \t\n":
                    pos2 += 1
                if pos2 < n and self.code_text[pos2] == "{":
                    spec, _ = self._balanced(pos2)
            if not spec:
                continue
            total_mm = 0.0
            has_fixed = False
            for dm in re.finditer(r"(?<![A-Za-z])[mp]\{([^{}]+)\}", spec):
                mm = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(mm|cm|pt)",
                                  dm.group(1).strip())
                if mm:
                    has_fixed = True
                    total_mm += float(mm.group(1)) * scale[mm.group(2)]
            if has_fixed and total_mm > col_w - 1.0:
                line = self._line_at(m.start())
                self.add(line, "ERROR",
                         f"tabular fixed column widths sum {total_mm:.0f}mm "
                         f"exceeds column width {col_w:.0f}mm — overflow is "
                         "drawn over the gutter into the adjacent column in "
                         "multi-column papers (red line 13); use "
                         "\\linewidth-proportional column widths "
                         "(latex-templates.md §1)")

    def run_all(self):
        self.check_documentclass()
        self.check_paper()
        self.check_columns()
        self.check_seal_line()
        self.check_environments()
        self.check_math_balance()
        self.check_packages()
        self.check_control_chars()
        self.check_unicode()
        self.check_straight_quotes()
        self.check_chinese_in_math()
        self.check_figure_completeness()
        self.check_orphan_figures()
        self.check_included_images()
        self.check_score_table()
        self.check_table_width()
        return self.issues

    def report(self):
        if not self.issues:
            print("tex_check: no issues found.")
            return 0
        errors = [x for x in self.issues if x[1] == "ERROR"]
        warnings = [x for x in self.issues if x[1] == "WARNING"]
        for line_no, severity, message in sorted(self.issues, key=lambda x: (x[0], x[1])):
            print(f"Line {line_no:4d} [{severity:7s}] {message}")
        print(f"\nTotal: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1 if errors else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("input", help="path to .tex file")
    ap.add_argument("--paper", help="expected paper as WxH in mm, e.g. 420x297")
    ap.add_argument("--cols", type=int, choices=[1, 2, 3],
                    help="expected body column count")
    ap.add_argument("--seal", choices=["on", "off"], help="expected seal-line setting")
    ap.add_argument("--lang", choices=["zh", "en"], help="expected language mode")
    args = ap.parse_args()

    if not os.path.exists(args.input):
        print(f"file not found: {args.input}", file=sys.stderr)
        return 2

    paper = None
    if args.paper:
        m = re.match(r"^\s*(\d+)\s*[xX×]\s*(\d+)\s*$", args.paper)
        if not m:
            print(f"bad --paper value: {args.paper} (want WxH, e.g. 420x297)",
                  file=sys.stderr)
            return 2
        paper = (int(m.group(1)), int(m.group(2)))

    with open(args.input, encoding="utf-8") as f:
        content = f.read()

    checker = TexChecker(content, paper=paper, cols=args.cols, seal=args.seal,
                         lang=args.lang, base_dir=os.path.dirname(os.path.abspath(args.input)))
    checker.run_all()
    return checker.report()


if __name__ == "__main__":
    sys.exit(main())
