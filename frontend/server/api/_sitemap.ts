import type { PortfolioCard, ServiceCard, TeamCard } from '~/types/public'

export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const origin = config.public.siteUrl.replace(/\/$/, '')
  const base = `${config.apiInternalUrl}/api/v1/public`
  const [services, portfolio, team] = await Promise.all([
    $fetch<ServiceCard[]>(`${base}/services`),
    $fetch<PortfolioCard[]>(`${base}/portfolio`),
    $fetch<TeamCard[]>(`${base}/team`),
  ])
  const abs = (path: string) => `${origin}${path}`
  return [
    { loc: abs('/') },
    { loc: abs('/portafolio') },
    { loc: abs('/aviso-de-privacidad') },
    { loc: abs('/links') },
    ...services.map((service) => ({
      loc: abs(`/servicios/${service.slug}`),
      lastmod: service.updated_at,
    })),
    ...portfolio.map((piece) => ({
      loc: abs(`/portafolio/${piece.slug}`),
      lastmod: piece.updated_at,
    })),
    ...team.map((member) => ({ loc: abs(`/equipo/${member.slug}`), lastmod: member.updated_at })),
  ]
})
