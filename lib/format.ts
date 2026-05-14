export function eur(n: number | null | undefined): string {
  if (n == null || isNaN(n)) return "—";
  return (
    "€" +
    Number(n)
      .toFixed(2)
      .replace(".", ",")
      .replace(/\B(?=(\d{3})+(?!\d))/g, ".")
  );
}
