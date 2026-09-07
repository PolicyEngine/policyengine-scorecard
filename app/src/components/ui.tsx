import type { ReactNode } from "react";
import {
  Badge,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@policyengine/ui-kit/primitives";
import { SPINE_META, type SpineBucket } from "../spine";
import { STATUS_LABELS, type Status } from "../types";

/** Small uppercase label above a stat or section. */
export function Kicker({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <p className={"kicker " + className}>{children}</p>;
}

/**
 * A headline number with its label and one line of context — the same
 * shape as ui-kit's MetricCard, but with a mono tabular figure and a
 * free-form value so ratios ("1,031 / 4,792") render as one unit.
 */
export function Stat({
  label,
  value,
  unit,
  sub,
}: {
  label: string;
  value: string;
  unit?: string;
  sub?: ReactNode;
}) {
  return (
    <Card className="gap-0 rounded-lg py-4 shadow-none">
      <CardContent className="px-4">
        <p className="fig text-3xl font-semibold leading-9 tracking-tight">
          {value}
          {unit && (
            <span className="ml-1.5 text-base font-normal text-muted-foreground">
              {unit}
            </span>
          )}
        </p>
        <p className="mt-1 text-sm text-foreground">{label}</p>
        {sub && (
          <p className="mt-0.5 text-xs leading-4 text-muted-foreground">{sub}</p>
        )}
      </CardContent>
    </Card>
  );
}

/** Card with a compact heading row — the unit of layout on every view. */
export function Panel({
  title,
  description,
  action,
  children,
  className = "",
}: {
  title: ReactNode;
  description?: ReactNode;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <Card className={"gap-3 rounded-lg py-4 shadow-none " + className}>
      <CardHeader className="px-4">
        <div className="flex flex-wrap items-baseline justify-between gap-2">
          <CardTitle className="text-base font-semibold">{title}</CardTitle>
          {action}
        </div>
        {description && (
          <p className="text-xs leading-4 text-muted-foreground">
            {description}
          </p>
        )}
      </CardHeader>
      <CardContent className="px-4">{children}</CardContent>
    </Card>
  );
}

/** Text-style button that moves the reader to another view. */
export function LinkButton({
  onClick,
  children,
  className = "",
}: {
  onClick: () => void;
  children: ReactNode;
  className?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        "text-sm font-medium text-primary underline-offset-4 hover:underline " +
        className
      }
    >
      {children}
    </button>
  );
}

export interface SelectOption {
  value: string;
  label: string;
}

/** Labelled ui-kit Select for the filter bars. */
export function LabeledSelect({
  label,
  value,
  onChange,
  options,
  className = "",
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  options: SelectOption[];
  className?: string;
}) {
  return (
    <div className={"flex flex-col gap-1 " + className}>
      <Label className="text-xs text-muted-foreground">{label}</Label>
      <Select value={value} onValueChange={onChange}>
        <SelectTrigger size="sm" className="w-full min-w-36" aria-label={label}>
          <SelectValue />
        </SelectTrigger>
        <SelectContent>
          {options.map((o) => (
            <SelectItem key={o.value} value={o.value}>
              {o.label}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

/** Colour square for a coverage bucket. */
export function Swatch({
  bucket,
  className = "",
}: {
  bucket: SpineBucket;
  className?: string;
}) {
  return (
    <span
      aria-hidden
      className={
        "inline-block h-2.5 w-2.5 shrink-0 rounded-[2px] border border-border " +
        SPINE_META[bucket].swatch +
        " " +
        className
      }
    />
  );
}

/** Status swatch for populations-feed statuses, which have no closeness. */
const STATUS_SWATCH: Record<Status, string> = {
  comparable: "bg-chart-1",
  constructed: "bg-chart-3",
  baseline_unvalidated: "bg-warning",
  concept_mismatch: "bg-chart-4",
  pe_gap: "bg-gray-600",
  not_computed: "bg-gray-300",
  suppressed: "bg-gray-100",
};

/**
 * Comparison-row badge: colour is the coverage bucket (how far apart the
 * two values are), text is the comparison status (why they are or are not
 * comparable) whenever both values exist.
 */
export function StatusBadge({
  bucket,
  status,
}: {
  bucket: SpineBucket;
  status?: Status;
}) {
  const meta = SPINE_META[bucket];
  const label =
    status && ["close", "moderate", "far"].includes(bucket)
      ? STATUS_LABELS[status]
      : meta.label;
  return (
    <Badge
      variant="outline"
      className="gap-1.5 whitespace-nowrap font-normal"
      title={meta.text}
    >
      <Swatch bucket={bucket} className="h-2 w-2 border-0" />
      {label}
    </Badge>
  );
}

/** Populations-feed status badge (reform validation). */
export function StatusPill({ status }: { status: Status }) {
  return (
    <Badge variant="outline" className="gap-1.5 whitespace-nowrap font-normal">
      <span
        aria-hidden
        className={"inline-block h-2 w-2 rounded-[2px] " + STATUS_SWATCH[status]}
      />
      {STATUS_LABELS[status] ?? status}
    </Badge>
  );
}

/** Tiny uppercase tag for relationships, severities and lane stages. */
export function Tag({
  children,
  tone = "solid",
  title,
  className = "",
}: {
  children: ReactNode;
  tone?: "solid" | "outline" | "dashed" | "primary";
  title?: string;
  className?: string;
}) {
  const tones: Record<string, string> = {
    solid: "bg-muted text-muted-foreground",
    outline: "border border-border text-muted-foreground",
    dashed: "border border-dashed border-border-medium text-muted-foreground",
    primary: "border border-chart-1 text-chart-3",
  };
  return (
    <span
      title={title}
      className={
        "inline-block rounded-sm px-1 py-px align-middle text-[10px] font-medium uppercase leading-4 tracking-wide " +
        tones[tone] +
        " " +
        className
      }
    >
      {children}
    </span>
  );
}

/** Mono provenance line (engine pins, fetch dates, build stamps). */
export function Provenance({
  items,
  className = "",
}: {
  items: ReactNode[];
  className?: string;
}) {
  return (
    <p
      className={
        "fig flex flex-wrap gap-x-4 gap-y-1 text-[11px] leading-4 text-muted-foreground " +
        className
      }
    >
      {items.map((it, i) => (
        <span key={i}>{it}</span>
      ))}
    </p>
  );
}
