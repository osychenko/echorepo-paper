ECHOREPO manuscript revision — 30 October 2026

Based on GitHub osychenko/echorepo-paper, main branch, at main.tex blob fe5e922cae65e967b1e1fa2ac813b3eb78c0d798.
Contains complete replacements for main.tex and echorepo_integrated.bib, plus the unchanged build_docx.py from the repo and PDF/DOCX previews.

CHANGES
- FAIR-oriented framing and sharpened introduction focused on physical samples and successive laboratory workflows
- 29 October 2026 v12 Zenodo dataset DOI 10.5281/zenodo.23784504 and ECHO Consortium attribution
- GitHub-connected software archive DOI 10.5281/zenodo.21105834
- Two schematic (not empirical) sample journeys: progressive enrichment and planned-country mismatch
- Domain overlap distribution: 678/4,362/4,517/997 samples with 0/1/2/3 linked additional domains
- Biodiversity co-coverage: 997 of 1,200 (83.08%) linked to both images and laboratory results
- Explicit code and data availability, limitations of QA denominator and subset representativeness
- QA workflow schematic replaced by a data coverage graphic; 4 total diagrams/charts and 3 tables

STILL TO VALIDATE BEFORE SUBMISSION
- The 396 QA-flagged sample IDs must be reconciled against the 10,554 sample IDs for the 3.75% rate.
- The GitHub-connected software Zenodo DOI's exact release metadata, title and creator should be checked against its record.
- The code version/commit and coverage-statistics script should be archived or linked unambiguously.
- The two-sample figure is deliberately schematic; it does not demonstrate empirical individual cases.
- Authorship/affiliations and journal declarations remain provisional.

USAGE
Unzip over the root of osychenko/echorepo-paper; inspect the diff before committing.
To build the PDF: latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
To build the Word review copy: python3 build_docx.py
The existing Makefile also offers make and make docx using Docker.

NOTE: GitHub connector read access succeeded but writing was rejected (403 Resource not accessible by integration). No remote commit has been made.
