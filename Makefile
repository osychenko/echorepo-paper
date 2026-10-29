PDF=main.pdf
IMAGE=echorepo-paper

all:
	docker build -t $(IMAGE) .
	docker run --rm \
		-v $(PWD):/paper \
		$(IMAGE) \
		latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

docx:
	docker build -t $(IMAGE) .
	docker run --rm \
		-v "$(PWD):/paper" \
		$(IMAGE) \
		pandoc main.tex \
			--from=latex \
			--to=docx \
			--citeproc \
			--bibliography=echorepo_integrated.bib \
			--resource-path=/paper:/paper/figures:/paper/sections \
			-o paperA_review.docx

clean:
	docker run --rm \
		-v $(PWD):/paper \
		$(IMAGE) \
		latexmk -C