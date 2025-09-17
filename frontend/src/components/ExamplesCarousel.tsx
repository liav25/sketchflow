"use client";

import { useEffect, useRef } from "react";
import { EXAMPLES } from "@/data/examples";

export default function ExamplesCarousel() {
  const scrollerRef = useRef<HTMLDivElement | null>(null);

  const scrollByDelta = (dir: "left" | "right") => {
    const el = scrollerRef.current;
    if (!el) return;

    const firstCard = el.querySelector<HTMLElement>("[data-card]");
    const gap = 16; // px
    const delta = firstCard ? firstCard.clientWidth + gap : el.clientWidth * 0.8;
    el.scrollBy({ left: dir === "left" ? -delta : delta, behavior: "smooth" });
  };

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    let timer = window.setInterval(() => scrollByDelta("right"), 5000);
    const onEnter = () => window.clearInterval(timer);
    const onLeave = () => (timer = window.setInterval(() => scrollByDelta("right"), 5000));
    el.addEventListener("mouseenter", onEnter);
    el.addEventListener("mouseleave", onLeave);
    return () => {
      window.clearInterval(timer);
      el.removeEventListener("mouseenter", onEnter);
      el.removeEventListener("mouseleave", onLeave);
    };
  }, []);

  return (
    <section id="examples" className="py-24 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-secondary-800 mb-4">Examples</h2>
          <p className="text-lg text-neutral-700">
            Swipe or use arrows. Edges fade into white.
          </p>
        </div>

        <div className="relative">
          {/* Gradient fades */}
          <div className="pointer-events-none absolute left-0 top-0 h-full w-12 bg-gradient-to-r from-white via-white/80 to-white/0 z-10" />
          <div className="pointer-events-none absolute right-0 top-0 h-full w-12 bg-gradient-to-l from-white via-white/80 to-white/0 z-10" />

          {/* Arrow controls */}
          <div className="absolute inset-y-0 left-2 z-20 flex items-center">
            <button
              aria-label="Previous"
              onClick={() => scrollByDelta("left")}
              className="rounded-full bg-white/90 border border-brand-muted shadow-elevation-2 hover:bg-white px-3 py-2 text-secondary-700"
            >
              ‹
            </button>
          </div>
          <div className="absolute inset-y-0 right-2 z-20 flex items-center">
            <button
              aria-label="Next"
              onClick={() => scrollByDelta("right")}
              className="rounded-full bg-white/90 border border-brand-muted shadow-elevation-2 hover:bg-white px-3 py-2 text-secondary-700"
            >
              ›
            </button>
          </div>

          {/* Scroller */}
          <div
            ref={scrollerRef}
            className="flex gap-4 overflow-x-auto scroll-smooth snap-x snap-mandatory pb-2"
          >
            {EXAMPLES.map((ex) => (
              <article
                key={ex.slug}
                data-card
                className="snap-start min-w-[85%] sm:min-w-[70%] md:min-w-[60%] lg:min-w-[50%] xl:min-w-[42%] rounded-2xl bg-white border border-brand-muted shadow-elevation-2 overflow-hidden"
              >
                <div className="p-5 border-b border-brand-muted">
                  <h3 className="text-xl font-semibold text-secondary-900">{ex.title}</h3>
                  {ex.description ? (
                    <p className="mt-1 text-neutral-600">{ex.description}</p>
                  ) : null}
                </div>
                <div className="grid grid-cols-2">
                  <figure className="relative aspect-[4/3] overflow-hidden">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={ex.beforeSrc}
                      alt={`${ex.title} — before`}
                      className="h-full w-full object-cover"
                      onError={(e) => {
                        (e.currentTarget as HTMLImageElement).style.display = 'none';
                        const fallback = document.createElement('div');
                        fallback.className = 'h-full w-full bg-neutral-100 flex items-center justify-center text-neutral-500';
                        fallback.textContent = 'Missing before image';
                        e.currentTarget.parentElement?.appendChild(fallback);
                      }}
                    />
                    <figcaption className="absolute left-2 top-2 text-xs font-medium bg-white/80 backdrop-blur px-2 py-1 rounded">
                      Before
                    </figcaption>
                  </figure>
                  <figure className="relative aspect-[4/3] overflow-hidden border-l border-brand-muted">
                    {/* eslint-disable-next-line @next/next/no-img-element */}
                    <img
                      src={ex.afterSrc}
                      alt={`${ex.title} — after`}
                      className="h-full w-full object-cover"
                      onError={(e) => {
                        (e.currentTarget as HTMLImageElement).style.display = 'none';
                        const fallback = document.createElement('div');
                        fallback.className = 'h-full w-full bg-neutral-100 flex items-center justify-center text-neutral-500';
                        fallback.textContent = 'Missing after image';
                        e.currentTarget.parentElement?.appendChild(fallback);
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
        </div>
      </div>
    </section>
  );
}

