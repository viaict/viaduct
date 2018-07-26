from flask import Blueprint, render_template

blueprint = Blueprint('pimpy2', __name__, url_prefix='/pimpy2')


@blueprint.route("/")
def root():
    return render_template("vue_content.htm", vue=True)
