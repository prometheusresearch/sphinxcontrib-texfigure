#
# Copyright (c) 2013, Prometheus Research, LLC
#


from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx.util.osutil import ensuredir
from subprocess import Popen, PIPE
import os, os.path, tempfile, shutil


class TeXFigureDirective(Directive):

    required_arguments = 1
    has_content = False
    option_spec = {
        'alt': directives.unchanged,
        'align': lambda arg: directives.choice(arg, ('left', 'center', 'right')),
    }

    def run(self):
        doc = self.state.document
        env = doc.settings.env
        docdir = os.path.dirname(env.doc2path(env.docname, base=None))
        filename = self.arguments[0]
        if filename.startswith('/'):
            filename = os.path.normpath(filename[1:])
        else:
            filename = os.path.normpath(os.path.join(docdir, filename))
        env.note_dependency(filename)
        filename = os.path.join(env.srcdir, filename)
        try:
            name, data, width, height = render_texfigure(env, filename)
        except TeXFigureError as exc:
            return [doc.reporter.error(str(exc))]
        node = texfigure()
        node['name'] = name
        node['data'] = data
        node['width'] = width
        node['height'] = height
        node['alt'] = self.options.get('alt')
        node['align'] = self.options.get('align')
        return [node]


class TeXFigureError(Exception):
    pass


class texfigure(nodes.General, nodes.Element):
    pass


def render_texfigure(env, filename):
    directory = os.path.dirname(filename)
    basename = os.path.basename(filename)
    stem = os.path.splitext(basename)[0]
    name = stem + '.png'
    temp = tempfile.mkdtemp()
    try:
        texinputs = [directory]
        for texdir in env.config.texfigure_texinputs:
            texdir = os.path.join(env.srcdir, texdir)
            texinputs.append(texdir)
        texinputs.append('')
        texinputs = ':'.join(texinputs)
        environ = os.environ.copy()
        environ['TEXINPUTS'] = texinputs
        cmdline = [env.config.texfigure_pdftex,
                   '-halt-on-error',
                   '-interaction', 'nonstopmode',
                   '-output-directory', temp,
                   basename]
        shell(cmdline, env=environ)
        cmdline = [env.config.texfigure_pdftoppm,
                   '-r', str(env.config.texfigure_resolution),
                   '-f', '1', '-l', '1',
                   os.path.join(temp, stem)+'.pdf',
                   os.path.join(temp, stem)]
        shell(cmdline)
        ppmfile = os.path.join(temp, stem)+'-1.ppm'
        if not os.path.exists(ppmfile):
            raise TeXFigureError("file not found: %s" % ppmfile)
        data = open(ppmfile, 'rb').read()
        cmdline = [env.config.texfigure_pnmcrop]
        data = shell(cmdline, data)
        line = data.splitlines()[1]
        width, height = [int(chunk) for chunk in line.split()]
        cmdline = [env.config.texfigure_pnmtopng,
                   '-transparent', 'white',
                   '-compression', '9']
        data = shell(cmdline, data)
    finally:
        shutil.rmtree(temp)
    return name, data, width, height


def shell(cmdline, input=None, env=None):
    try:
        process = Popen(cmdline, stdin=PIPE, stdout=PIPE, stderr=PIPE, env=env)
    except OSError as exc:
        raise TeXFigureError("cannot start executable `%s`: %s"
                             % (' '.join(cmdline), exc))
    output, error = process.communicate(input)
    if process.returncode != 0:
        if not error:
            error = output
        raise TeXFigureError("`%s` exited with an error:\n%s"
                             % (' '.join(cmdline), error))
    return output


def visit_texfigure(self, node):
    href = "%s/%s" % (self.builder.imgpath, node['name'])
    filename = os.path.join(self.builder.outdir, '_images', node['name'])
    ensuredir(os.path.dirname(filename))
    open(filename, 'wb').write(node['data'])
    if (isinstance(node.parent, nodes.TextElement) or
        (isinstance(node.parent, nodes.reference) and
         not isinstance(node.parent.parent, nodes.TextElement))):
        suffix = ''
    else:
        suffix = '\n'
    atts = {}
    atts['src'] = href
    atts['width'] = node['width']
    atts['height'] = node['height']
    if node['alt']:
        atts['alt'] = node['alt']
    atts['class'] = 'texfigure'
    if node['align']:
        atts['class'] += ' align-%s' % node['align']
    self.body.append(self.emptytag(node, 'img', suffix, **atts))


def depart_texfigure(self, node):
    pass


def setup(app):
    app.add_config_value('texfigure_pdftex', 'pdflatex', 'env')
    app.add_config_value('texfigure_pdftoppm', 'pdftoppm', 'env')
    app.add_config_value('texfigure_pnmcrop', 'pnmcrop', 'env')
    app.add_config_value('texfigure_pnmtopng', 'pnmtopng', 'env')
    app.add_config_value('texfigure_texinputs', [], 'env')
    app.add_config_value('texfigure_resolution', 110, 'env')
    app.add_directive('texfigure', TeXFigureDirective)
    app.add_node(texfigure,
                 html=(visit_texfigure, depart_texfigure))


