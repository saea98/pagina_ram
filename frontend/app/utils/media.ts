import type { ImageAsset, Site } from '~/types/public'

export function siteImage(site: Site, id: string | null | undefined): ImageAsset | null {
  if (!id || !site.media) return null
  return site.media[id] ?? null
}

export function largestUrl(map: Record<string, string> | undefined): string {
  if (!map) return ''
  const widths = Object.keys(map)
    .map(Number)
    .filter((value) => !Number.isNaN(value))
    .sort((a, b) => a - b)
  const key = widths.at(-1)
  if (key === undefined) return Object.values(map)[0] ?? ''
  return map[String(key)] ?? ''
}

export function toSrcset(map: Record<string, string> | undefined): string {
  if (!map) return ''
  return Object.entries(map)
    .map(([width, url]) => `${url} ${width}w`)
    .join(', ')
}
