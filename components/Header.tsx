import { Fragment } from "react";
import { MESSAGES } from "@/lib/messages";

export function Header() {
  return (
    <header className="border-b border-rule pb-6 mb-8">
      <div className="flex items-baseline gap-4 flex-wrap">
        <h1 className="font-serif italic font-semibold text-5xl tracking-tight m-0 leading-none">
          {MESSAGES.brand.wordmark}
        </h1>
        <p className="font-serif text-lg text-ink-soft m-0">
          {MESSAGES.brand.tagline}
        </p>
      </div>

      <div className="inline-flex items-center gap-2 mt-4 px-3 py-1.5 bg-good border border-accent-green rounded-sm text-[13px] text-accent-green font-medium">
        <span className="w-1.5 h-1.5 rounded-full bg-accent-green inline-block" />
        <span>{MESSAGES.header.privacyBadge}</span>
      </div>

      <p className="mt-6 max-w-[720px] text-[15px] text-ink-soft leading-relaxed">
        {MESSAGES.header.intro.map((seg, i) =>
          seg.kind === "strong" ? (
            <strong key={i} className="text-ink font-semibold">
              {seg.value}
            </strong>
          ) : (
            <Fragment key={i}>{seg.value}</Fragment>
          ),
        )}
      </p>
    </header>
  );
}
