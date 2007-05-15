from django import template

register = template.Library()

class MenuItemNode(template.Node):
    def __init__(self, path, label):
        self.path = path
        self.label = label.strip('"')

    def render(self, context):
        ctx_path = context['request'].path

        active = False
        if self.path == '/':
            active = ctx_path == '/'
        else: 
            active = ctx_path.startswith(self.path)

        act_class = ''
        if active:
            act_class = ' class="active"'

        return '<a%s href="%s">%s</a>' % (act_class, self.path, self.label)

@register.tag
def menuitem(parser, token):

    try:
        tag_name, path, label = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, \
                "%r tag requires exactly two arguments: path and label" % \
                token.split_contents[0]

    return MenuItemNode(path, label)
