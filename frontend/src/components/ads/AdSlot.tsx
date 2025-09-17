"use client";

import { useEffect, useRef } from "react";

type AdSlotProps = {
  slot?: string; // AdSense slot id (numeric string). If not set, shows a placeholder in dev.
  format?: string; // e.g., "auto"
  responsive?: boolean; // data-full-width-responsive
  className?: string;
  style?: React.CSSProperties;
  /**
   * If true, renders a subtle placeholder box when ads are disabled or slot is missing.
   * Defaults to true in development and false in production.
   */
  showPlaceholder?: boolean;
};

declare global {
  interface Window {
    adsbygoogle: unknown[];
  }
}

export default function AdSlot({
  slot,
  format = "auto",
  responsive = true,
  className,
  style,
  showPlaceholder,
}: AdSlotProps) {
  const insRef = useRef<HTMLModElement | null>(null);

  const client = process.env.NEXT_PUBLIC_ADSENSE_CLIENT;
  const enabled = (process.env.NEXT_PUBLIC_ADSENSE_ENABLED ?? "true") !== "false";
  const adtest = process.env.NODE_ENV !== "production" ? "on" : undefined;
  const shouldShowPlaceholder =
    showPlaceholder ?? (process.env.NODE_ENV !== "production");

  useEffect(() => {
    // Only attempt to load if enabled, client is present, and slot is provided
    if (!enabled || !client || !slot) return;

    try {
      const q = (window.adsbygoogle = (window.adsbygoogle || []) as unknown[]);
      q.push({});
    } catch {
      // Swallow errors; ad loading should not break the app
    }
  }, [client, enabled, slot]);

  // If disabled or missing configuration, render a placeholder (optional)
  if (!enabled || !client || !slot) {
    if (!shouldShowPlaceholder) return null;
    return (
      <div
        className={
          "border border-neutral-200 bg-neutral-50 text-neutral-500 " +
          "rounded-xl text-center text-sm flex items-center justify-center " +
          (className ?? "")
        }
        style={{ height: 120, ...style }}
        aria-label="Ad placeholder"
      >
        Ad placeholder (configure AdSense)
      </div>
    );
  }

  return (
    <ins
      ref={insRef}
      className={`adsbygoogle ${className ?? ""}`.trim()}
      style={{ display: "block", ...(style ?? {}) }}
      data-ad-client={client}
      data-ad-slot={slot}
      data-ad-format={format}
      data-full-width-responsive={responsive ? "true" : undefined}
      data-adtest={adtest}
      aria-label="Advertisement"
    />
  );
}
