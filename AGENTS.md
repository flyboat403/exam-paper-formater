# AGENTS.md

## What this repo is

- This is an agent **skill**, not an app or library. The repo root **is** the skill root
  (scripts resolve relative to it; do not move `SKILL.md` into a subdirectory).
- `SKILL.md` is the source of truth: YAML frontmatter (trigger description), 10-step
  workflow, and numbered quality red lines. Read it before changing behavior.
- `README.md` is the user-facing overview and upstream MIT attribution. Preserve the
  attribution section when editing it.
- No package manifest, build system, linter, or test runner. Scripts are plain
  Python 3.8+ (stdlib; `matplotlib` / `pypdfium2` / `pymupdf` optional).
- Docs and reference prose are Chinese; match that in user-facing docs. Script
  docstrings/CLI help are English.

## Commands

```bash
python3 scripts/check_env.py [--no-browser-check]   # JSON report; read the "pipeline" field
python3 scripts/tex_check.py <file.tex> --paper WxH --cols {1,2,3} --seal {on,off} --lang {zh,en}
python3 scripts/draw_seal.py <exam.pdf> -o <sealed.pdf> --paper WxH --lang {zh,en}
xelatex -interaction=nonstopmode <file.tex>          # run twice (refs + column balancing)
```

- `check_env.py` always exits 0; decide `latex` vs `html-fallback` from `"pipeline"`.
- `tex_check.py` exits 1 on any ERROR, 0 otherwise, 2 on bad args/missing file.
- Always pass the parameters the user actually chose. `--paper` is `WxH` in mm and
  validates orientation: landscape means the **long** side first (A3 landscape = `420x297`).
- `tex_check.py` only checks `.tex`. For the HTML fallback, use the manual checklist in
  `references/html-fallback.md` §3.
- Windows: set `PYTHONIOENCODING=utf-8` before Python scripts and redirect xelatex stdin
  (`< NUL`), otherwise Chinese output garbles and MiKTeX hangs on prompts.

## Workflow constraints that are easy to violate

- `references/` files are loaded **conditionally** (see `SKILL.md` step 5).
  `references/intake.md` and `references/latex-templates.md` must be read in full
  (no limit, no skimming) before collecting parameters / writing `.tex`.
  Do **not** preload unrelated reference files; the skill explicitly forbids it to
  avoid diluting the critical instructions.
- Layout is contract: paper size, orientation, column count, seal line, and language in
  the generated file must match the user's confirmed choices exactly.
- In the HTML fallback the header (`h1` / `.sub` / `<hr>`) and the score table belong
  **inside** `<div class="cols">` (left column of a 2/3-column paper), matching
  `latex-templates.md`. Putting them outside makes the title centre on the gutter.
  The score table uses `width:100%`, never a fixed cm width.
- HTML fallback seal is **post-processed**, not CSS: print the HTML without seal markup,
  then run `draw_seal.py`. It draws the whole seal on page 1 only by default; `--repeat`
  keeps line/circles/prompt on later pages (personal info always page 1).
  CSS `top:20%` is document-relative and Chromium cannot page-scope it.
- `scripts/diagram_tools.py` provides 12 matplotlib diagram helpers (PNG, 150 DPI).
  Import it via `sys.path.insert(0, "<skill-root>/scripts")`.
- `scripts/draw_seal.py` overlays the HTML-fallback seal with PyMuPDF. Verify with
  `page.get_text("blocks")`: by default page 1 has 2 left-side blocks (prompt + info)
  and later pages have 0. With `--repeat`, later pages have the prompt only.
  It embeds + subsets the seal font (a non-embedded CJK font prints as boxes on some
  RIPs) and runs a pre-flight check: text inside the 22mm band, `/Rotate` pages,
  mixed page sizes, or an already-sealed PDF exit 3 unless `--force` is passed.
- Generated `.tex`, images, and PDFs belong in the current project's `output/`
  directory. Use the Chinese filenames the examples use.

## Evals / verification

- There is no test runner. `evals/evals.json` contains 5 prompt + assertion cases;
  `input_file` paths are relative to `evals/` (e.g. `inputs/eval1_数学期中卷.md`).
  Execute the skill flow manually and check both the prose assertions and the
  `params` passed to `tex_check.py`.
- Before committing script changes, run `check_env.py` and run `tex_check.py` against a
  sample `.tex` with real layout flags; nothing else exercises these paths.

## Do not commit

- `output/`, `*/output/`, `冒烟测试/`, `.dsh-paste/`, and LaTeX aux files are gitignored.
  Typeset artifacts are disposable; never treat them as source.
