PDF=main.pdf

all:
	docker build -t echorepo-paper .
	docker run --rm \
		-v $(PWD):/paper \
		echorepo-paper \
		latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex

clean:
	docker run --rm \
		-v $(PWD):/paper \
		echorepo-paper \
		latexmk -C