"""Extract parameter descriptions using the same mandoc renderer as man pages."""

import re
import subprocess
from html.parser import HTMLParser


class Element:
    def __init__(self, tag='', attrs=()):
        self.tag = tag
        self.attrs = dict(attrs)
        self.children = []

    def text(self):
        return ''.join(child if isinstance(child, str) else child.text()
                       for child in self.children)

    def find(self, tag, nested=True):
        for child in self.children:
            if isinstance(child, Element):
                if child.tag == tag:
                    yield child
                    if not nested:
                        continue
                yield from child.find(tag, nested)


class ManHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Element()
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Element(tag, attrs)
        self.stack[-1].children.append(node)
        if tag not in {'br', 'hr', 'meta', 'link', 'img', 'input'}:
            self.stack.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def plain(text):
    """Upstream text is prose, never reStructuredText markup."""
    text = ' '.join(text.split())
    for char in ('\\', '`', '*', '|', '_'):
        text = text.replace(char, '\\' + char)
    return text


def indent(text, width):
    return '\n'.join(' ' * width + line if line else ''
                     for line in text.splitlines())


def blocks(node):
    """Keep paragraphs, lists, tables and displays as native RST blocks."""
    out, pending = [], []

    def flush():
        text = plain(''.join(pending))
        if text:
            out.append(text)
        pending.clear()

    for child in node.children:
        if isinstance(child, str):
            pending.append(child)
        elif child.tag in {'p', 'div', 'section'}:
            flush()
            out.append(blocks(child))
        elif child.tag == 'pre':
            flush()
            out.append('::\n\n' + indent(child.text().rstrip(), 3))
        elif child.tag in {'ul', 'ol', 'dl'}:
            flush()
            items = []
            for item in child.children:
                if not isinstance(item, Element):
                    continue
                if item.tag == 'dt':
                    items.append(plain(item.text()))
                elif item.tag == 'dd':
                    items.append(indent(blocks(item), 3))
                elif item.tag == 'li':
                    marker = '#. ' if child.tag == 'ol' else '* '
                    text = indent(blocks(item), 3)
                    items.append(marker + text[3:])
            out.append('\n\n'.join(items))
        elif child.tag == 'table':
            flush()
            rows = [[plain(cell.text()) for cell in row.children
                     if isinstance(cell, Element) and cell.tag in {'td', 'th'}]
                    for row in child.find('tr')]
            rows = [row for row in rows if row]
            if rows:
                width = max(map(len, rows))
                table = ['.. list-table::', '']
                for row in rows:
                    row += [''] * (width - len(row))
                    table.append('   * - ' + row[0])
                    table.extend('     - ' + cell for cell in row[1:])
                out.append('\n'.join(table))
        elif child.tag == 'br':
            pending.append(' ')
        else:
            pending.append(child.text())
    flush()
    return '\n\n'.join(part for part in out if part)


def descriptions(source, names):
    """Render a whole man page once; pair parameter terms with their bodies.

    Restrict extraction to known parameter names so nested definition lists
    and other sections cannot be mistaken for parameter declarations.
    """
    rendered = subprocess.run(
        ['mandoc', '-T', 'html', '-O', 'fragment'], input=source,
        text=True, capture_output=True, check=True)
    parser = ManHTML()
    parser.feed(rendered.stdout)
    result = {}
    for listing in parser.root.find('dl', nested=False):
        current = None
        for child in listing.children:
            if not isinstance(child, Element):
                continue
            if child.tag == 'dt':
                # IDs may have suffixes when the same word appears earlier
                # in the page; old man5 terms do not have IDs at all.
                words = child.text().split()
                name = words[0].split('=', 1)[0] if words else ''
                current = name if name in names else None
            elif child.tag == 'dd' and current:
                text = blocks(child)
                if text:
                    result[current] = text
                current = None
    # Historical OpenZFS man5 pages use a paragraph followed by .RS/.RE,
    # rather than .TP, for each parameter.
    for section in parser.root.find('section'):
        current = None
        for child in section.children:
            if not isinstance(child, Element):
                continue
            if child.tag == 'p':
                match = re.fullmatch(r'([a-z][a-z0-9_]*)\s+\([a-z0-9_ ]+\)',
                                     ' '.join(child.text().split()))
                current = match.group(1) if match and match.group(1) in names else None
            elif child.tag == 'div' and current:
                if 'Bd-indent' in child.attrs.get('class', '').split():
                    text = blocks(child)
                    if text:
                        result[current] = text
                current = None
    return result
