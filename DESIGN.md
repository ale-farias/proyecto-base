# Design System - Sistema de Gestión de Turnos

## Paleta de Colores

### Modo Claro (Light Mode)

| Variable | Color | Uso |
|----------|-------|-----|
| `--color-fondo` | `#fafbfc` | Fondo principal de la página |
| `--color-fondo-secundario` | `#f1f5f9` | Fondos alternos, secciones |
| `--color-fondo-card` | `#ffffff` | Tarjetas, modales |
| `--color-texto` | `#0f172a` | Texto principal (contraste 14.5:1 con fondo) |
| `--color-texto-claro` | `#475569` | Texto secundario |
| `--color-texto-muted` | `#64748b` | Texto terciario, placeholders |
| `--color-primario` | `#0f172a` | Botones primarios, headings |
| `--color-secundario` | `#1e293b` | Hover states |
| `--color-acento` | `#f59e0b` | Destacados, estrellas, CTAs |
| `--color-acento-2` | `#ec4899` | Acento secundario |
| `--color-borde` | `#e2e8f0` | Bordes de elementos |
| `--color-borde-claro` | `#f1f5f9` | Bordes ligeros |

### Modo Oscuro (Dark Mode)

| Variable | Color | Uso | Contraste |
|----------|-------|-----|-----------|
| `--color-fondo` | `#0a0a0a` | Fondo principal | ✅ 15:1 |
| `--color-fondo-secundario` | `#141414` |Fondos alternos | ✅ 15:1 |
| `--color-fondo-card` | `#1a1a1a` | Tarjetas, modales | ✅ 14:1 |
| `--color-texto` | `#ffffff` | Texto principal | - |
| `--color-texto-claro` | `#d4d4d4` | Texto secundario | ✅ 7.5:1 |
| `--color-texto-muted` | `#a0a0a0` | Texto terciario | ✅ 4.5:1 |
| `--color-primario` | `#3b82f6` | Botones, links |
| `--color-secundario` | `#60a5fa` | Hover states |
| `--color-acento` | `#fbbf24` | Estrellas, highlights |
| `--color-acento-2` | `#f472b6` | Acento secundario |
| `--color-borde` | `#2a2a2a` | Bordes |
| `--color-borde-claro` | `#1f1f1f` | Bordes ligeros |

### Estados (Alertas y Feedback)

| Estado | Color | Fondo | Uso |
|--------|-------|-------|-----|
| Exito | `#10b981` | `#d1fae5` / `#022c22` | Confirmaciones |
| Error | `#ef4444` | `#fee2e2` / `#450a0a` | Errores, acciones destructivas |
| Advertencia | `#f59e0b` | `#fef3c7` / `#451a03` | Avisos importantes |
| Info | `#3b82f6` | `#dbeafe` / `#172554` | Información |

## Tipografía

### Familia Principal

```css
font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
```

### Escala

| Elemento | Tamaño | Peso | Line-height |
|----------|-------|------|-------------|
| h1 | 2.5rem (40px) | 700 | 1.2 |
| h2 | 2rem (32px) | 700 | 1.2 |
| h3 | 1.5rem (24px) | 700 | 1.2 |
| h4 | 1.25rem (20px) | 700 | 1.2 |
| Body | 0.9375rem (15px) | 400 | 1.6 |
| Small | 0.875rem (14px) | 400 | 1.5 |
| Caption | 0.8125rem (13px) | 400 | 1.4 |

## Espaciado

- Base: 4px
- xs: 4px, sm: 8px, md: 16px, lg: 24px, xl: 32px, 2xl: 48px

## Sombras

```css
--sombra-pequeña: 0 1px 2px rgba(0, 0, 0, 0.05);
--sombra-media: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--sombra-grande: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--sombra-xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
```

## Interacciones

### Transiciones

```css
--transicion-rapida: all 0.15s ease;
--transicion: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
--transicion-lenta: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
```

### Botones

- Hover: translateY(-1px) + box-shadow
- Active: scale(0.97)
- Focus: outline-offset 2px

### Tarjetas de Servicio

- Hover: translateY(-2px) + border-color + box-shadow
- Click feedback: scale(0.98)

### Formularios

- Error: shake animation + border-color error
- Focus: border-color primary + box-shadow 3px
- Loading button: spinner animation

## Accesibilidad

- Contraste mínimo: 4.5:1 para texto normal
- Targets táctiles: mínimo 44x44px
- Focus visible en todos los elementos interactivos