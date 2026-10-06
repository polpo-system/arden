# arden

The package tree of polpo, read by portia, polpo's package manager (as vipatsar is for
vipak and voc).

One directory per package in a category directory, `<category>/<name>/<name>-<version>.arden`,
in TOML:

- `[PACKAGE]`   name, category, version, author, license, description
- `[REMOTE]`    where the sources come from: type, uri, tag. `type = "git"` is the base system
                (built from polpo itself, nothing to download); `type = "files"` is a remote
                package, whose files portia downloads from `uri/<path>` (https, http, gemini,
                spartan) into `src/pkg/<name>/`
- `[DEPS]`      packages needed, `name = version`
- `[PROVIDES]`  virtual packages provided, e.g. `display` by display-x11 and display-sixel
- `[CONFLICTS]` packages that cannot be installed together
- `[MODULES]`   Oberon sources in build order; `all` for every architecture, `x86`, `arm`,
                `riscv`, `mips`, `armv7` for the rest. The objects go to `obj/<arch>/`.
- `[FILES]`     other files: `all` or per architecture; `path=dest` installs a copy at `dest` in
                the polpo root (share/, tools/)
- `[SUMS]`      of a remote package: `"path" = "sha256:..."` (or md5) for every file; a file with
                another sum is refused. `portia.Sums name dir` prints them
- `[TESTS]`     Oberon commands run after building (`portia.Test`, `Install /t`): `copy` files to
                a new directory, `cmds` (`$compile` is the compiler of the architecture), `ok`
                lines expected in the output, `bad` texts refused; `display = true` for tests
                that need the desktop. `[TESTS.<arch>] cmds` run after the common ones

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

## The base system

The recipes of the base system (the packages built from polpo itself) are written by
`genarden.Run <arden dir>`, an Oberon command of polpo (package polpo-tools): it reads the
build recipes `tools/*.Tool` of polpo and `tools/base.toml` here, which says which package a
module belongs to, with the descriptions, dependencies and files of the packages. It also
writes the `INDEX`, from the recipes found in the tree. Run it after changing the build
recipes of polpo, then `portia.Check`. The recipes of remote packages are written by hand.

All the tools are Oberon commands; nothing here needs another language.
