## Development and Releases

This section is intended for maintainers of the project.

### Releasing a New Version

To release a new version of OAT Tools, follow these steps:

1. **Implement or modify features and tests**
   - Make your changes to the codebase
   - Add or update corresponding tests
   - Ensure your code follows the project's coding standards

2. **Run tests to ensure everything works**
   ```bash
   uv run pytest
   ```
   Make sure all tests pass before proceeding.

3. **Update the version number**
   - Edit `pyproject.toml` and increment the version number in the `[project]` section
   - Follow [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`
     - **PATCH**: Bug fixes and small improvements
     - **MINOR**: New features that are backwards compatible
     - **MAJOR**: Breaking changes

4. **Commit and push your changes**
   ```bash
   git add .
   git commit -m "Release version X.Y.Z"
   git push origin main
   ```

5. **Create and push a version tag**
   ```bash
   # Create a tag (replace X.Y.Z with your version number)
   git tag vX.Y.Z
   
   # Push the tag to trigger the release workflow
   git push origin vX.Y.Z
   ```

6. **Monitor the release**
   - The GitHub Actions workflow will automatically build and publish the package to PyPI
   - Check the [Actions tab](../../actions) in GitHub to ensure the release completed successfully
   - Verify the new version appears on [PyPI](https://pypi.org/project/oat-tools/)

### Example Release Commands

Here's a complete example for releasing version 1.0.1:

```bash
# After making your changes and updating pyproject.toml version to "1.0.1"
uv run pytest                    # Ensure tests pass
git add .
git commit -m "Release version 1.0.1"
git push origin main
git tag v1.0.1
git push origin v1.0.1
```

The automated workflow will handle the rest!