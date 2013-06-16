from __future__ import absolute_import

from flask import current_app
from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor


class PreviewPostprocessor(Postprocessor):
    def run(self, text):
        continue_fragment = current_app.config['POST_CONTINUE_LINK_FRAGMENT']
        return text.replace(current_app.config['POST_BODY_PREVIEW_SEPARATOR'],
                            '<div id="{}"></div>'.format(continue_fragment))


class EstherExtension(Extension):
    def extendMarkdown(self, md, md_globals):
        md.postprocessors.add('previewpp', PreviewPostprocessor(md), '_end')
