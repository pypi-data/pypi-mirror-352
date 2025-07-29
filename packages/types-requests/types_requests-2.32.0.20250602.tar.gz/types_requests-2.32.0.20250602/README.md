## Typing stubs for requests

This is a [PEP 561](https://peps.python.org/pep-0561/)
type stub package for the [`requests`](https://github.com/psf/requests) package.
It can be used by type-checking tools like
[mypy](https://github.com/python/mypy/),
[pyright](https://github.com/microsoft/pyright),
[pytype](https://github.com/google/pytype/),
[Pyre](https://pyre-check.org/),
PyCharm, etc. to check code that uses `requests`. This version of
`types-requests` aims to provide accurate annotations for
`requests==2.32.*`.

Note: `types-requests` has required `urllib3>=2` since v2.31.0.7. If you need to install `types-requests` into an environment that must also have `urllib3<2` installed into it, you will have to use `types-requests<2.31.0.7`.

This package is part of the [typeshed project](https://github.com/python/typeshed).
All fixes for types and metadata should be contributed there.
See [the README](https://github.com/python/typeshed/blob/main/README.md)
for more details. The source for this package can be found in the
[`stubs/requests`](https://github.com/python/typeshed/tree/main/stubs/requests)
directory.

This package was tested with
mypy 1.16.0,
pyright 1.1.400,
and pytype 2024.10.11.
It was generated from typeshed commit
[`eb495ff1353a538a5021341b3c905c35a2284899`](https://github.com/python/typeshed/commit/eb495ff1353a538a5021341b3c905c35a2284899).