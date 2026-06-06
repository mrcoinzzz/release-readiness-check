# Release Readiness Check

A small command line tool for maintainers who want a quick local check before publishing an open-source release.

It looks for the signals that make a release easier to trust, review, and consume: version metadata, release notes, CI, license, security policy, and packaging files.

## Checks

- Version metadata in common package files
- Changelog or release notes
- License file
- Security policy
- CI workflow
- README
- Test directory
- Package metadata
- Git repository presence
- Clean working tree, when Git is available

The tool does not need network access and can run in local repositories or CI.

## Install

```bash
python3 -m pip install -e .
```

## Usage

Check the current directory:

```bash
release-readiness-check
```

Check another repository:

```bash
release-readiness-check /path/to/project
```

Return JSON:

```bash
release-readiness-check /path/to/project --format json
```

Use in CI:

```bash
release-readiness-check . --min-score 80
```

## Why this exists

Small maintainers often publish releases while juggling fixes, documentation, support, and security concerns. This tool makes release readiness visible before the tag goes out.

## Roadmap

- Language-specific version extraction
- Markdown report output
- Git tag comparison
- GitHub Actions annotation support
- Configurable checks

## License

MIT
