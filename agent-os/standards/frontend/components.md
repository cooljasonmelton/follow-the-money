## UI component best practices

- **Single Responsibility**: Each component should have one clear purpose and do it well
- **Reusability**: Design components to be reused across different contexts with configurable props
- **Composability**: Build complex UIs by combining smaller, simpler components rather than monolithic structures
- **Clear Interface**: Define explicit, well-documented props with sensible defaults for ease of use
- **Encapsulation**: Keep internal implementation details private and expose only necessary APIs
- **Consistent Naming**: Use clear, descriptive names that indicate the component's purpose and follow team conventions
- **State Management**: Keep state as local as possible; lift it up only when needed by multiple components
- **Minimal Props**: Keep the number of props manageable; if a component needs many props, consider composition or splitting it
- **Documentation**: Document component usage, props, and provide examples for easier adoption by team members
- **Living Examples**: Ship a Storybook story (or MDX doc) and a React Testing Library spec for every reusable/shared component
- **Controlled Inputs**: Default to controlled inputs for forms so validation, masking, and accessibility are consistent
- **Server/Data Boundaries**: Co-locate data fetching with server components/hooks and keep presentational components pure/predictable
