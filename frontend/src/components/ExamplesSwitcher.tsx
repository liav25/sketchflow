"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { EXAMPLES } from "@/data/examples";
import { ArrowRightIcon } from "@heroicons/react/24/outline";

const SWITCH_MS = 4000; // auto-switch every 4 seconds
const FADE_MS = 2000;   // fade transition duration 2s

export default function ExamplesSwitcher() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (EXAMPLES.length <= 1) return; // nothing to rotate
    const id = window.setInterval(() => {
      setIndex((i) => (i + 1) % EXAMPLES.length);
    }, SWITCH_MS);
    return () => window.clearInterval(id);
  }, []);

  if (EXAMPLES.length === 0) {
    return (
      <section id="examples" className="py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="rounded-2xl border border-dashed border-brand-muted bg-brand-surface p-10 text-center text-neutral-600">
            Add examples in /frontend/src/data/examples.ts
          </div>
        </div>
      </section>
    );
  }

  return (
    <section id="examples" className="pt-2 pb-6 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="relative">
          {/* Fixed height to keep images consistent */}
          <div className="relative w-full bg-white min-h-[420px] md:min-h-[480px] flex items-center">
            {EXAMPLES.map((ex, i) => (
              <div
                key={ex.slug}
                className={`absolute inset-0 grid grid-cols-[auto_auto_auto] items-center justify-center justify-items-center gap-1 sm:gap-2 md:gap-3 transition-opacity duration-[2000ms] ease-in-out ${
                  i === index ? "opacity-100" : "opacity-0 pointer-events-none"
                }`}
              >
                {/* Before */}
                <div className="flex items-center justify-center px-0">
                  <div className="relative bg-white" style={{ width: 600, height: 360 }}>
                    <Image
                      src={ex.beforeSrc}
                      alt={`${ex.title || ex.slug} before`}
                      fill
                      sizes="(min-width: 768px) 600px, 360px"
                      style={{ objectFit: 'contain' }}
                      priority={i === 0}
                    />
                    <div
                      aria-hidden="true"
                      className="pointer-events-none absolute inset-0"
                      style={{
                        backgroundImage:
                          'linear-gradient(to right, white 0%, rgba(255,255,255,0) 14%, rgba(255,255,255,0) 86%, white 100%),' +
                          'linear-gradient(to bottom, white 0%, rgba(255,255,255,0) 14%, rgba(255,255,255,0) 86%, white 100%)',
                      }}
                    />
                  </div>
                </div>

                {/* Center Arrow */}
                <div className="pointer-events-none flex items-center justify-center text-secondary-700">
                  <ArrowRightIcon className="w-12 h-12 sm:w-14 sm:h-14 md:w-16 md:h-16" style={{ strokeWidth: 3 }} />
                </div>

                {/* After */}
                <div className="flex items-center justify-center px-0">
                  <div className="relative bg-white" style={{ width: 600, height: 360 }}>
                    <Image
                      src={ex.afterSrc}
                      alt={`${ex.title || ex.slug} after`}
                      fill
                      sizes="(min-width: 768px) 600px, 360px"
                      style={{ objectFit: 'contain' }}
                      priority={i === 0}
                    />
                    <div
                      aria-hidden="true"
                      className="pointer-events-none absolute inset-0"
                      style={{
                        backgroundImage:
                          'linear-gradient(to right, white 0%, rgba(255,255,255,0) 14%, rgba(255,255,255,0) 86%, white 100%),' +
                          'linear-gradient(to bottom, white 0%, rgba(255,255,255,0) 14%, rgba(255,255,255,0) 86%, white 100%)',
                      }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
