#!/usr/bin/env python3
# usage: tools/genarden.py <arden directory>; regenerate after changing polpo's tools/*.Tool, then portia.Check
# generate arden package descriptions for the polpo base system from the build recipes
import os, re, sys, collections, subprocess

POLPO = '/home/noch/src/mine/polpo-related/polpo'
OUT = sys.argv[1]
RECIPES = [('build', 'x86'), ('arm-cross', 'x86'), ('rop2-cross', 'x86'),
           ('arm', 'arm'), ('riscv', 'riscv'), ('mips', 'mips'), ('armv7', 'armv7')]
ARCHS = ['x86', 'arm', 'riscv', 'mips', 'armv7']

def package(path):
    b = os.path.basename(path)[:-4]           # without .Mod
    d = os.path.dirname(path)
    core = {'Linux0', 'Kernel', 'Root', 'Reals', 'POLPO.Files', 'Modules0', 'loksh'}
    console = {'out', 'Modules', 'Objects0', 'objects', 'strings', 'regex', 'Utf8', 'Texts0',
               'RXA', 'Oberon0', 'texts', 'oberon', 'in', 'termios', 'system', 'POLPO.FATFiles',
               'shell', 'cat'}
    if b in core: return 'core'
    if b in console and d in ('src/cli', 'src/common') or b == 'system': return 'console'
    if b == 'xxs': return 'xxs'
    if b == 'TOML': return 'toml'
    if b == 'Versions': return 'versions'
    if b == 'portia': return 'portia'
    if b == 'Checksums': return 'checksums'
    if b == 'Sockets': return 'sockets'
    if b == 'DNS': return 'dns'
    if d == 'src/lib/ooc': return 'ooc'
    if d == 'src/lib/strutils': return 'strutils'
    if b == 'Base64': return 'base64'
    if b == 'Internet': return 'internet'
    if d == 'src/lib/http': return 'http'
    if d == 'src/lib/tls': return 'tls'
    if b == 'fetch': return 'fetch'
    if b == 'gemini': return 'gemini'
    if b == 'spartan': return 'spartan'
    if b == 'net': return 'net'
    if b in ('bdffont', 'grep', 'rx'): return 'console-tools'
    if d == 'src/cli/x86': return 'compiler-x86'
    if d == 'src/cli/arm': return 'compiler-arm'
    if d == 'src/cli/rop2': return 'compiler-rop2'
    if d == 'src/cli/riscv': return 'compiler-riscv'
    if d == 'src/cli/mips': return 'compiler-mips'
    if d == 'src/cli/armv7': return 'compiler-armv7'
    if b in ('POLPO.Objects', 'POLPO.FileDir'): return 'desktop-base'
    if b in ('POLPO.Display', 'POLPO.Input'): return 'display-x11'
    if b in ('POLPO.SXL.Display', 'POLPO.SXL.Input'): return 'display-sixel'
    if b in ('Edit', 'Styles', 'ScriptFrames', 'Script', 'Dates', 'Strings', 'POLPO.Compiler',
             'POLPO.FileTools'): return 'desktop-tools'
    if d == 'src/desktop/x86': return 'desktop-compiler-x86'
    if d == 'src/desktop/arm': return 'desktop-compiler-arm'
    if d in ('src/desktop/rop2', 'src/desktop/riscv', 'src/desktop/mips', 'src/desktop/armv7'):
        return 'desktop-system' if b == 'POLPO.System' else 'desktop-compiler-rop2'
    if b == 'POLPO.System': return 'desktop-system'
    if d == 'src/desktop': return 'desktop'
    raise SystemExit('no package for ' + path)

mods = collections.defaultdict(lambda: collections.OrderedDict())  # pkg -> path -> set(archs)
xflag = set()  # (path, arch) compiled with /x
links = {}     # arch -> link command
for recipe, arch in RECIPES:
    for line in open(os.path.join(POLPO, 'tools', recipe + '.Tool'), errors='replace'):
        m = re.search(r'(src/\S+\.Mod)', line)
        if m and 'Compile' in line:
            p = m.group(1)
            mods[package(p)].setdefault(p, set()).add(arch)
            if ' /x ' in ' ' + line + ' ': xflag.add((p, arch))
        elif re.match(r'\s*[a-z]*linker\.Link ', line) and recipe in ('build', 'arm', 'riscv', 'mips', 'armv7'):
            links[arch] = line.strip()
# the sixel variant is not in the recipes (make sixel): all architectures
for p in ('src/desktop/POLPO.SXL.Display.Mod', 'src/desktop/POLPO.SXL.Input.Mod'):
    mods['display-sixel'][p] = set(ARCHS)
for arch in ARCHS: xflag.add(('src/desktop/POLPO.SXL.Display.Mod', arch))  # make sixel: /x

INFO = {
 'core': ('the boot image: runtime, files, module loader and the loksh binary', []),
 'console': ('the console: shell, texts, terminal, Oberon.Text', ['core']),
 'console-tools': ('grep, rx (regular expressions), bdffont', ['console']),
 'xxs': ('a nano-like console editor for plain files and Oberon texts', ['console']),
 'compiler-x86': ('the x86 OP2 compiler, linker and browser', ['console']),
 'compiler-arm': ('the ARM OB compiler and linkers (native on ARM, cross on x86)', ['console']),
 'compiler-rop2': ('the ROP2 compiler front end and boot linker', ['console']),
 'compiler-riscv': ('the RISC-V back end of ROP2', ['compiler-rop2']),
 'compiler-mips': ('the MIPS back end of ROP2', ['compiler-rop2']),
 'compiler-armv7': ('the ARMv7 back end of ROP2', ['compiler-rop2']),
 'desktop-base': ('objects and the file directory, below the display', ['console']),
 'desktop': ('the Oberon desktop: display space, fonts, texts, viewers', ['desktop-base', 'display']),
 'desktop-system': ('the System module of the desktop', ['desktop']),
 'display-x11': ('Display and Input for X11', ['desktop-base']),
 'display-sixel': ('Display and Input for xterm (sixel)', ['desktop-base']),
 'desktop-tools': ('Edit, Script, Styles and other desktop tools', ['desktop-system']),
 'desktop-compiler-x86': ('the x86 compiler, boot linker, decoder and browser in the desktop', ['desktop-tools', 'compiler-x86']),
 'desktop-compiler-arm': ('the ARM compiler, decoder and browser in the desktop', ['desktop-tools', 'compiler-arm']),
 'desktop-compiler-rop2': ('the ROP2 compilers and decoders in the desktop', ['desktop-tools', 'compiler-rop2']),
 'toml': ('a small TOML reader, from github.com/norayr/toml', []),
 'versions': ('comparing version numbers like 1.2.10 and 0.3.0-rc1', []),
 'checksums': ('MD5 and SHA-256 of data and files', ['core']),
 'portia': ('portia, the package manager', ['console', 'toml', 'versions', 'checksums']),
 'sockets': ('TCP and UDP over IPv4 and IPv6', ['core']),
 'dns': ('host names to addresses: /etc/hosts and DNS over UDP, A and AAAA', ['core', 'sockets']),
 'ooc': ('oocIntStr and what it needs from the OOC library (as in voc)', []),
 'strutils': ('strTypes and strUtils, string helpers shared with voc', ['console']),
 'base64': ('Base64 encoding and decoding, shared with voc', ['console']),
 'internet': ('TCP by host name and port, the Internet interface of voc', ['console', 'sockets', 'dns']),
 'http': ('an HTTP/1.1 client, shared with voc', ['console', 'ooc', 'strutils', 'base64', 'internet']),
 'tls': ('TLS 1.3 in Oberon (AES-128-GCM, X25519 and P-256, RSA and ECDSA chains) and https over http, shared with voc', ['console', 'sockets', 'internet', 'http', 'strutils']),
 'fetch': ('fetch.Get and fetch.Show: HTTP and HTTPS downloads', ['console', 'http', 'tls']),
 'gemini': ('gemini.Get and gemini.Show: Gemini downloads, keys trusted on first use', ['console', 'tls']),
 'spartan': ('spartan.Get and spartan.Show: Spartan downloads', ['console', 'internet']),
 'net': ('minimal network tools: Get, Send, Echo, UDP, Lookup, Resolve, Address', ['console', 'sockets', 'dns']),
}
FILES = {
 'core': {'x86': 'bin/x86/loksh', 'arm': 'bin/arm/loksh', 'riscv': 'bin/riscv/loksh',
          'mips': 'bin/mips/loksh', 'armv7': 'bin/armv7/loksh'},
 'console': {'all': 'Oberon.Text texts.md'},
 'compiler-x86': {'all': 'tools/build.Tool'},
 'compiler-arm': {'all': 'tools/arm.Tool tools/arm-cross.Tool'},
 'compiler-rop2': {'all': 'tools/rop2-cross.Tool'},
 'compiler-riscv': {'all': 'tools/riscv.Tool'},
 'compiler-mips': {'all': 'tools/mips.Tool'},
 'compiler-armv7': {'all': 'tools/armv7.Tool'},
 'desktop': {'all': 'share/* fonts/* texts/*'},
 'desktop-tools': {'all': 'tools/System.Tool tools/Edit.Tool tools/Script.Tool'},
 'console-tools': {'all': 'tools/rx.Tool'},
}
CATEGORY = {  # linux: produces Linux executables; system; devel: compilers; apps; lib
 'core': 'linux',
 'console': 'system', 'desktop-base': 'system', 'desktop': 'system', 'desktop-system': 'system',
 'display-x11': 'system', 'display-sixel': 'system', 'portia': 'system',
 'toml': 'lib', 'versions': 'lib', 'sockets': 'lib', 'dns': 'lib', 'net': 'apps',
 'ooc': 'lib', 'strutils': 'lib', 'base64': 'lib', 'internet': 'lib', 'http': 'lib', 'tls': 'lib', 'fetch': 'apps', 'gemini': 'apps', 'spartan': 'apps', 'checksums': 'lib',
 'compiler-x86': 'devel', 'compiler-arm': 'devel', 'compiler-rop2': 'devel', 'compiler-riscv': 'devel',
 'compiler-mips': 'devel', 'compiler-armv7': 'devel', 'desktop-compiler-x86': 'devel',
 'desktop-compiler-arm': 'devel', 'desktop-compiler-rop2': 'devel',
 'xxs': 'apps', 'console-tools': 'apps', 'desktop-tools': 'apps',
}
LICENSE = {'toml': 'GPL-3', 'ooc': 'LGPL-2+', 'strutils': 'GPL-3'}  # others: the license of polpo
PROVIDES = {'display-x11': ('display', 'display-sixel'), 'display-sixel': ('display', 'display-x11')}
# packages whose sources are in another repository ([REMOTE] type = files): their recipes
# are written by hand and only listed in the INDEX here
EXTERNAL = [('devel', 'coco', '0.1.0'), ('devel', 'coco-eth', '0.1.0')]

def q(x):  # a TOML basic string
    return '"' + x.replace('\\', '\\\\').replace('"', '\\"') + '"'

def arr(items):  # a TOML array, one element a line when it is long
    one = '[' + ', '.join(q(x) for x in items) + ']'
    if len(one) <= 80: return one
    return '[\n' + ''.join('  %s,\n' % q(x) for x in items) + ']'

os.makedirs(OUT, exist_ok=True)
index = []
for pkg in INFO:
    desc, deps = INFO[pkg]
    cat = CATEGORY[pkg]
    d = os.path.join(OUT, cat, pkg); os.makedirs(d, exist_ok=True)
    f = open(os.path.join(d, pkg + '-0.1.0.arden'), 'w')
    f.write('[PACKAGE]\nname        = %s\ncategory    = %s\nversion     = "0.1.0"\nauthor      = %s\nlicense     = %s\n'
            % (q(pkg), q(cat), q('noch' if pkg == 'toml' else 'polpo'), q(LICENSE.get(pkg, 'ETH Oberon'))))
    f.write('description = %s\n\n' % q(desc))
    f.write('[REMOTE]\ntype = "git"\nuri  = "https://raw.githubusercontent.com/polpo-system/polpo/main"\ntag  = "main"\n\n')
    f.write('[DEPS]\n')
    for dep in deps: f.write('%s = "0.1.0"\n' % dep)
    if pkg in PROVIDES:
        f.write('\n[PROVIDES]\n%s = "0.1.0"\n\n[CONFLICTS]\n%s = "0.1.0"\n' % PROVIDES[pkg])
    # modules, in build order: common ones under all, the rest per architecture
    f.write('\n[MODULES]\n')
    def tok(p, archs):  # "/x path" when every one of archs compiles it with /x
        return ('/x ' + p) if all((p, a) in xflag for a in archs) else p
    allm = [tok(p, ARCHS) for p, a in mods[pkg].items() if a == set(ARCHS)]
    if allm: f.write('all = %s\n' % arr(allm))
    for arch in ARCHS:
        m = [tok(p, [arch]) for p, a in mods[pkg].items() if arch in a and a != set(ARCHS)]
        if m: f.write('%s = %s\n' % (arch, arr(m)))
    if pkg == 'core':  # link the boot image, then move it in place
        f.write('\n[BUILD]\n')
        for arch in ARCHS:
            cmd = links[arch]
            new = re.search(r'(bin/\S+?)(\.new|2)?(\s|$)', cmd)
            f.write('%s = %s\n' % (arch, arr([cmd, 'mv %s bin/%s/loksh' % (new.group(1) + (new.group(2) or ''), arch)])))
    if pkg in FILES:
        f.write('\n[FILES]\n')
        for k, v in FILES[pkg].items():
            out = []
            for w in v.split():
                if w.endswith('/*'):  # expanded: portia does not list directories yet
                    out += subprocess.run(['git', '-C', POLPO, 'ls-files', w[:-2]], capture_output=True, text=True).stdout.split()
                else:
                    out.append(w)
            f.write('%s = %s\n' % (k, arr(out)))
    f.close()
    index.append('%s/%s 0.1.0' % (cat, pkg))
for cat, pkg, ver in EXTERNAL:
    if not os.path.exists(os.path.join(OUT, cat, pkg, '%s-%s.arden' % (pkg, ver))):
        raise SystemExit('no recipe %s/%s/%s-%s.arden' % (cat, pkg, pkg, ver))
    index.append('%s/%s %s' % (cat, pkg, ver))
open(os.path.join(OUT, 'INDEX'), 'w').write('\n'.join(index) + '\n')
print('\n'.join(index))
