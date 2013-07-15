import re
from decimal import *

from django.contrib.staticfiles.storage import staticfiles_storage
from django.template.defaultfilters import stringfilter
from django.utils.html import strip_tags, escape

from jingo import register
import scrubber

@register.filter
def tablecols(data, cols):
    rows = []
    row = []
    index = 0
    for user in data:
        row.append(user)
        index = index + 1
        if index % cols == 0:
            rows.append(row)
            row = []
    # Still stuff missing?
    if len(row) > 0:
        for i in range(cols - len(row)):
            row.append([])
        rows.append(row)
    return rows

# Put commas in things
# http://code.activestate.com/recipes/498181-add-thousands-separator-commas-to-formatted-number/
re_digits_nondigits = re.compile(r'\d+|\D+')

@register.filter
@stringfilter
def commas(value):
    parts = re_digits_nondigits.findall(value)
    for i in xrange(len(parts)):
        s = parts[i]
        if s.isdigit():
            parts[i] = _commafy(s)
            break
    return ''.join(parts)

def _commafy(s):
    r = []
    for i, c in enumerate(reversed(s)):
        if i and (not (i % 3)):
            r.insert(0, ',')
        r.insert(0, c)
    return ''.join(r)


# Turn a duration in seconds into a human readable string
@register.filter
def duration(s):
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    parts = []
    if d:
        parts.append('%dd' % (d))
    if h:
        parts.append('%dh' % (h))
    if m:
        parts.append('%dm' % (m))
    if s:
        parts.append('%ds' % (s))

    return ' '.join(parts)

@register.filter
def duration_right(s):
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)

    parts = []
    if d:
        parts.append('%dd' % (d))
    if h or d:
        parts.append('%02dh' % (h))
    if m or h or d:
        parts.append('%02dm' % (m))
    parts.append('%02ds' % (s))

    return ' '.join(parts)


# Turn a duration in seconds into a shorter human readable string
@register.filter
def shortduration(s):
    return ' '.join(duration(s).split()[:2])

# Do balance colouring (red for negative, green for positive)
@register.filter
@stringfilter
def balance(s):
    if s == '0':
        return s
    elif s.startswith('-'):
        return '<span class="neg">%s</span>' % (s)
    else:
        return '<span class="pos">%s</span>' % (s)

@register.filter
def balance_class(n):
    if n < 0:
        return 'neg'
    else:
        return 'pos'


roman_list = ['', 'I', 'II', 'III', 'IV', 'V']

@register.filter
def roman(num):
    if isinstance(num, str) or isinstance(num, unicode):
        return roman_list[int(num)]
    elif isinstance(num, int) or isinstance(num, long):
        return roman_list[num]
    else:
        return ''

MONTHS = [None, 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
@register.filter
def month_name(num):
    return MONTHS[num]

@register.filter
def date(d, f):
    return d.strftime(f)

# Shorten numbers to a human readable version
THOUSAND = 10**3
TEN_THOUSAND = 10**4
MILLION = 10**6
BILLION = 10**9
@register.filter
def humanize(value):
    if value is None or value == '':
        return '0'

    if value >= BILLION or value <= -BILLION:
        v = Decimal(value) / BILLION
        return '%sB' % (v.quantize(Decimal('.01'), rounding=ROUND_UP))
    elif value >= MILLION or value <= -MILLION:
        v = Decimal(value) / MILLION
        if v >= 10:
            return '%sM' % (v.quantize(Decimal('.1'), rounding=ROUND_UP))
        else:
            return '%sM' % (v.quantize(Decimal('.01'), rounding=ROUND_UP))
    elif value >= TEN_THOUSAND or value <= -TEN_THOUSAND:
        v = Decimal(value) / THOUSAND
        return '%sK' % (v.quantize(Decimal('.1'), rounding=ROUND_UP))
    elif value >= THOUSAND or value <= -THOUSAND:
        return '%s' % (commas(Decimal(value).quantize(Decimal('1.'), rounding=ROUND_UP)))
    else:
        if isinstance(value, Decimal):
            return value.quantize(Decimal('.1'), rounding=ROUND_UP)
        else:
            return value

# Conditionally wrap some text in a span if it matches a condition. Ugh.
@register.filter
def spanif(value, arg):
    parts = arg.split()
    if len(parts) != 3:
        return value

    n = int(parts[2])
    if (parts[1] == '<' and value < n) or (parts[1] == '=' and value == n) or (parts[1] == '>' and value > n):
        return '<span class="%s">%s</span>' % (parts[0], value)
    else:
        return value

# Jinja2 filter version of staticfiles. Hopefully.
@register.function
def static(path):
    return staticfiles_storage.url(path)

@register.filter
def keeptags(text, tags):
    """
    Strips all [X]HTML tags except the space separated list of tags
    from the output.

    Usage: keeptags:"strong em ul li"
    """
    tags = [re.escape(tag) for tag in tags.split()]
    tags_re = '(%s)' % '|'.join(tags)
    singletag_re = re.compile(r'<(%s\s*/?)>' % tags_re)
    starttag_re = re.compile(r'<(%s)(\s+[^>]+)>' % tags_re)
    endtag_re = re.compile(r'<(/%s)>' % tags_re)
    text = singletag_re.sub('##~~~\g<1>~~~##', text)
    text = starttag_re.sub('##~~~\g<1>\g<3>~~~##', text)
    text = endtag_re.sub('##~~~\g<1>~~~##', text)
    text = strip_tags(text)
    text = escape(text)
    recreate_re = re.compile('##~~~([^~]+)~~~##')
    text = recreate_re.sub('<\g<1>>', text)
    return text
