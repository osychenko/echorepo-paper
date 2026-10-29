#!/usr/bin/env python3
"""Create a Word review copy of the ECHOREPO manuscript with citations and diagrams.

Expects main.tex and echorepo_integrated.bib in the project root.
Keeps main.tex unchanged and converts its TikZ figures to PNGs in a temporary
workspace, so Pandoc can embed them as native Word pictures.
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
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if result.returncode:
        raise RuntimeError("Command failed: " + " ".join(command) + "\n" + result.stdout[-6000:])
    if "pandoc" in command[0] and result.stdout.strip():
        print(result.stdout.strip())


def main() -> None:
    if not TEX.is_file() or not BIB.is_file():
        raise SystemExit("main.tex and echorepo_integrated.bib must both be present")
    source = TEX.read_text(encoding="utf-8")
    if "\\begin{filecontents" in source:
        raise SystemExit("Remove filecontents from main.tex; bibliography must be external")

    # Source graphics are wrapped in resizebox {...}{!}{%<tikzpicture>};
    # preserve the surrounding figure environments, captions, and labels.
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
            call(["pdftoppm", "-f", "1", "-singlefile", "-r", "190", "-png", str(pdf), str(figures / f"diagram-{number}")])
            return r"\includegraphics[width=0.95\linewidth]{figures/diagram-" + str(number) + ".png}"

        source = regex.sub(convert, source)
        if "\\begin{tikzpicture}" in source:
            raise SystemExit("Some TikZ diagrams could not be converted")

        # Pandoc does not reliably parse tabularx; normalise to tabular
        # while preserving the rows, headings, captions and table labels.
        source = source.replace(
            r"\begin{tabularx}{\linewidth}{@{}p{4.7cm}X@{}}",
            r"\begin{longtable}{p{4.7cm}p{8.3cm}}",
        )
        source = source.replace(
            r"\begin{tabularx}{\linewidth}{@{}Xrr@{}}",
            r"\begin{longtable}{p{9.0cm}rr}",
        )
        source = source.replace(r"\end{tabularx}", r"\end{longtable}")
        # Pandoc recognises captions and cross-references when they appear
        # *inside* longtable. TeX floats with tabularx hide captions in Word.
        float_start = re.compile(
            r"\\begin\{table\}\[htbp\]\s*"
            r"\\centering\\small\s*"
            r"\\caption\{([^\n]*)\}\s*"
            r"\\label\{([^}]+)\}\s*"
            r"(\\begin\{longtable\}\{[^\n]*\})",
        )
        def place_caption(match):
            return (match.group(3) + "\n" +
                    r"\caption{" + match.group(1) + "}" +
                    r"\label{" + match.group(2) + "}" + ("\\" * 2) + "\n")
        source, moved = float_start.subn(place_caption, source)
        if moved != 2:
            raise SystemExit(f"Expected 2 table floats, found {moved}")
        source = source.replace(r"\end{longtable}" + "\n" + r"\end{table}", r"\end{longtable}")
        # Keep scientific content unchanged; this is only a Pandoc math-caption workaround.
        source = source.replace("($n=6{,}871$)", "(n = 6,871)")
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
