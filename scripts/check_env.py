#!/usr/bin/env python3
"""Environment check for the exam-paper-formater skill.

Detects which rendering pipeline is available and prints a JSON report:

  - xelatex      : primary LaTeX pipeline (ctexart / article -> PDF)
  - matplotlib   : diagram generation (scripts/diagram_tools.py)
  - cjk fonts    : CJK fonts found (LaTeX via ctex needs one; Windows
                   auto-selects SimSun/SimHei, Linux needs Noto CJK etc.)
  - pdf preview  : pypdfium2 (preferred) or pdftoppm, for visual verification
  - headless browser : Edge/Chromium, for the HTML fallback pipeline

Usage:
    python scripts/check_env.py            # print JSON report
    python scripts/check_env.py --no-browser-check   # skip browser probe

Exit code is always 0; the report's "pipeline" field says what to use:
"latex" or "html-fallback".
"""

import json
import os
import re
import shutil
import subprocess
import sys


def probe(cmd, timeout=30):
    """Return (ok, first_line_of_stdout) for a command, or (False, reason)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           encoding="utf-8", errors="replace")
        out = (r.stdout or "") + (r.stderr or "")
        first = next((l.strip() for l in out.splitlines() if l.strip()), "")
        return (r.returncode == 0, first or f"exit {r.returncode}")
    except FileNotFoundError:
        return False, "not found"
    except subprocess.TimeoutExpired:
        return False, "timeout"
    except Exception as e:  # noqa: BLE001
        return False, str(e)


def find_xelatex():
    exe = shutil.which("xelatex")
    if exe:
        ok, raw = probe([exe, "--version"])
        ver = next((l.strip() for l in raw.splitlines()
                    if re.search(r"XeTeX, Version|MiKTeX-XeTeX|TeX \(", l)),
                   raw)
        return {"available": ok, "path": exe, "version": ver}
    # Common non-PATH locations (MiKTeX portable, TeX Live custom dirs)
    candidates = []
    if os.name == "nt":
        candidates += [
            r"C:\MiKTeX\miktex\bin\x64\xelatex.exe",
            r"C:\Program Files\MiKTeX\miktex\bin\x64\xelatex.exe",
            r"E:\tools\miktex\texmfs\install\miktex\bin\x64\xelatex.exe",
            r"E:\tools\miktex\miktex\bin\x64\xelatex.exe",
            r"E:\tools\miktex\bin\x64\xelatex.exe",
        ]
    else:
        candidates += ["/usr/local/texlive/2024/bin/x86_64-linux/xelatex",
                       "/usr/local/texlive/2025/bin/x86_64-linux/xelatex"]
    for c in candidates:
        if os.path.exists(c):
            ok, raw = probe([c, "--version"])
            if ok:
                ver = next((l.strip() for l in raw.splitlines()
                            if re.search(r"XeTeX, Version|MiKTeX-XeTeX|TeX \(", l)),
                           raw)
                return {"available": True, "path": c, "version": ver,
                        "note": "not on PATH; use full path or add to PATH"}
    return {"available": False, "path": None, "version": None,
            "install_hint": "Windows no-admin: download the standalone setup "
                            "utility (miktex.org/download -> Command-line "
                            "installer, or CTAN systems/win32/miktex/setup/"
                            "windows-x64/setup-*.exe) then run: "
                            "miktexsetup_standalone --local-package-repository=D:\\miktex-pkgs "
                            "--package-set=basic download && "
                            "miktexsetup_standalone --quiet --local-package-repository=D:\\miktex-pkgs "
                            "--portable=D:\\miktex --package-set=basic --use-registry=no install; "
                            "add D:\\miktex\\texmfs\\install\\miktex\\bin\\x64 to PATH. "
                            "Admin: choco install miktex. "
                            "Linux: apt install texlive-xetex texlive-lang-chinese "
                            "texlive-latex-extra"}


def find_matplotlib():
    try:
        import matplotlib  # noqa: F401
        import matplotlib.font_manager as fm
        wanted = ("Noto Sans CJK", "Source Han", "WenQuanYi",
                  "Microsoft YaHei", "SimHei", "Noto Sans SC",
                  "SimSun", "KaiTi")
        cjk = sorted({f.name for f in fm.fontManager.ttflist
                      if any(w in f.name for w in wanted)})
        return {"available": True, "version": matplotlib.__version__,
                "cjk_fonts": cjk}
    except Exception as e:  # noqa: BLE001
        return {"available": False, "version": None, "cjk_fonts": [],
                "error": str(e),
                "install_hint": "pip install matplotlib"}


def find_pdf_preview():
    try:
        import pypdfium2  # noqa: F401
        return {"available": True, "backend": "pypdfium2"}
    except Exception:  # noqa: BLE001
        pass
    if shutil.which("pdftoppm"):
        return {"available": True, "backend": "pdftoppm"}
    return {"available": False,
            "install_hint": "pip install pypdfium2  (or apt/choco install poppler)"}


def find_headless_browser():
    names = ["msedge", "msedge.exe", "chrome", "google-chrome", "chromium",
             "chromium-browser", "headless_shell"]
    for n in names:
        p = shutil.which(n)
        if p:
            return {"available": True, "path": p}
    if os.name == "nt":
        for cand in (r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                     r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
                     r"C:\Program Files\Google\Chrome\Application\chrome.exe"):
            if os.path.exists(cand):
                return {"available": True, "path": cand}
    return {"available": False, "install_hint": "install Microsoft Edge or Chromium"}


def find_cjk_system_fonts():
    """Best-effort CJK font presence for the LaTeX pipeline (ctex)."""
    found = []
    if os.name == "nt":
        fonts = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
        if os.path.isdir(fonts):
            for fn in os.listdir(fonts):
                low = fn.lower()
                if any(k in low for k in ("simsun", "simhei", "msyh",
                                          "notosanssc", "notoserifsc",
                                          "sourcehan", "stkaiti")):
                    found.append(fn)
    else:
        r = subprocess.run(["fc-list", ":lang=zh", "family"],
                           capture_output=True, text=True, timeout=20)
        if r.returncode == 0:
            found = sorted({l.split(":")[0].strip()
                            for l in r.stdout.splitlines() if l.strip()})[:10]
    return {"available": len(found) > 0, "fonts": found[:12]}


def main():
    report = {
        "python": sys.version.split()[0],
        "platform": sys.platform,
        "xelatex": find_xelatex(),
        "matplotlib": find_matplotlib(),
        "cjk_system_fonts": find_cjk_system_fonts(),
        "pdf_preview": find_pdf_preview(),
        "headless_browser": find_headless_browser(),
    }
    report["pipeline"] = "latex" if report["xelatex"]["available"] else "html-fallback"
    missing = []
    if not report["xelatex"]["available"]:
        missing.append("xelatex")
    if not report["matplotlib"]["available"]:
        missing.append("matplotlib (diagrams)")
    if not report["cjk_system_fonts"]["available"] and sys.platform != "win32":
        missing.append("CJK system font")
    report["missing"] = missing
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
