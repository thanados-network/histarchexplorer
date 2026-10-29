#!/bin/bash

pybabel extract -F translations/babel.cfg -k lazy_gettext -k _l -o translations/messages.pot .
#babel init -i translations/messages.pot -d translations -l de
pybabel update -i translations/messages.pot -d translations/
pybabel compile -d translations

