# Contributing

We welcome everyone to help us on this project.

All bug reports, feature requests and questions should be filed at the
[GitHub issues page](https://github.com/illuin-tech/opyoid/issues).

You can open your own Pull Request after discussing the need for those changes in an issue.

All pull requests should:
- Keep the code as clean as possible
- Pass all tests
- Pass the lint check
- Keep the coverage at 100%, with new unit tests for all changes
- Update the `CHANGELOG.md` file with the `Fixes`, `Features` and/or `Breaking changes` that the changes will bring

## Local development
Install the development dependencies with `pip install -r dev.requirements.txt`.

Run `python -m unitttest discover` to run the tests.

Run these commands to check the files linting:
```shell script
pylint --load-plugins pylint_quotes opyoid
pylint --load-plugins pylint_quotes tests tests_e2e \
  --disable=too-many-public-methods,no-self-use,too-many-instance-attributes
```
