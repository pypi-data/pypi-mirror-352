# Lumeo Python PyPi package

[Package on PyPI](https://pypi.org/project/lumeo/)

## Development

Uses pyscaffold and tox to manage the project, so get 'em first.
```
pipx install tox pyscaffold
pipx inject pyscaffold pyscaffoldext-markdown
```

### Build
```
tox -e build
```

### Local test shell with lumeo package available
```
tox -e shell
``` 

### Run a script locally to test changes
```
pipx run --spec .[scripts] --no-cache lumeo-media-download --help
```

### Docs
Note: We haven't yet set up the docs to be published anywhere.
```
tox -e docs
```

## How to Make a Release

1. Make your changes in a separate branch and open a PR.

This will run the tests and python package build process

2. When the PR is approved and merged into main, a new release can be made.

Tag the commit with the new version number:
```
git tag -a v1.2.4 -m "Release version 1.2.4"
```

Push the tag to the repository:
```
git push origin v1.2.4
```

This will trigger the CI that will build and publish the new version to pypi.org.

