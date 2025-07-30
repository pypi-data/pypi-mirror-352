# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.9.3] - 2025-06-03

### Removed

- Removed unique scenario names for `run-remote` jobs as no longer required by dashboard

## [0.9.2] - 2025-05-27

### Added

- Deeper and tentatively complete localisation of the CLI framework (#262)
- ROS tests can be recorded as "error" rather than just fail or success (#267)

### Fixed

- Compliance with the Artefacts API protocol on reporting common scenario names
  across parameterised runs.

## [0.9.1] - 2025-04-30

### Added

- Runs in container accept and pass options to the underlying container engine (#246)
- Internationalisation of command output and Japanese support (#139)

### Fixed

- Compliance with the Artefacts API protocol on upload/no-upload option (#217)

## [0.8.0] - 2025-04-04

### Added

- Run in containers with only an artefacts.yaml configuration file. No need to
  write a Dockerfile in many standard situations.

### Changed

- New logging messages and format.

### Fixed

- Logging correctly filters between logs for stderr and stdout
- Client now correctly handles rosbags not saved to the top level of a project.
- Fixed error formatting of test error(s).

## [0.7.3] - 2025-03-26

### Fixed

- Handle nested ROS params in the configuration file.

## [0.7.2] - 2025-03-19

### Fixed

- Fixed error handling (bug from misuse of Click's `ClickException`).

### Changed

- Improved error handling and messages.


## [0.7.1] - 2025-03-14

### Added

- Partial CHANGELOG with information on the day we start SemVer and the current
  0.7.0. More detail to come inbetween, but we will focus on the future.

### Changed

- Replace Ruff shield for the original Black one.


## [0.7.0] - 2025-02-25

### Added

- Default upload directory to automatically include output from the Artefacts
  toolkit.

### Changed

- Always rebuild container images before run. These incremental rebuilds avoid
  existing confusion when running an updated code base without rebuilding.
- Separate CD workflow from PyPi publication testing: For reusability and
  direct invocation.


## [0.5.8] - 2024-08-19

### Added

- Beginning of semantic versioning.
- Local metrics errors do not block publication of results.
- Introduction of Black formatting. 

[unreleased]: https://github.com/art-e-fact/artefacts-client/compare/0.9.2...HEAD
[0.9.2]: https://github.com/art-e-fact/artefacts-client/releases/tag/0.9.2
[0.9.1]: https://github.com/art-e-fact/artefacts-client/releases/tag/0.9.1
[0.8.0]: https://github.com/art-e-fact/artefacts-client/releases/tag/0.8.0
[0.7.0]: https://github.com/art-e-fact/artefacts-client/releases/tag/0.7.0
[0.5.8]: https://github.com/art-e-fact/artefacts-client/releases/tag/0.5.8
