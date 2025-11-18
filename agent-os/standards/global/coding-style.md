## Coding style best practices

- **Consistent Naming Conventions**: Establish and follow naming conventions for variables, functions, classes, and files across the codebase
- **Automated Formatting**: Maintain consistent code style (indenting, line breaks, etc.)
- **Meaningful Names**: Choose descriptive names that reveal intent; avoid abbreviations and single-letter variables except in narrow contexts
- **Small, Focused Functions**: Keep functions small and focused on a single task for better readability and testability
- **Consistent Indentation**: Use consistent indentation (spaces or tabs) and configure your editor/linter to enforce it
- **TypeScript Strictness**: Enable `strict` (including `noImplicitAny`, `noUncheckedIndexedAccess`, etc.) and fix violations instead of loosening compiler settings
- **Typed React Components**: Prefer function components with explicitly typed props/return types; never rely on `React.FC`'s implicit children typing
- **Explicit Exports**: Declare explicit return types for all exported helpers/hooks to make API contracts clear and avoid inference drift
- **Module Barrels**: Keep shared utilities/components behind stable barrel files (`index.ts`) so imports remain consistent as files move
- **Remove Dead Code**: Delete unused code, commented-out blocks, and imports rather than leaving them as clutter
- **Backward compatibility only when required:** Unless specifically instructed otherwise, assume you do not need to write additional code logic to handle backward compatibility.
- **DRY Principle**: Avoid duplication by extracting common logic into reusable functions or modules
