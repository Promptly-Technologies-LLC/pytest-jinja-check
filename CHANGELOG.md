# CHANGELOG

<!-- version list -->

## v1.1.0 (2026-06-23)

### Features

- Add opt-in automatic template lint at pytest session start
  ([`8dcfda4`](https://github.com/Promptly-Technologies-LLC/pytest-jinja-check/commit/8dcfda41a380c2cd0dc05b563284e1185fac5675))


## v1.0.2 (2026-03-14)

### Bug Fixes

- Subtract set variables from undeclared variables for all templates
  ([`e8418ad`](https://github.com/Promptly-Technologies-LLC/pytest-jinja-check/commit/e8418ad337f72ee31f8d34362ed553ebaad048a9))


## v1.0.1 (2026-03-14)

### Bug Fixes

- Exclude macro imports and set variables from undeclared variables check
  ([#5](https://github.com/Promptly-Technologies-LLC/pytest-jinja-check/pull/5),
  [`3e523a9`](https://github.com/Promptly-Technologies-LLC/pytest-jinja-check/commit/3e523a9a5b907036360fa48647fdaa3cc1b2c62f))

- Exclude macro imports from undeclared variables check
  ([#5](https://github.com/Promptly-Technologies-LLC/pytest-jinja-check/pull/5),
  [`3e523a9`](https://github.com/Promptly-Technologies-LLC/pytest-jinja-check/commit/3e523a9a5b907036360fa48647fdaa3cc1b2c62f))

- Exclude {% set %} variables from parent's undeclared variables during inheritance
  ([#5](https://github.com/Promptly-Technologies-LLC/pytest-jinja-check/pull/5),
  [`3e523a9`](https://github.com/Promptly-Technologies-LLC/pytest-jinja-check/commit/3e523a9a5b907036360fa48647fdaa3cc1b2c62f))


## v1.0.0 (2026-03-14)

- Initial Release
