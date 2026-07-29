JS_PKG  = src/imio/omnia/tinymce/browser/npm
JS_PIN  = $(JS_PKG)/node_modules/@imiobe/omnia-tinymce
STATIC  = src/imio/omnia/tinymce/browser/static

.PHONY: update-js clean-js

update-js:
	cd $(JS_PKG) && npm install
	cp $(JS_PIN)/dist/omnia-tinymce.umd.cjs $(STATIC)/omnia-tinymce.js
	cp $(JS_PIN)/dist/omnia-tinymce.css $(STATIC)/omnia-tinymce.css

clean-js:
	rm -f $(STATIC)/omnia-tinymce.js $(STATIC)/omnia-tinymce.css
