type BadgeProps = { label: string };

export function Badge({ label }: BadgeProps) {
  return <span>{label}</span>;
}
