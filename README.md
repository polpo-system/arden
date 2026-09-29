# arden

The package tree of polpo, read by portia, polpo's package manager (as vipatsar is for
vipak and voc).

One directory per package, `<name>/<name>-<version>.arden`, in the TOML format of vipatsar
with polpo's additions:

- `[PACKAGE]`   name, version, author, license, description
- `[REMOTE]`    where the sources come from: type (git), uri, tag
- `[DEPS]`      packages needed, `name = version`
- `[PROVIDES]`  virtual packages provided, e.g. `display` by display-x11 and display-sixel
- `[CONFLICTS]` packages that cannot be installed together
- `[MODULES]`   Oberon sources in build order; `all` for every architecture, `x86`, `arm`,
                `riscv`, `mips`, `armv7` for the rest. The objects go to `obj/<arch>/`.
- `[FILES]`     other files: `all` or per architecture, `*` patterns allowed

`INDEX` lists the packages. The base system packages describe polpo itself.
