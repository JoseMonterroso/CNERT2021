all: paper.pdf reproduce.pdf demo.pdf

paper.pdf: bibtex/*.bib *.tex 
	pdflatex paper
	bibtex paper
	pdflatex paper
	pdflatex paper
	pdflatex paper

reproduce.pdf: bibtex/*.bib *.tex
	pdflatex reproduce
	pdflatex reproduce
	pdflatex reproduce

demo.pdf: bibtex/*.bib *.tex
	pdflatex demo
	bibtex demo
	pdflatex demo
	pdflatex demo
	pdflatex demo

clean: 
	\rm -f *.aux *.spl *~ *.log *.blg *.bbl *.dep *.out *.synctex.gz paper.pdf reproduce.pdf demo.pdf

