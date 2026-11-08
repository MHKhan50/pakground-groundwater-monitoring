.PHONY: install test prepare validate analyse clean
install:
	python3 -m pip install -r requirements.txt
test:
	python3 -m unittest discover -s tests -v
prepare:
	python3 scripts/prepare_dataset.py --download
validate:
	python3 scripts/validate_dataset.py
analyse:
	python3 scripts/analyse.py
clean:
	rm -f data/pakistan_groundwater_observations.csv results/site_trends.csv
