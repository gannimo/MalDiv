filename = malwarediversity

all: $(filename).pdf

$(filename).pdf: $(filename).tex bibliography.bib
	pdflatex $(filename).tex
	bibtex $(filename).aux
	pdflatex $(filename).tex

$(filename).ps: $(filename).pdf
	pdftops $(filename).pdf

.PHONY=view
view: $(filename).pdf
	evince $(filename).pdf

clean:
	rm -f *.aux *.bbl *.log *.dvi *.blg *~ *.ps *.out
