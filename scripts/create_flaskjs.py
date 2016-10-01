from app import js_glue

with open('src/js/global/flask.js', 'w', encoding='utf8') as f:
    f.write(js_glue.generate_js())
