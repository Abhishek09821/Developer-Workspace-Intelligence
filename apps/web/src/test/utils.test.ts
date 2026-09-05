import { describe, it, expect } from 'vitest'
import { cn, capitalize, statusColor, timeAgo } from '@/lib/utils'

describe('cn', () => {
  it('merges class strings', () => {
    expect(cn('a', 'b')).toBe('a b')
  })

  it('ignores falsy values', () => {
    expect(cn('a', false && 'b', null, undefined, 'c')).toBe('a c')
  })
})

describe('capitalize', () => {
  it('capitalizes the first letter and lowercases the rest', () => {
    expect(capitalize('HELLO')).toBe('Hello')
    expect(capitalize('world')).toBe('World')
  })
})

describe('statusColor', () => {
  it('returns a string for known statuses', () => {
    expect(statusColor('completed')).toContain('emerald')
    expect(statusColor('failed')).toContain('red')
    expect(statusColor('created')).toContain('slate')
  })

  it('returns a default for unknown statuses', () => {
    expect(statusColor('unknown_status')).toBe('bg-slate-700 text-slate-300')
  })
})

describe('timeAgo', () => {
  it('returns "just now" for very recent dates', () => {
    const now = new Date().toISOString()
    expect(timeAgo(now)).toBe('just now')
  })

  it('returns days for older dates', () => {
    const old = new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString()
    expect(timeAgo(old)).toBe('3d ago')
  })
})
