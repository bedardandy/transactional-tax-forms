# transactional-tax-forms — developer entry points.
# Most targets are offline; `fetch`, `fill`, `manifest`, and `check-upstream` use network.
.PHONY: help test fetch fill manifest manifest-check check-upstream catalog

help:
	@echo "make test                       run the deterministic test suite (the CI gate)"
	@echo "make fetch FORMS=IRS-SS-4        download blank PDF(s), verified against the manifest"
	@echo "make fill FORM=.. CASE=.. OUT=.. fill a mapped form from a case (needs the blank)"
	@echo "make manifest                    (re)fetch all blanks; rebuild manifest + widget inventory"
	@echo "make manifest-check              report manifest vs source_urls without writing"
	@echo "make check-upstream             re-probe official URLs; flag forms the agencies revised"
	@echo "make catalog                     regenerate forms_index.json + by_domain.json"

test:
	python3 -m pytest tests/ -v

fetch:
	python3 tools/fetch_pdfs.py $(if $(FORMS),--forms $(FORMS),)

fill:
	python3 -m engine.fill_via_mapping --form $(FORM) --case $(CASE) $(if $(OUT),--out $(OUT),)

manifest:
	python3 tools/build_manifest.py

manifest-check:
	python3 tools/build_manifest.py --check

check-upstream:
	python3 tools/check_upstream.py $(if $(FORMS),--forms $(FORMS),)

catalog:
	python3 tools/gen_catalog.py
