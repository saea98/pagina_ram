import * as v from 'valibot'

export const leadSchema = v.pipe(
  v.object({
    name: v.pipe(v.string(), v.trim(), v.minLength(1, 'Escribe tu nombre.')),
    email: v.string(),
    phone: v.string(),
    message: v.pipe(v.string(), v.trim(), v.minLength(1, 'Cuéntanos de tu proyecto.')),
    consent: v.boolean(),
  }),
  v.forward(
    v.check(
      (input) => input.email.includes('@') || /^\+[1-9]\d{7,14}$/.test(input.phone),
      'Deja un correo o un teléfono.',
    ),
    ['email'],
  ),
  v.forward(
    v.check((input) => input.consent === true, 'Necesitamos tu consentimiento para escribirte.'),
    ['consent'],
  ),
)

export type LeadFields = v.InferInput<typeof leadSchema>
