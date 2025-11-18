## Test coverage best practices

- **Business Rule Protection**: Add unit/characterization tests for every meaningful business rule or bug fix before shipping
- **Critical Integrations**: Cover “must-not-fail” API endpoints with integration tests that execute the full stack (routing → data layer)
- **Happy + Guard Rail**: Each endpoint/component gets at least one happy-path test and one guard-rail (error/edge) test to prevent regressions
- **Contract Sync**: Keep contract tests aligned with the generated OpenAPI/Prisma clients so breaking changes surface immediately
- **External Dependencies**: Prefer real dockerized services in CI; only mock when the dependency is flaky or not available locally, and document the trade-off
- **Test Behavior, Not Implementation**: Focus tests on what the code does, not how it does it, to reduce brittleness
- **Clear Test Names**: Use descriptive names that explain what's being tested and the expected outcome
- **Fast Execution**: Keep unit tests fast (milliseconds) so developers run them frequently during development
