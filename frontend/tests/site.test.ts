import { describe, expect, it } from 'vitest'
import { readUtm } from '../app/composables/useUtm'
import { splitHeroTitle } from '../app/utils/hero'
import { matchGain } from '../app/utils/lufs'

describe('matchGain', () => {
  it('pulls the louder stem down to the quieter one', () => {
    expect(matchGain(-14, -16)).toBeCloseTo(10 ** ((-16 - -14) / 20))
    expect(matchGain(-16, -14)).toBe(1)
    expect(matchGain(null, -14)).toBe(1)
  })
})

describe('splitHeroTitle', () => {
  it('breaks before the first emphasis when the title has no br', () => {
    const words = splitHeroTitle('Tu música, tu proceso y <em>nuestra cereza.</em>')
    const emphasis = words.find((word) => word.em)
    expect(emphasis?.text).toBe('nuestra')
    expect(emphasis?.breakBefore).toBe(true)
  })
})

describe('readUtm', () => {
  it('keeps the first touch of the session', () => {
    const storage = new Map<string, string>()
    const memory = {
      getItem: (key: string) => storage.get(key) ?? null,
      setItem: (key: string, value: string) => storage.set(key, value),
    } as Storage
    const first = readUtm('?utm_source=instagram&utm_medium=bio', 'https://instagram.com', memory)
    const second = readUtm('?utm_source=email', '', memory)
    expect(first.source).toBe('instagram')
    expect(second.source).toBe('instagram')
    expect(second.referrer).toBe('https://instagram.com')
  })
})
