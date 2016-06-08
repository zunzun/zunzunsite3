



import django.forms.widgets
import django.utils.encoding
import django.utils.safestring
import django.utils.html
from itertools import chain

class Spaced_RadioFieldRenderer(django.forms.widgets.RadioFieldRenderer):

    def render(self):
        leadingSpaces = '' # the first item has no leading spaces
        itemString = ''
        for w in self:
            itemString += leadingSpaces + django.utils.encoding.force_text(w) + '\n'
            leadingSpaces = '&nbsp;&nbsp;&nbsp;'
        return django.utils.safestring.mark_safe(itemString)


class BR_RadioFieldRenderer(django.forms.widgets.RadioFieldRenderer):

    def render(self):
        itemString = ''
        for w in self:
            itemString += django.utils.encoding.force_text(w) + '<br>\n'
        return django.utils.safestring.mark_safe(itemString)


class ColorTD_RadioFieldRenderer(django.forms.widgets.RadioFieldRenderer):

    def render(self):
        itemString = ''
        for w in self:
            itemString += '<TD align="left" BGCOLOR="#' + django.utils.encoding.force_text(w.choice_value) + '">&nbsp;' + django.utils.encoding.force_text(w) + '&nbsp;</TD>\n'
        return django.utils.safestring.mark_safe(itemString)

class BR_CheckboxSelectMultiple_Widget(django.forms.widgets.CheckboxSelectMultiple):

    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs, name=name)
        output = []
        # Normalize to strings
        str_values = set([django.utils.encoding.force_text(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = ' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = django.forms.widgets.CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = django.utils.encoding.force_text(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = django.utils.html.conditional_escape(django.utils.encoding.force_text(option_label))
            output.append('<label%s>%s %s</label><br>' % (label_for, rendered_cb, option_label))
        return django.utils.safestring.mark_safe('\n'.join(output))
