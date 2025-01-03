import { z } from 'zod'

// Basic validation schemas
export const portSchema = z.string().regex(/^(COM\d+|\/dev\/tty(USB|ACM|S)\d+)$/, {
  message: 'Invalid port format'
})

export const versionSchema = z.string().regex(/^(v\d+\.\d+\.\d+|master)$/, {
  message: 'Invalid version format'
})

export const printerNameSchema = z.string()
  .min(1, 'Printer name is required')
  .max(50, 'Printer name too long')
  .regex(/^[\w\s-]+$/, {
    message: 'Printer name can only contain letters, numbers, spaces, and hyphens'
  })

// Complex validation schemas
export const dimensionsSchema = z.object({
  x: z.number().positive('X dimension must be positive'),
  y: z.number().positive('Y dimension must be positive'),
  z: z.number().positive('Z dimension must be positive')
})

export const speedSchema = z.object({
  max_velocity: z.number().positive('Max velocity must be positive'),
  max_accel: z.number().positive('Max acceleration must be positive'),
  max_z_velocity: z.number().positive('Max Z velocity must be positive'),
  max_z_accel: z.number().positive('Max Z acceleration must be positive')
})

export const configSchema = z.object({
  printer_name: printerNameSchema,
  bed_size: dimensionsSchema,
  speed: speedSchema,
  features: z.object({
    pressure_advance: z.boolean(),
    input_shaping: z.boolean()
  })
})

// Validation functions
export const validatePort = (port: string): boolean => {
  try {
    portSchema.parse(port)
    return true
  } catch {
    return false
  }
}

export const validateVersion = (version: string): boolean => {
  try {
    versionSchema.parse(version)
    return true
  } catch {
    return false
  }
}

export const validateConfig = (config: unknown) => {
  return configSchema.safeParse(config)
}

// Type inference
export type PrinterConfig = z.infer<typeof configSchema>
export type Dimensions = z.infer<typeof dimensionsSchema>
export type SpeedConfig = z.infer<typeof speedSchema>

// Input sanitization
export const sanitizeInput = (input: string): string => {
  return input.replace(/[^\w\s-]/g, '')
}

// Form validation helpers
export const validateField = (
  schema: z.ZodType<any>,
  value: unknown
): { valid: boolean; error?: string } => {
  try {
    schema.parse(value)
    return { valid: true }
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        valid: false,
        error: error.errors[0]?.message || 'Invalid input'
      }
    }
    return { valid: false, error: 'Validation failed' }
  }
}

export const validateForm = <T>(
  schema: z.ZodType<T>,
  data: unknown
): { valid: boolean; data?: T; errors?: Record<string, string> } => {
  const result = schema.safeParse(data)
  
  if (result.success) {
    return { valid: true, data: result.data }
  }
  
  const errors: Record<string, string> = {}
  result.error.errors.forEach((error) => {
    const path = error.path.join('.')
    errors[path] = error.message
  })
  
  return { valid: false, errors }
}

// Common validation patterns
export const patterns = {
  hostname: /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9](?:\.[a-zA-Z]{2,})+$/,
  ipAddress: /^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/,
  macAddress: /^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$/,
  url: /^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$/
}
