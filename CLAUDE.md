# CLAUDE.md

Guidance for Claude Code in this repository. Keep it under 200 lines and do not
repeat what README, `docs/` or the ADRs say: link to them.

## What this is

`ingot-mail`: an addon of [Ingots](https://github.com/ak-ingots/ingots) for
the mail of its applications: its API is that of the mail, assuming nothing
of the addons that use it.
A library (ADR 0003), Python >= 3.14, part of the
[ak-ingots](https://github.com/ak-ingots) ecosystem; the meta repository
`ingots-libs` holds the ecosystem-wide decisions in `docs/adr/`.

## Layout

- `project.py`: `MailProject`, with `MailSettingsUnit` (`settings/`, the
  configs `MAIL_*` in `settings/configs.py`, of every backend) and
  `MailLoggingUnit` (`logging/`, the logger `ingot_mail`).
- `mail/`: `MailUnit`, the mail of the project: `Mail` in `data.py`, the
  errors in `errors.py`, `BaseMailer` in `mailers.py`, the facade of the slot
  `mailer`, abstract, its final `send()` refusing a header unfit before the
  backend, the sender of the mail or `MAIL_FROM` by `_get_sender(mail)`.
- `contrib/<backend>/`: `memory/`; `aiosmtplib/`, a connection a mail, its
  errors wrapped in `MailDeliveryError`, transient by the reply.
- `testing/contracts/`: `MailerContract`, run on every backend (ADR 0005).
- `tests/test_readme.py` runs the README for consumers; `python -m
  ingot_mail` runs the addon on its own (prefix `INGOT`), the mailer in
  memory.

## Commands

Everything goes through `make` (run `make` alone for the target list); uv
provides the environments and interpreters.

```bash
make check        # what CI runs: lint, test, coverage, wheel-test, integration, cl-check
make lint         # black --check, flake8, mypy --strict
make test         # unittest on the working tree
make integration  # the mailer of SMTP against docker-compose.yml, two Mailpits
make coverage     # the same under coverage; fails below 99%
make wheel-test   # unittest on the built wheel, PYTHONS="3.14 3.15"
make format       # black
```

One test: `uv run python -m unittest tests.test_canary.CanaryTestCase`.

## Commits and GitHub

- Never commit, amend, push, open a pull request, tag or rewrite history on
  your own initiative: show a summary and the proposed message, wait for an
  explicit approval of that commit. One approval does not extend to the
  next. Never merge a pull request: the user does (`gh pr merge` is denied).
- The remote is `ak-ingots/ingot-mail`. Inside the `ingots-libs`
  checkout, run gh and git network commands as
  `direnv exec /home/bee/work/ingots-libs <cmd>` (the token comes from its
  `.envrc`; never read it).
- `main` and `release/X.Y` are protected by a ruleset: no direct push, force
  push or deletion; pull requests only, squash-merged, with every CI job
  green on a branch up to date with `main`. One change per branch and PR,
  kept to one commit; the squash commit takes the PR title and description,
  so write them as the commit message. The `Co-Authored-By` trailer goes in
  the branch commit only: GitHub carries it to the end of the squash commit.
- Before pushing a branch, rebase it onto the current `main` and run
  `make check`. After the user merges, switch to `main`, pull and delete the
  local branch.
- A release: a pull request sets the version (`uv version X.Y.Z`) and
  collates the changelog (`make cl-build VERSION=X.Y.Z`); after the merge,
  the tag `vX.Y.Z` on its commit starts the `release` workflow, which
  publishes to TestPyPI, tests the package installed from it (the shared
  workflow `index-test`), then publishes to PyPI once the user approves the
  `pypi` environment. Run by hand, the workflow rehearses on TestPyPI only.

## Rules

- Every change users should know about adds a fragment to `changelog.d/`
  (`<issue>.<type>.md` or `+<slug>.<type>.md`, see `changelog.d/README.md`);
  `cl-check` fails CI without one.
- The version is static in `pyproject.toml` (`uv_build`, no setuptools-scm);
  it changes only at release time.
- Versions start at 0.1.0: the name holds no older release; a version is
  published only once.
- `ingots` is pinned to a minor version: before 1.0 a minor
  version of the framework may break its addons. Moving on to the next one
  is a change of its own, with a news fragment.
- Flat layout: the package is `ingot_mail/` at the root. The wheel must be
  complete: `make wheel-test` imports the package only from the wheel.
- Tests are stdlib `unittest`, no pytest. Code passes `mypy --strict` with
  `explicit-override`: every override takes `@t.override`; black at 88
  columns.
- The supported interpreters are listed in three places with nothing linking
  them: `PYTHONS` in the Makefile, the classifiers and the `wheel` matrix in
  `.github/workflows/ci.yml`. Change them together.
- CI runs exactly the `make` targets; a new check goes into `make check` and
  `ci.yml` together.
- A comment tells what the code cannot: why it is so, a constraint from
  outside (a bug of a library, a standard, a measure), a trap for the next
  change. None repeats the code, a name, a docstring or what a key of a
  config says, nor tells the history of a change: that is the commit's.
  Reading it, one thinks "ah, so that's it"; a comment that gives no such
  moment states the obvious and goes.
- A TODO names its issue of GitHub, `# TODO(#42): ...`, of another
  repository `# TODO(ak-ingots/ingots#42): ...`: one without an issue is
  never done. No issue, no TODO: do it now, or open the issue first.
- A type is narrowed by an annotation in the class, not by `t.cast` at
  each use: an entity its project or parent, `project: "AuthProject"`,
  `parent: AuthProofsOwner`, a mixin too, a mixin of two projects naming a
  type of both; an error its `args`, `args: tuple[str, int]`. `t.cast`
  stays where no class can carry the type: a function whose parameter
  cannot be narrowed, a value from a library or from outside.
- Code layout and naming follow ADR 0007; the PUER rules of `ingots` apply to
  an addon too: hooks start with an underscore and are overridden, not
  called; a protected member is touched only by its class, its subclasses
  and its own package.

Of this package:

- A unit lives in the `__init__.py` of its package, as in `ingots.defaults`.
  A unit, the configs and the errors take the prefix `Mail`, where the name
  of a class of the mail tells it already: `Mail`, `BaseMailer`,
  `MemoryMailer`.
- A backend is under its own extra, named after its library, when it needs
  more than the core; a contrib gives the class of the slot it fills, the
  application composes.

## Design

An addon extends the framework through slots and subclassing (ADR 0004) and
ships contract tests that its consumers run (ADR 0005); design principles in
ADR 0006. The settings it extends are documented in `ingots`:
`docs/defaults/settings.md` and `docs/defaults/addon.md`.
The design of the addon is `docs/design/mail/` of the meta repository.
