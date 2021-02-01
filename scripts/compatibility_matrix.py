#!/usr/bin/env python3

# License: CC0 https://creativecommons.org/share-your-work/public-domain/cc0/

# Generate cross-OS ZFS features matrix support by parsing man pages.

import logging
import sys

from collections import defaultdict
from urllib.error import HTTPError
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


def openzfs():
    sources = {'master': 'https://raw.githubusercontent.com/openzfs/zfs/'
               'master/man/man5/zpool-features.5'}
    # TODO(gmelikov): use git tags from OpenZFS repo
    with urlopen('https://zfsonlinux.org') as web:
        versions = findall(r'download/zfs-([0-9.]+)',
                           web.read().decode('utf-8', 'ignore'))
    versions.append("0.6.5.11")
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


def freebsd_pre_openzfs():
    # TODO(gmelikov): add FreeBSD HEAD (OpenZFS version)?
    #   There could be some lag between OpenZFS upstream and the FreeBSD,
    #   or even Linux implementations.
    sources = {}
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


def nexenta():
    sources = {'master': 'https://raw.githubusercontent.com/Nexenta/'
               'illumos-nexenta/master/usr/src/man/man5/zpool-features.5'}
    with urlopen('https://github.com/Nexenta/illumos-nexenta') as web:
        versions = findall(r'>release-([0-9.]+)</span>',
                           web.read().decode('utf-8', 'ignore'))
    versions.sort()
    versions = versions[-2:]
    versions.append("4.0.5-FP")
    for ver in versions:
        sources[ver] = ('https://raw.githubusercontent.com/Nexenta/illumos-'
                        'nexenta/release-{}/usr/src/man/man5/'
                        'zpool-features.5'.format(ver))
    return sources


openzfs_key = 'OpenZFS (Linux, FreeBSD 13+)'
sources = {
        openzfs_key: openzfs(),
        'FreeBSD pre OpenZFS': freebsd_pre_openzfs(),
        'OpenZFS on OS X': openzfsonosx(),
        'OmniOS CE': omniosce(),
        'Joyent': joyent(),
        'NetBSD': netbsd(),
        'Nexenta': nexenta(),
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
    found = {}
    LOG.debug('Work on %s...', name)
    for ver, url in sub.items():
        LOG.debug('Get %s...', url)
        try:
            with urlopen(url) as c:
                if c.getcode() != 200:
                    LOG.debug('Failed with HTTP code %d', c.getcode())
                    continue
                man = c.read().decode('utf-8')
        except HTTPError:
            LOG.debug('Failed with HTTPError')
            continue
        found[ver] = url
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
                elif guid == 'com.nexenta:cos_properties':
                    # This is wrong in the documentation.  The actual code in
                    # zfeature_common.c uses this name:
                    guid = 'com.nexenta:class_of_storage'
                domain, feature = guid.split(':', 1)
                features[(feature, domain)].append((name, ver))
            elif line.startswith('READ\\-ONLY COMPATIBLE'):
                readonly[guid] = (line.split()[-1] == 'yes')
        # This is missing in the documentation, but is supported by the code:
        # https://github.com/Nexenta/illumos-nexenta/blob/release-4.0.4-FP/usr/src/common/zfs/zfeature_common.c
        if name == 'Nexenta' and ver.startswith('4.'):
            features[('meta_devices', 'com.nexenta')].append((name, ver))
    sources[name] = found

os_sources = sources.copy()
os_sources.pop(openzfs_key)
header = list(sorted(os_sources.keys()))
header.insert(0, openzfs_key)
header = list(zip(header, (sorted(sources[name],
              key=lambda x: regex(r'[^0-9]', '', x) or x) for name in header)))

html = open(path + '/zfs_feature_matrix.html', 'w')

f_len, d_len = zip(*features.keys())
f_len, d_len = max(map(len, f_len)), max(map(len, d_len)) + 1

html.write('''<!DOCTYPE html>
<title>ZFS Feature Matrix</title>
<meta charset="utf-8" /><meta name="referrer" content="never" />
<link rel='shortcut icon' href='/favicon.ico' type='image/x-icon'>
<style>
body {
  font-family: "Helvetica", "Arial", sans-serif;
}
.yes {
  background-color: lightgreen;
}
.warn {
  background-color: yellow;
}
.no {
  background-color: lightsalmon;
}
abbr {
  text-decoration: none;
}
table {
  border-collapse: collapse;
  display: block;
  overflow-x: scroll;
  overflow-y: hidden;
}
.name {
  max-width: 19ch;
}
th,td {
  padding: 0.2em 0.4em;
  border: 1px solid #aaa;
  background-color: #f9f9f9;
}
.line:hover {
  filter: brightness(115%);
}
th {
  background-color: #eaecf0;
}
.l {
  display: inline-block;
  text-align: right;
  min-width: ''' + str(d_len) + '''ex;
  color: #777;
}
.r {
  display: inline-block;
  text-align: left;
  min-width: ''' + str(f_len) + '''ex;
}
.feature_col {
  min-width: ''' + str(f_len + d_len + 1) + '''ch;
}
.rotate {
  text-align: center;
  vertical-align: middle;
}
.rotate span {
  writing-mode: vertical-rl;
  -webkit-writing-mode: vertical-rl;
  transform: scale(-1);
}
.rocol {
  min-width: 3em;
}
</style>
''')

html.write('<table>\n')
html.write('<tr><th scope="col" class="feature_col" rowspan="2">Feature Flag</th>')
html.write('<th class="rotate rocol" scole="col" rowspan="2"><span>Read-Only<br />Compatible</span></th>')

for name, vers in header:
    html.write('<th class="name" scope="col" colspan="' + str(len(vers)) + '">'
               + name + '</th>')
html.write('</tr>\n<tr>')
for _, vers in header:
    for ver in vers:
        html.write('<td class="rotate"><span>' + ver + '</span></td>')
html.write('</tr>\n')

for (feature, domain), names in sorted(features.items()):
    guid = domain + ':' + feature
    html.write(f'<tr class="line"><th scope="row"><span class="l">{domain}:</span><span class="r">{feature}</span></th>')
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
html.write('<p>Table generates by parsing manpages for feature flags, and is entirely dependent on good, accurate documentation.<br />Last updated on ' + now + ' using <a href="https://github.com/openzfs/openzfs-docs/tree/master/scripts/compatibility_matrix.py">compatibility_matrix.py</a>.</p>\n')

html.close()
