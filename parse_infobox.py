import re

re_comment = re.compile('<!--.*?-->', re.S)

def strip_comment(s):
    return re_comment.sub('', s).strip('|\t\n\r ')

re_template_token = re.compile(r'(\{\{([^|{}]+)\|?|\}\})')
def find_templates(page):
    stack = 0
    m = re_template_token.search(page)
    templates = []
    while m:
        if m.group().startswith('{{'):
            templates.append((m.start(), m.group(2)))
            stack += 1
        #print stack * ' ', stack, m.start(), m.end(), `m.group(0)`
        if m.group() == '}}':
            stack -= 1
            start, name = templates.pop()
            yield (name, page[start:m.end()])
        m = re_template_token.search(page, m.end())

re_inner_token = re.compile(r'(\[\[|\{\{|\}\}|\|([^}\[\]=<>]+)=|\]\]|<!--|-->)')
def parse_template(text):
    assert text.startswith('{{') and text.endswith('}}')
    name = text[2:text.find('|')].strip()
    if '|' not in text:
        return name
    link_stack = 0
    template_stack = 0
    comment = False
    m = re_inner_token.search(text)
    xend = 0
    xkey = None
    pairs = []
    while m:
        token = m.group(0)
        #print link_stack, template_stack, `token`
        if comment:
            if token == '-->':
                comment = False
        elif token == '<!--':
            comment = True
        elif token == '{{':
            template_stack += 1
        elif token == '}}':
            template_stack -= 1
            if template_stack == 0:
                pairs.append((xkey, strip_comment(text[xend:m.start()])))
        elif token == '[[':
            link_stack += 1
        elif token == ']]':
            link_stack -= 1
        elif link_stack == 0 and template_stack == 1:
            #print m.start(), m.end(), `m.group(0)`
            if xkey:
                pairs.append((xkey, strip_comment(text[xend:m.start()])))
            xend = m.end()
            xkey = m.group(2).strip('| \n\r')
        m = re_inner_token.search(text, m.end())
    return pairs
