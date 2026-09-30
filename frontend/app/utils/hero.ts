export interface HeroWord {
  text: string
  em: boolean
  breakBefore: boolean
}

export function splitHeroTitle(html: string): HeroWord[] {
  const marked = html.replace(/<br\s*\/?>/gi, '\n')
  const chunks = marked.split(/(<em>[\s\S]*?<\/em>)/i)
  const words: HeroWord[] = []
  let breakNext = false
  for (const chunk of chunks) {
    const em = /^<em>/i.test(chunk)
    const plain = chunk.replace(/<\/?em>/gi, '')
    for (const token of plain.split(/(\n|\s+)/)) {
      if (!token || /^\s+$/.test(token)) continue
      if (token === '\n') {
        breakNext = true
        continue
      }
      words.push({ text: token, em, breakBefore: breakNext })
      breakNext = false
    }
  }
  if (!/<br/i.test(html)) {
    const firstEm = words.findIndex((word) => word.em)
    if (firstEm > 0) words[firstEm]!.breakBefore = true
  }
  return words
}
