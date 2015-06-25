i18n = viaduct/translations
cfg = babel.cfg
messages = messages.pot
pybabel=venv/bin/pybabel


# Compile the translations .po files to .mo files usable by flask.
.PHONY: babel_compile
babel_compile: babel_update
	python ${pybabel} compile -d ${i18n}


# Merge the new messages.pot with the existing translations.
.PHONY: babel_update
babel_update: babel_extract
	python ${pybabel} update -i ${messages} -d ${i18n}
	make clean


# Extract all the marked strings from the repository.
.PHONY: babel_extract
babel_extract:
	python ${pybabel} extract -F ${cfg} --sort-output -k lazy_gettext -o ${messages} .


# DO NOT USE ON EXISTING BABEL INSTALLATION
# .PHONY: init
# init: extract
	# python ${pybabel} init -i messages.pot -d translations -l en
	# python ${pybabel} init -i messages.pot -d translations -l nl
	# make clean


# Delete crap
.PHONY: clean
clean:
	rm ${messages}
