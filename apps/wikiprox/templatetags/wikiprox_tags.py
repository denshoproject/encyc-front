from django import template

from wikiprox.sources import format_primary_source


register = template.Library()


class PrimarySourceNode(template.Node):
    def __init__(self, primarysource):
        self.primarysource = template.Variable(primarysource)
    def render(self, context):
        try:
            primarysource = self.primarysource.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        return format_primary_source(primarysource)

def do_primarysource(parser, token):
    """Render a Source using a templatetag.
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, primarysource = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument" % token.contents.split()[0]
    return PrimarySourceNode(primarysource)

register.tag('primarysource', do_primarysource)
