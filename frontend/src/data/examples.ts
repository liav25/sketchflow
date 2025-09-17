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
    beforeSrc: '/examples/pizza-flow-before.jpeg',
    afterSrc: '/examples/pizza-flow-after.png',
  },
  {
    slug: 'user-db-response',
    title: 'User → DB → Response',
    description: 'Whiteboard idea transformed into a tidy sequence',
    format: 'mermaid',
    beforeSrc: '/examples/user-db-response-before.jpeg',
    afterSrc: '/examples/user-db-response-after.jpeg',
  },
  {
    slug: 'system-architecture',
    title: 'System Architecture (Audit/Transport/Archive)',
    description: 'Complex whiteboard system converted to a structured diagram',
    format: 'mermaid',
    beforeSrc: '/examples/system-architecture-before.webp',
    afterSrc: '/examples/system-architecture-after.png',
  },
];
