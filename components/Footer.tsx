import { MESSAGES } from "@/lib/messages";

const LINK_CLASS =
  "text-ink-soft underline decoration-rule hover:decoration-ink-soft";

type FooterProps = { count: number };

export function Footer({ count }: FooterProps) {
  const F = MESSAGES.footer;
  return (
    <footer className="mt-16 pt-6 border-t border-rule text-[12px] text-ink-faint font-mono">
      <div>
        <strong className="text-ink-soft">{F.sourcesHeading}</strong>
      </div>
      <div className="mt-2 leading-relaxed">
        · {F.sources.nomenclator}
        <br />
        ·{" "}
        <a className={LINK_CLASS} href={F.sources.boe.href}>
          {F.sources.boe.label}
        </a>{" "}
        — {F.sources.boe.desc}
        <br />
        ·{" "}
        <a className={LINK_CLASS} href={F.sources.rd177.href}>
          {F.sources.rd177.label}
        </a>{" "}
        — {F.sources.rd177.desc}
        <br />
        ·{" "}
        <a className={LINK_CLASS} href={F.sources.rd823.href}>
          {F.sources.rd823.label}
        </a>{" "}
        — {F.sources.rd823.desc}
      </div>
      <div className="mt-4">
        {F.privacy}
        <br />
        {F.buildInfo(count)}{" "}
        <a className={LINK_CLASS} href={F.repoHref}>
          {F.repoLabel}
        </a>
      </div>
    </footer>
  );
}
