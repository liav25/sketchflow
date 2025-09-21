// Example images now live as public assets (SVG). Use path strings.

export type ExampleItem = {
  slug: string;
  title: string;
  description?: string;
  format?: 'mermaid' | 'drawio' | 'uml';
  beforeSrc: string;
  afterSrc: string;
};

export const EXAMPLES: ExampleItem[] = [
  {
    slug: 'pizza-flow',
    title: 'Pizza Order Flow',
    description: 'From notebook sketch to clean flowchart',
    format: 'mermaid',
    beforeSrc: '/examples/pizza-flow-before.webp',
    afterSrc: '/examples/pizza-flow-after.webp',
  },
  {
    slug: 'user-db-response',
    title: 'User → DB → Response',
    description: 'Whiteboard idea transformed into a tidy sequence',
    format: 'mermaid',
    beforeSrc: '/examples/user-db-response-before.webp',
    afterSrc: '/examples/user-db-response-after.webp',
  },
  {
    slug: 'system-architecture',
    title: 'System Architecture (Audit/Transport/Archive)',
    description: 'Complex whiteboard system converted to a structured diagram',
    format: 'mermaid',
    beforeSrc: '/examples/system-architecture-before.webp',
    afterSrc: '/examples/system-architecture-after.webp',
  },
];
