# Release Note

## v0.1.0 

### Highlights
- Initial release of the project.
- Added core functionality for interacting with Elasticsearch indices.

### Core
- Implemented `search` command to query Elasticsearch indices.
- Added `check` command to filter commit IDs based on existing records in Elasticsearch.
- Introduced `delete` command to remove specific documents by ID from Elasticsearch.
- Added support for filtering results by specific fields using the `--filter` option in the `search` command.

### Other
- Added basic logging functionality for better debugging and monitoring.
- Included `CONTRIBUTING.md` to guide contributors.
- Added `pytest` support for running unit tests.
- Improved documentation for all commands and usage examples.

## v0.1.1 

### bugfix
- Fixed keyring no recommended backend was available bug.
- Fixed tag subfix, set main branch as default tag and exclude it.
- Fixed '/' bug, es field can not include it, remove it from model name.