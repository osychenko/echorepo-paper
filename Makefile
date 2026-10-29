PDF=main.pdf
IMAGE=echorepo-paper

.PHONY: all docx clean

all:
	docker build -t $(IMAGE) .
	docker run --rm \
		-v "$(PWD):/paper" \
		$(IMAGE) \
		latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

# Generates paperA_review.docx, including diagrams and correctly placed bibliography.
docx:
	docker build -t $(IMAGE) .
	docker run --rm \
		-v "$(PWD):/paper" \
		$(IMAGE) \
		python3 build_docx.py

clean:
	docker run --rm \
		-v "$(PWD):/paper" \
		$(IMAGE) \
		latexmk -C
