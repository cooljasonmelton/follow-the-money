## Database migration best practices

- **Reversible Migrations**: Always implement rollback/down methods to enable safe migration reversals
- **Small, Focused Changes**: Keep each migration focused on a single logical change for clarity and easier troubleshooting
- **Zero-Downtime Deployments**: Consider deployment order and backwards compatibility for high-availability systems
- **Separate Schema and Data**: Keep schema changes separate from data migrations for better rollback safety
- **Index Management**: Create indexes on large tables carefully, using concurrent options when available to avoid locks
- **Naming Conventions**: Use clear, descriptive names that indicate what the migration does
- **Version Control**: Always commit migrations to version control and never modify existing migrations after deployment
- **Generated Scripts Only**: Use the project’s migration generator (Prisma Migrate, Knex, etc.) rather than hand-written SQL so schema and client stay synced
- **Local Down-Test**: Run both `up` and `down` locally before opening a PR to ensure rollbacks succeed
- **Expand/Contract**: For breaking changes, follow the `expand → backfill → contract` pattern and ship each step separately to keep deployments safe
- **Data Backfill Smoke Tests**: When migrating data, include quick verification SQL to confirm row counts/conditions immediately after the migration
