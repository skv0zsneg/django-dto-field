# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- End-to-end coverage for `DTOField` ORM read and write paths, defaults, nullable values, and malformed DTO data.
- Add dependabot to CI.
- Matrix Python and Django supported versions for CI tests.

### Changed

- Refactor DTO serialization around a registry of DTO implementations for dictionaries and dataclasses.
- Validate schema-bound `DTOField` values before serializing them for database writes.
- Add contributing link to `README.md`.
- Add supported Python and Django versions to `README.md`.

### Fixed

- Respect Django `null` and `blank` validation rules in `DTOField`.

## [0.1.1-beta1] - 2026-07-08

### Added

- Migrate from `poetry` to `uv`. 
- `CONTRIBUTING.md` for new contributions.

## [0.1.0-beta1] - 2026-05-11

### Added

- Add benchmarks `JSONField` vs `DTOField`, #26

## [0.1.0-alpha3] - 2026-05-03

### Added

- Add `dataclass` support, #29

### Changed

- Move `dto_code` checking to `BaseDtoFeature` class.
- Breaking: change `DtoField` naming to `DTOField` to be similar to `JSONField` naming.

### Removed

- Registry class because of it over-engineering propose.
- `TypedDict` support because of int not DTO nature, #28

## [0.1.0-alpha2] - 2026-04-05

### Changed

- Structure and naming, #23

### Added

- More unit tests during architecture changing.
- Binary DTO's now storing with TLV (Type-Length-Value).
- Global registry for serialization information storage.

## [0.1.0-alpha1] - 2026-01-26

### Added

- Serialization and deserialization dict field values, #13 #14
