## Database model best practices

- **Clear Naming**: Use singular names for models and plural for tables following your framework's conventions
- **Timestamps**: Include created and updated timestamps on all tables for auditing and debugging
- **Data Integrity**: Use database constraints (NOT NULL, UNIQUE, foreign keys) to enforce data rules at the database level
- **Appropriate Data Types**: Choose data types that match the data's purpose and size requirements
- **Indexes on Foreign Keys**: Index foreign key columns and other frequently queried fields for performance
- **Validation at Multiple Layers**: Implement validation at both model and database levels for defense in depth
- **Relationship Clarity**: Define relationships clearly with appropriate cascade behaviors and naming conventions
- **Avoid Over-Normalization**: Balance normalization with practical query performance needs
- **Tenant Scoping**: Every tenant-aware model includes `tenant_id` (or equivalent) constraints and default scopes to avoid data leakage
- **Soft Deletes by Default**: For user-owned data, implement soft deletes plus retention policies unless hard deletes are a compliance requirement
- **Protect PII**: Encrypt sensitive columns using managed extensions or application-level encryption and document the key management approach
- **Ownership Docs**: Add comments/docstrings describing aggregate boundaries, invariants, and owning teams so responsibilities stay clear
