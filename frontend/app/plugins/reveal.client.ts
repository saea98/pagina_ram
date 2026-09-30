export default defineNuxtPlugin((nuxtApp) => {
  const observe = () => {
    const reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    document.querySelectorAll('.reveal:not(.in)').forEach((element) => {
      if (reduce) {
        element.classList.add('in')
        return
      }
      const observer = new IntersectionObserver(
        (entries) => {
          for (const entry of entries) {
            if (!entry.isIntersecting) continue
            entry.target.classList.add('in')
            observer.unobserve(entry.target)
          }
        },
        { threshold: 0.12 },
      )
      observer.observe(element)
    })
  }
  nuxtApp.hook('page:finish', observe)
  if (import.meta.client) observe()
})
