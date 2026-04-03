JS_SRC = src/imio/omnia/tinymce/browser/resources
STATIC  = src/imio/omnia/tinymce/browser/static

.PHONY: build-js clean-js

build-js:
	cd $(JS_SRC) && npm ci && npm run build
	cp $(JS_SRC)/dist/omnia-tinymce.umd.cjs  $(STATIC)/omnia-tinymce.js
	cp $(JS_SRC)/dist/omnia-tinymce.css $(STATIC)/omnia-tinymce.css

clean-js:
	rm -f $(STATIC)/omnia-tinymce.js $(STATIC)/omnia-tinymce.css
