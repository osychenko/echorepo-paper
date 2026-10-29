FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-bibtex-extra \
    biber \
    latexmk \
    lmodern \
    pandoc \
    python3 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /paper
