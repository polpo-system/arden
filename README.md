# arden

The package tree of polpo, read by portia, polpo's package manager (as vipatsar is for
vipak and voc).

One directory per package in a category directory, `<category>/<name>/<name>-<version>.arden`,
in TOML:

- `[PACKAGE]`   name, category, version, author, license, description
- `[REMOTE]`    where the sources come from: type (git), uri, tag
- `[DEPS]`      packages needed, `name = version`
- `[PROVIDES]`  virtual packages provided, e.g. `display` by display-x11 and display-sixel
- `[CONFLICTS]` packages that cannot be installed together
- `[MODULES]`   Oberon sources in build order; `all` for every architecture, `x86`, `arm`,
                `riscv`, `mips`, `armv7` for the rest. The objects go to `obj/<arch>/`.
- `[FILES]`     other files: `all` or per architecture, `*` patterns allowed

`INDEX` lists the packages as `category/name version`. Package names are unique across the
tree; portia finds a package by name or by category/name.

Categories:

- `linux`   packages that produce Linux executables (core links `bin/<arch>/loksh`)
- `system`  the running system: console, desktop, displays, portia
- `devel`   compilers and development tools
- `apps`    applications and tools
- `lib`     libraries

The base system packages describe polpo itself and are generated from polpo's recipes by
`tools/genarden.py <arden directory>`.
