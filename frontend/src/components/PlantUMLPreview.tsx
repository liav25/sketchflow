'use client';

import React from 'react';
import plantumlEncoder from 'plantuml-encoder';
// We render directly via the PlantUML server using an encoded URL

type Props = {
  code: string;
  alt?: string;
  className?: string;
};

function buildServerBase(): string {
  const custom = process.env.NEXT_PUBLIC_PLANTUML_SERVER;
  if (custom) {
    try {
      const u = new URL(custom);
      return u.origin + (u.pathname.endsWith('/') ? u.pathname.slice(0, -1) : u.pathname);
    } catch {
      // fallthrough to default
    }
  }
  return 'https://www.plantuml.com/plantuml';
}

export default function PlantUMLPreview({ code, alt = 'PlantUML Preview', className }: Props) {
  const [imgError, setImgError] = React.useState(false);

  const trimmed = (code || '').trim();
  if (!trimmed) {
    return (
      <div className={className}>
        <p className="text-sm text-neutral-600 dark:text-neutral-300">No UML code to preview.</p>
        <p className="text-xs text-neutral-500 dark:text-neutral-400">Try switching to the Code tab or regenerate.</p>
      </div>
    );
  }

  // Ensure @startuml/@enduml wrapper for server rendering
  const withWrapper = trimmed.toLowerCase().startsWith('@startuml') && trimmed.toLowerCase().endsWith('@enduml')
    ? trimmed
    : `@startuml\n${trimmed}\n@enduml`;

  const encoded = plantumlEncoder.encode(withWrapper);
  const server = buildServerBase();
  const src = `${server}/svg/${encoded}`;

  if (imgError) {
    return (
      <div className={className}>
        <p className="text-sm text-red-600 dark:text-red-400">Failed to load UML preview.</p>
        <a href={src} target="_blank" rel="noopener noreferrer" className="text-primary-600 underline">Open in new tab</a>
      </div>
    );
  }

  return (
    <img
      alt={alt}
      src={src}
      className={className}
      style={{ maxWidth: '100%', height: 'auto' }}
      onError={() => setImgError(true)}
    />
  );
}
