from flask import Blueprint, request, flash, render_template, redirect, url_for

from esther.forms import ContactForm

blueprint = Blueprint('general', __name__)

@blueprint.route('/')
def index():
    return render_template('general/index.html')

@blueprint.route('/about')
def about():
    return render_template('general/about.html')

@blueprint.route('/contact', methods=('GET', 'POST'))
def contact():
    form = ContactForm(request.form)

    if form.validate_on_submit():
        flash(u'Your message has been sent. I will get back to you as soon '
              'as possible.')
        return redirect(url_for('general.index'))

    return render_template('general/contact.html', form=form)
