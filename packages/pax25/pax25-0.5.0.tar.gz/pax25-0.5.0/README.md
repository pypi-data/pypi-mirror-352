# PAX25

pax25 is intended to be a full AX.25 stack.

It implements V2 of the AX.25 stack (not 2.2-- so no MOD128, no SREJ, no XID)
Multiple interfaces (KISS/Serial, AX over IP, file) support.

Target Python is 3.13. Earlier versions of the 3.X branch will not work, but later versions will likely work.

## Documentation

[Documentation for Pax25](https://foxyfoxie.gitlab.io/pax25/) is built and published based on the contents of the `documentation` directory. It is based on [mkdocs](https://www.mkdocs.org/), the configuration for which is found in the repository root.
