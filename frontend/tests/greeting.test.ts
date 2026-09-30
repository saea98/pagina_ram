import { describe, expect, it } from 'vitest'
import { homeGreeting } from '../app/utils/greeting'

describe('homeGreeting', () => {
  it('saluda en español', () => {
    expect(homeGreeting).toBe('Hola')
  })
})
