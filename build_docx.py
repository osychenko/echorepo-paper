#!/usr/bin/env python3
"""Create the Word review copy from main.tex, with TikZ diagrams and references.

This version handles both the original manuscript and the Direction A revision,
including its extra methodological-requirements table and changed QA table.
No change to the Makefile or Dockerfile is required.
"""
from __future__ import annotations
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEX = ROOT / "main.tex"
BIB = ROOT / "echorepo_integrated.bib"
OUT = ROOT / "paperA_review.docx"


def call(command, *, cwd=None):
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, text=True)
    if result.returncode:
        raise RuntimeError("Command failed: " + " ".join(command) +
                           "\n" + result.stdout[-6000:])
    if command[0] == "pandoc" and result.stdout.strip():
        print(result.stdout.strip())


def prepare_tables(source: str) -> str:
    """Convert the four known tabularx layouts into Pandoc-friendly longtables.

    Fail explicitly if a new layout is added instead of silently dropping it.
    Preserve captions, labels, and LaTeX table content.
    """
    layouts = {
        # Original canonical resources table.
        r"\begin{tabularx}{\linewidth}{@{}p{4.7cm}X@{}}":
            r"\begin{longtable}{p{4.7cm}p{8.3cm}}",
        # Original coverage table.
        r"\begin{tabularx}{\linewidth}{@{}Xrr@{}}":
            r"\begin{longtable}{p{9.0cm}rr}",
        # New Direction A methodological-requirements table.
        r"\begin{tabularx}{\linewidth}{@{}p{2.5cm}p{4.0cm}X@{}}":
            r"\begin{longtable}{p{2.5cm}p{4.0cm}p{6.5cm}}",
        # New Direction A QA table.
        r"\begin{tabularx}{\linewidth}{@{}Xr@{}}":
            r"\begin{longtable}{p{11.0cm}r}",
    }
    original_count = source.count(r"\begin{tabularx}")
    for old, new in layouts.items():
        source = source.replace(old, new)
    if r"\begin{tabularx}" in source:
        raise SystemExit("Unrecognized tabularx column layout. "
                         "Add its conversion to prepare_tables() in build_docx.py")

    source = source.replace(r"\end{tabularx}", r"\end{longtable}")
    converted = source.count(r"\begin{longtable}")
    if converted != original_count:
        raise SystemExit(f"Found {original_count} tabularx tables, "
                         f"but converted {converted}")

    # Move float captions and labels inside the longtable environment.
    # Pandoc does not preserve captions reliably when a longtable remains
    # wrapped inside a LaTeX table float.
    float_start = re.compile(
        r"\\begin\{table\}\[htbp\]\s*"
        r"\\centering\s*\\small\s*"
        r"\\caption\{([^\n]*)\}\s*"
        r"\\label\{([^}]+)\}\s*"
        r"(\\begin\{longtable\}\{[^\n]*\})"
    )

    def place_caption(match):
        return (match.group(3) + "\n" +
                r"\caption{" + match.group(1) + "}" +
                r"\label{" + match.group(2) + r"}\\" + "\n")

    expected = len(re.findall(r"\\begin\{table\}(?![a-z])", source))
    source, moved = float_start.subn(place_caption, source)
    if moved != expected:
        raise SystemExit(f"Found {expected} table floats but converted {moved}. "
                         "Check table captions/layouts in main.tex")

    # Strip the enclosing table float (its end immediately follows longtable).
    source = re.sub(r"\\end\{longtable\}\s*\\end\{table\}",
                    lambda m: r"\end{longtable}", source)
    if r"\end{table}" in source:
        raise SystemExit("One or more LaTeX table float wrappers remain")

    print(f"Converted {moved} of {expected} tables for Word")
    return source


def main() -> None:
    if not TEX.is_file() or not BIB.is_file():
        raise SystemExit("main.tex and echorepo_integrated.bib must both be present")
    source = TEX.read_text(encoding="utf-8")
    if "\\begin{filecontents" in source:
        raise SystemExit("Remove filecontents; bibliography must be external")

    # Convert existing TikZ pictures (the original Figure conversion mechanism).
    regex = re.compile(
        r"\\resizebox\{(?:[^{}]*)\}\{!\}\{\s*%?\s*"
        r"(\\begin\{tikzpicture\}.*?\\end\{tikzpicture\})\s*\}",
        re.DOTALL,
    )
    with tempfile.TemporaryDirectory(prefix="echorepo_word_") as temp:
        work = Path(temp)
        figures = work / "figures"
        figures.mkdir()
        count = [0]

        def convert(match):
            count[0] += 1
            number = count[0]
            tex = (
                r"\documentclass[border=5pt]{standalone}" "\n"
                r"\usepackage[T1]{fontenc}" "\n"
                r"\usepackage{lmodern}" "\n"
                r"\usepackage{tikz}" "\n"
                r"\usetikzlibrary{arrows.meta,positioning,fit,calc,shapes.geometric,backgrounds}" "\n"
                r"\newcommand{\code}[1]{\texttt{#1}}" "\n"
                r"\begin{document}" "\n" + match.group(1) + "\n" +
                r"\end{document}" "\n"
            )
            src = figures / f"diagram-{number}.tex"
            src.write_text(tex, encoding="utf-8")
            call(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", src.name], cwd=figures)
            pdf = src.with_suffix(".pdf")
            call(["pdftoppm", "-f", "1", "-singlefile", "-r", "190", "-png",
                  str(pdf), str(figures / f"diagram-{number}")])
            return (r"\includegraphics[width=0.95\linewidth]{figures/diagram-"
                    + str(number) + ".png}")

        source = regex.sub(convert, source)
        if r"\begin{tikzpicture}" in source:
            raise SystemExit("Some TikZ diagrams could not be converted")

        source = prepare_tables(source)
        source = source.replace("($n=10{,}554$)", "(n = 10,554)")
        intermediate = work / "main-word.tex"
        intermediate.write_text(source, encoding="utf-8")
        args = [
            "pandoc", str(intermediate), "--from=latex", "--to=docx",
            "--citeproc", f"--bibliography={BIB}",
            "--metadata=reference-section-title:References",
            f"--resource-path={work}:{ROOT}:{ROOT / 'figures'}",
            "-o", str(OUT),
        ]
        call(args, cwd=ROOT)
    print(f"Created {OUT} with {count[0]} diagrams")


if __name__ == "__main__":
    main()
