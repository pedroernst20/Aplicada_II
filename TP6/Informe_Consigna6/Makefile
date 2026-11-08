LATEX = pdflatex
FLAGS = -interaction=nonstopmode -halt-on-error
TARGET = main
SIM_SCRIPT = sim/simular_consigna6.py

.PHONY: all sim pdf clean distclean

all: sim pdf

sim:
	python3 $(SIM_SCRIPT)

pdf: $(TARGET).pdf

$(TARGET).pdf: $(TARGET).tex plantilla.cls chapters/1_introduccion_y_marco.tex chapters/2_diseno_preregulador.tex chapters/3_transistor_soa_disipador.tex chapters/4_simulaciones_y_calidad.tex
	$(LATEX) $(FLAGS) $(TARGET).tex
	$(LATEX) $(FLAGS) $(TARGET).tex
	$(RM) $(TARGET).aux $(TARGET).log $(TARGET).out $(TARGET).toc $(TARGET).fls $(TARGET).fdb_latexmk $(TARGET).synctex.gz

clean:
	$(RM) *.aux *.log *.out *.toc *.fls *.fdb_latexmk *.synctex.gz chapters/*.aux

distclean: clean
	$(RM) $(TARGET).pdf
