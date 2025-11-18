## General development conventions

- **Consistent Project Structure**: Organize files and directories in a predictable, logical structure that team members can navigate easily
- **Clear Documentation**: Maintain up-to-date README files with setup instructions, architecture overview, and contribution guidelines
- **Architecture Records**: Capture non-trivial trade-offs in lightweight ADRs stored in-repo so future work understands the context
- **Version Control Best Practices**: Use clear commit messages, feature branches, and meaningful pull/merge requests with descriptions
- **Workflow Templates**: Treat GitHub issue and PR templates as part of the contract—fill required sections and keep checklists up-to-date
- **Environment Configuration**: Use environment variables for configuration; never commit secrets or API keys to version control
- **Dependency Management**: Keep dependencies up-to-date and minimal; document why major dependencies are used
- **Code Review Process**: Establish a consistent code review process with clear expectations for reviewers and authors
- **Testing Requirements**: Define what level of testing is required before merging (unit tests, integration tests, etc.)
- **Feature Flags**: Use feature flags for incomplete features rather than long-lived feature branches
- **Flag Ownership**: Document how each feature flag maps to LaunchDarkly/ConfigCat (or equivalent) and who owns enabling/removal
- **Changelog Maintenance**: Keep a changelog or release notes to track significant changes and improvements
