import type { Home, ServiceDetail, PortfolioDetail, Faq } from '~/types/public'

export function homeJsonLd(home: Home, url: string) {
  return {
    '@context': 'https://schema.org',
    '@type': 'ProfessionalService',
    name: home.site.brand.name,
    url,
    email: home.site.contact.email,
    image: home.site.seo.og_image_media_id
      ? home.site.media?.[home.site.seo.og_image_media_id]?.webp['1600']
      : undefined,
    areaServed: 'Ciudad de México',
    sameAs: [home.site.social.instagram].filter(Boolean),
    founder: home.team.map((member) => ({
      '@type': 'Person',
      name: member.full_name,
      jobTitle: member.role_label,
    })),
    hasOfferCatalog: {
      '@type': 'OfferCatalog',
      itemListElement: home.services.map((service) => ({
        '@type': 'Offer',
        itemOffered: { '@type': 'Service', name: service.title },
      })),
    },
  }
}

export function serviceJsonLd(service: ServiceDetail, url: string, provider: string) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Service',
    name: service.title,
    description: service.short_description,
    url,
    areaServed: 'Ciudad de México',
    provider: { '@type': 'ProfessionalService', name: provider },
    ...(service.price_from_mxn
      ? {
          offers: {
            '@type': 'Offer',
            priceSpecification: {
              '@type': 'PriceSpecification',
              price: service.price_from_mxn,
              priceCurrency: 'MXN',
            },
          },
        }
      : {}),
  }
}

export function recordingJsonLd(piece: PortfolioDetail, url: string) {
  return {
    '@context': 'https://schema.org',
    '@type': 'MusicRecording',
    name: piece.title,
    url,
    image: piece.cover?.webp['960'],
    byArtist: { '@type': 'MusicGroup', name: piece.artist_name },
    duration: piece.audio?.duration_s ? `PT${Math.round(piece.audio.duration_s)}S` : undefined,
  }
}

export function faqJsonLd(faqs: Faq[]) {
  return {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    mainEntity: faqs.map((faq) => ({
      '@type': 'Question',
      name: faq.question,
      acceptedAnswer: { '@type': 'Answer', text: faq.answer },
    })),
  }
}
