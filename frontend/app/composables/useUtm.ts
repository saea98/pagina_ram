const KEY = 'cherry-utm'

export interface StoredUtm {
  source: string | null
  medium: string | null
  campaign: string | null
  content: string | null
  term: string | null
  referrer: string | null
}

const empty: StoredUtm = {
  source: null,
  medium: null,
  campaign: null,
  content: null,
  term: null,
  referrer: null,
}

export function readUtm(search: string, referrer: string, storage: Storage | null): StoredUtm {
  let stored = empty
  try {
    const raw = storage?.getItem(KEY)
    if (raw) stored = { ...empty, ...(JSON.parse(raw) as Partial<StoredUtm>) }
  } catch {
    stored = empty
  }
  const params = new URLSearchParams(search)
  const incoming: StoredUtm = {
    source: params.get('utm_source'),
    medium: params.get('utm_medium'),
    campaign: params.get('utm_campaign'),
    content: params.get('utm_content'),
    term: params.get('utm_term'),
    referrer: referrer || null,
  }
  const hasIncoming = Object.entries(incoming).some(([name, value]) => name !== 'referrer' && value)
  if (!stored.source && hasIncoming) {
    const next = { ...incoming, referrer: incoming.referrer || stored.referrer }
    try {
      storage?.setItem(KEY, JSON.stringify(next))
    } catch {
      /* private mode */
    }
    return next
  }
  if (!stored.referrer && referrer) {
    const next = { ...stored, referrer }
    try {
      storage?.setItem(KEY, JSON.stringify(next))
    } catch {
      /* private mode */
    }
    return next
  }
  return stored
}

export function useUtm(): StoredUtm {
  if (!import.meta.client) return empty
  return readUtm(window.location.search, document.referrer, window.sessionStorage)
}
