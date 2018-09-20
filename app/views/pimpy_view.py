from flask import Blueprint, render_template, abort

blueprint = Blueprint('pimpy2', __name__, url_prefix='/pimpy2')


@blueprint.route("/")
def root():
    # abort(404)
    return render_template("vue_content.htm", vue=True)
