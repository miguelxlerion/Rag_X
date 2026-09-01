type Props = {
  size?: number
  className?: string
  strokeWidth?: number
}

function svgProps(size: number, strokeWidth: number, className?: string) {
  return {
    width: size,
    height: size,
    viewBox: '0 0 24 24',
    fill: 'none',
    stroke: 'currentColor',
    strokeWidth,
    strokeLinecap: 'round' as const,
    strokeLinejoin: 'round' as const,
    className,
    'aria-hidden': true,
  }
}

// Key — cerradura minimalista profesional (no emoji)
export function IconKey({ size = 16, className, strokeWidth = 1.75 }: Props) {
  return (
    <svg {...svgProps(size, strokeWidth, className)}>
      <path d="M7 10a5 5 0 0 1 9 3v1h1a1 1 0 0 1 1 1v4a1 1 0 0 1-1 1h-9a1 1 0 0 1-1-1v-4a1 1 0 0 1 1-1h1v-1a5 5 0 0 1 4-4.9" />
      <path d="M7 15a2 2 0 1 0 4 0 2 2 0 0 0-4 0z" />
    </svg>
  )
}

// Plug / Test — conector de prueba (alternativa profesional)
export function IconPlug({ size = 16, className, strokeWidth = 1.75 }: Props) {
  return (
    <svg {...svgProps(size, strokeWidth, className)}>
      <path d="M9 9V5a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4" />
      <path d="M7 9a2 2 0 0 0 0 4h10a2 2 0 0 0 0-4H7z" />
      <path d="M12 13v5" />
      <path d="M9 18h6" />
    </svg>
  )
}

// Beaker — para "Crear agentes de prueba" (alternativa profesional)
export function IconBeaker({ size = 16, className, strokeWidth = 1.75 }: Props) {
  return (
    <svg {...svgProps(size, strokeWidth, className)}>
      <path d="M8 3h8" />
      <path d="M9 3v5l-4 9a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1l-4-9V3" />
      <path d="M9 13h6" />
    </svg>
  )
}

// Download
export function IconDownload({ size = 16, className, strokeWidth = 1.75 }: Props) {
  return (
    <svg {...svgProps(size, strokeWidth, className)}>
      <path d="M12 3v12" />
      <path d="M7 10l5 5 5-5" />
      <path d="M3 17h18" />
    </svg>
  )
}

// Upload
export function IconUpload({ size = 16, className, strokeWidth = 1.75 }: Props) {
  return (
    <svg {...svgProps(size, strokeWidth, className)}>
      <path d="M12 21V9" />
      <path d="M7 14l5-5 5 5" />
      <path d="M3 17h18" />
    </svg>
  )
}

// Save
export function IconSave({ size = 16, className, strokeWidth = 1.75 }: Props) {
  return (
    <svg {...svgProps(size, strokeWidth, className)}>
      <path d="M5 3h10l3 3v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z" />
      <path d="M5 7h10" />
      <path d="M9 14h5" />
      <path d="M9 17h5" />
    </svg>
  )
}

// External link — flecha sutil
export function IconExternal({ size = 14, className, strokeWidth = 1.75 }: Props) {
  return (
    <svg {...svgProps(size, strokeWidth, className)}>
      <path d="M14 5h5v5" />
      <path d="M10 14L19 5" />
      <path d="M5 7v12h12" />
    </svg>
  )
}

// Check / Success
export function IconCheck({ size = 16, className, strokeWidth = 2 }: Props) {
  return (
    <svg {...svgProps(size, strokeWidth, className)}>
      <path d="M5 13l4 4L19 7" />
    </svg>
  )
}
