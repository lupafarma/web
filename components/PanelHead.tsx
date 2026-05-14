type PanelHeadProps = {
  title: string;
  meta?: string;
};

export function PanelHead({ title, meta }: PanelHeadProps) {
  return (
    <div className="flex items-baseline justify-between border-b-2 border-ink pb-2 mb-4">
      <h2 className="font-serif text-[22px] tracking-tight font-medium m-0">
        {title}
      </h2>
      {meta && (
        <span className="font-mono text-[12px] text-ink-faint uppercase tracking-wider">
          {meta}
        </span>
      )}
    </div>
  );
}
