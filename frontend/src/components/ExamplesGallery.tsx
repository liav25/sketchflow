"use client";

import { EXAMPLES } from "@/data/examples";

export default function ExamplesGallery() {
  const examples = EXAMPLES;

  return (
    <section id="examples" className="py-24 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-secondary-800 mb-4">Examples</h2>
          <p className="text-lg text-neutral-700">
            Before and after results from real sketch conversions
          </p>
        </div>

        {examples.length === 0 ? (
          <div className="max-w-2xl mx-auto text-center p-8 border border-dashed border-brand-muted rounded-xl bg-brand-surface">
            <p className="text-neutral-700">
              No examples yet. Place your images in
              <code className="mx-1 px-1 py-0.5 rounded bg-neutral-100 text-neutral-800">/frontend/public/examples</code>
              and add entries in
              <code className="mx-1 px-1 py-0.5 rounded bg-neutral-100 text-neutral-800">/frontend/src/data/examples.ts</code>.
            </p>
            <p className="mt-3 text-neutral-600 text-sm">
              Use a slug and name files like <span className="font-mono">slug-before.webp</span> / <span className="font-mono">slug-after.webp</span> or <span className="font-mono">slug-before.svg</span> / <span className="font-mono">slug-after.svg</span>.
            </p>
          </div>
        ) : (
          <div className="grid gap-8 md:gap-10 md:grid-cols-2">
            {examples.map((ex) => (
              <article
                key={ex.slug}
                className="rounded-2xl bg-white border border-brand-muted shadow-elevation-2 overflow-hidden"
              >
                <div className="p-5 border-b border-brand-muted">
                  <h3 className="text-xl font-semibold text-secondary-900">{ex.title}</h3>
                  {ex.description ? (
                    <p className="mt-1 text-neutral-600">{ex.description}</p>
                  ) : null}
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2">
                  <figure className="relative aspect-[4/3] overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={ex.beforeSrc}
                      alt={`${ex.title} — before`}
                      className="h-full w-full object-cover"
                      onError={(e) => {
                        const img = e.currentTarget as HTMLImageElement;
                        const tried = img.dataset.fallbackTried === '1';
                        if (!tried && img.src.endsWith('.svg')) {
                          img.dataset.fallbackTried = '1';
                          img.src = img.src.replace(/\.svg($|\?)/, '.webp$1');
                          return;
                        }
                        img.style.display = 'none';
                        const fallback = document.createElement('div');
                        fallback.className = 'h-full w-full bg-neutral-100 flex items-center justify-center text-neutral-500';
                        fallback.textContent = 'Missing before image';
                        img.parentElement?.appendChild(fallback);
                      }}
                    />
                    <figcaption className="absolute left-2 top-2 text-xs font-medium bg-white/80 backdrop-blur px-2 py-1 rounded">
                      Before
                    </figcaption>
                  </figure>
                  <figure className="relative aspect-[4/3] overflow-hidden border-t md:border-t-0 md:border-l border-brand-muted">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={ex.afterSrc}
                      alt={`${ex.title} — after`}
                      className="h-full w-full object-cover"
                      onError={(e) => {
                        const img = e.currentTarget as HTMLImageElement;
                        const tried = img.dataset.fallbackTried === '1';
                        if (!tried && img.src.endsWith('.svg')) {
                          img.dataset.fallbackTried = '1';
                          img.src = img.src.replace(/\.svg($|\?)/, '.webp$1');
                          return;
                        }
                        img.style.display = 'none';
                        const fallback = document.createElement('div');
                        fallback.className = 'h-full w-full bg-neutral-100 flex items-center justify-center text-neutral-500';
                        fallback.textContent = 'Missing after image';
                        img.parentElement?.appendChild(fallback);
                      }}
                    />
                    <figcaption className="absolute left-2 top-2 text-xs font-medium bg-white/80 backdrop-blur px-2 py-1 rounded">
                      After
                    </figcaption>
                  </figure>
                </div>

                <div className="flex items-center justify-between p-4 border-t border-brand-muted">
                  <div className="text-sm text-neutral-600">
                    {ex.format ? ex.format.toUpperCase() : 'RESULT'}
                  </div>
                  <div className="flex gap-3">
                    <a
                      href={ex.beforeSrc}
                      target="_blank"
                      className="text-sm font-medium text-primary-700 hover:text-primary-800"
                    >
                      View before
                    </a>
                    <a
                      href={ex.afterSrc}
                      target="_blank"
                      className="text-sm font-medium text-primary-700 hover:text-primary-800"
                    >
                      View after
                    </a>
                  </div>
                </div>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
