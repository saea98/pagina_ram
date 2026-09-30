export function matchGain(
  lufs: number | null | undefined,
  other: number | null | undefined,
): number {
  if (lufs == null || other == null) return 1
  const target = Math.min(lufs, other)
  return 10 ** ((target - lufs) / 20)
}
