#!/usr/bin/env python3

# License: CC0 https://creativecommons.org/share-your-work/public-domain/cc0/

# A messy script that figures out ZFS features. It's very messy, sorry. I am
# not responsible if this script eats your laundry.
#
# This uses manpages, because I'm lazy. If your manpages are wrong, you have a
# bug.
#
# If the script is wrong, or could be improved, feel free to contact me on
# freenode, and tell me why it's wrong. My nick is zgrep.
#
# 2018-07-05: Created.
# ????-??-??: Many things happened.
# 2020-02-23: Applied patch by rlaager.
# 2020-02-30: Show domain prefixes (via Vlad Bokov), partially apply patch by
#   rlaager.
# 2020-03-05: Patch by rlaager (allocation_classes, ZoL -> openzfs).
# 2020-10-07: Rework by gmelikov for openzfs-docs

import logging
import sys

from collections import defaultdict
from urllib.request import urlopen
from datetime import datetime
from re import sub as regex, findall
from json import loads as dejson

LOG = logging.getLogger()
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

if len(sys.argv) == 1:
    path = '.'
elif len(sys.argv) != 2:
    print('Usage:', sys.argv[0], 'path')
    exit(1)
else:
    path = sys.argv[1]


def zfsonlinux():
    sources = {'master': 'https://raw.githubusercontent.com/openzfs/zfs/'
               'master/man/man5/zpool-features.5'}
    with urlopen('https://zfsonlinux.org') as web:
        versions = findall(r'download/zfs-([0-9.]+)',
                           web.read().decode('utf-8', 'ignore'))
    for ver in set(versions):
        sources[ver] = ('https://raw.githubusercontent.com/openzfs/zfs/'
                        'zfs-{}/man/man5/zpool-features.5'.format(ver))
    return sources


def openzfsonosx():
    sources = {'master': 'https://raw.githubusercontent.com/openzfsonosx/'
               'zfs/master/man/man5/zpool-features.5'}
    with urlopen('https://api.github.com/repos/openzfsonosx/zfs/tags') as web:
        try:
            tags = dejson(web.read().decode('utf-8', 'ignore'))
            tags = [x['name'].lstrip('zfs-') for x in tags]
            tags.sort()
            latest = tags[-1]
            tags = [tag for tag in tags if 'rc' not in tag]
            if 'rc' not in latest:
                tags = tags[-3:]
            else:
                tags = tags[-2:] + [latest]
        except Exception:
            tags = []
    for ver in tags:
        sources[ver] = ('https://raw.githubusercontent.com/openzfsonosx/zfs/'
                        'zfs-{}/man/man5/zpool-features.5'.format(ver))
    return sources


def freebsd():
    sources = {'head': 'https://svnweb.freebsd.org/base/head/cddl/contrib/'
               'opensolaris/cmd/zpool/zpool-features.7?view=co'}
    with urlopen('https://www.freebsd.org/releases/') as web:
        versions = findall(r'/releases/([0-9.]+?)R',
                           web.read().decode('utf-8', 'ignore'))
    with urlopen('https://svnweb.freebsd.org/base/release/') as web:
        data = web.read().decode('utf-8', 'ignore')
    actualversions = []
    for ver in set(versions):
        found = list(sorted(findall(
            r'/base/release/(' + ver.replace('.', '\\.') + r'[0-9.]*)',
            data
            )))
        if found:
            actualversions.append(found[-1])
    for ver in actualversions:
        sources[ver] = ('https://svnweb.freebsd.org/base/release/{}/cddl/'
                        'contrib/opensolaris/cmd/zpool/zpool-features.7'
                        '?view=co'.format(ver))
    return sources


def omniosce():
    sources = {'master': 'https://raw.githubusercontent.com/omniosorg/'
               'illumos-omnios/master/usr/src/man/man5/zpool-features.5'}
    with urlopen('https://omniosce.org/releasenotes.html') as web:
        versions = findall(r'omnios-build/blob/(r[0-9]+)',
                           web.read().decode('utf-8', 'ignore'))
    versions.sort()
    versions = versions[-2:]
    for ver in versions:
        sources[ver] = ('https://raw.githubusercontent.com/omniosorg/'
                        'illumos-omnios/{}/usr/src/man/man5/'
                        'zpool-features.5'.format(ver))
    return sources


def joyent():
    sources = {'master': 'https://raw.githubusercontent.com/joyent/'
               'illumos-joyent/master/usr/src/man/man5/zpool-features.5'}
    with urlopen('https://github.com/joyent/illumos-joyent') as web:
        versions = findall(r'data-name="release-([0-9]+)"',
                           web.read().decode('utf-8', 'ignore'))
    versions.sort()
    versions = versions[-2:]
    for ver in versions:
        sources[ver] = ('https://raw.githubusercontent.com/joyent/illumos-'
                        'joyent/release-{}/usr/src/man/man5/'
                        'zpool-features.5'.format(ver))
    return sources


def netbsd():
    url = ('http://cvsweb.netbsd.org/bsdweb.cgi/~checkout~/src/external/'
           'cddl/osnet/dist/cmd/zpool/zpool-features.7'
           '?content-type=text/plain&only_with_tag={}')
    sources = {'main': url.format('MAIN')}
    with urlopen('https://netbsd.org/releases/') as web:
        tags = findall(r'href="formal-.+?/NetBSD-(.+?)\.html',
                       web.read().decode('utf-8', 'ignore'))
    tags = [(v, 'netbsd-' + v.replace('.', '-') + '-RELEASE') for v in tags]
    for ver, tag in tags:
        if int(ver.split('.')[0]) >= 9:
            sources[ver] = url.format(tag)
    return sources


sources = {
        'OpenZFS on Linux': zfsonlinux(),
        'FreeBSD': freebsd(),
        'OpenZFS on OS X': openzfsonosx(),
        'OmniOS CE': omniosce(),
        'Joyent': joyent(),
        'NetBSD': netbsd(),
        'Illumos': {
            'master': 'https://raw.githubusercontent.com/illumos/illumos-gate/'
                      'master/usr/src/man/man5/zpool-features.5',
            },
        # 'OpenZFS on Windows': {
        #    'master': 'https://raw.githubusercontent.com/openzfsonwindows/ZFSin/master/ZFSin/zfs/man/man5/zpool-features.5',
        #    },
        }

features = defaultdict(list)
readonly = dict()

for name, sub in sources.items():
    LOG.debug('Work on %s...', name)
    for ver, url in sub.items():
        LOG.debug('Get %s...', url)
        with urlopen(url) as c:
            if c.getcode() != 200:
                continue
            man = c.read().decode('utf-8')
        for line in man.split('\n'):
            if line.startswith('.It '):
                line = line[4:]
            if line.startswith('GUID'):
                guid = line.split()[-1]
                if guid == 'com.intel:allocation_classes':
                    # This is wrong in the documentation for Illumos and
                    # FreeBSD.  The actual code in zfeature_common.c uses
                    # org.zfsonlinux:allocation_classes.
                    guid = 'org.zfsonlinux:allocation_classes'
                elif guid == 'org.open-zfs:large_block':
                    guid += 's'
                domain, feature = guid.split(':', 1)
                features[(feature, domain)].append((name, ver))
            elif line.startswith('READ\\-ONLY COMPATIBLE'):
                readonly[guid] = (line.split()[-1] == 'yes')

header = list(sorted(sources.keys()))
header = list(zip(header, (sorted(sources[name],
              key=lambda x: regex(r'[^0-9]', '', x) or x) for name in header)))
header.append(('Sortix', ('current',)))

html = open(path + '/zfs.html', 'w')

f_len, d_len = zip(*features.keys())
f_len, d_len = max(map(len, f_len)), max(map(len, d_len)) + 1

html.write('''<!DOCTYPE html>
<title>ZFS Feature Matrix</title>
<meta charset="utf-8" /><meta name="referrer" content="never" />
<link rel='shortcut icon' href='/favicon.ico' type='image/x-icon'>
<style>body{font-family: "Helvetica", "Arial", sans-serif}
.yes{background-color:lightgreen}
.warn{background-color:yellow}
.no{background-color:lightsalmon}
abbr{text-decoration: none}
table{border-collapse: collapse}
th,td{padding:0.2em 0.4em;border:1px solid #aaa;background-color:#f9f9f9}
th{background-color:#eaecf0}
.l{display:inline-block;text-align:right;min-width:''' + str(d_len) + '''ex;color:#777}
.r{display:inline-block;text-align:left;min-width:''' + str(f_len) + '''ex}</style>
''')

html.write('<table>\n')
html.write('<tr><th scope="col" rowspan="2">Feature Flag</th>')
html.write('<th scole="col" rowspan="2">Read-Only<br />Compatible</th>')

for name, vers in header:
    html.write('<th scope="col" colspan="' + str(len(vers)) + '">'
               + name + '</th>')
html.write('</tr>\n<tr>')
for _, vers in header:
    for ver in vers:
        html.write('<td>' + ver + '</td>')
html.write('</tr>\n')

for (feature, domain), names in sorted(features.items()):
    guid = domain + ':' + feature
    html.write(f'<tr><th scope="row"><span class="l">{domain}:</span><span class="r">{feature}</span></th>')
    if readonly[guid]:
        html.write('<td class="yes">yes</td>')
    else:
        html.write('<td class="warn">no</td>')
    for name, vers in header:
        for ver in vers:
            if (name, ver) in names:
                html.write('<td class="yes">yes</td>')
            else:
                html.write('<td class="no">no</td>')
    html.write('</tr>\n')
html.write('</table>\n')

now = datetime.now().isoformat() + 'Z'
html.write('<p>This works by parsing manpages for feature flags, and is entirely dependent on good, accurate documentation.<br />Last updated on ' + now + ' using <a href="zfs.py">zfs.py</a>.</p>\n')

html.close()
