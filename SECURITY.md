# Política de seguridad

## Reportar vulnerabilidades

Si descubres una vulnerabilidad de seguridad en Lupa, **no abras un issue público**. En su lugar:

1. Abre un [security advisory privado](https://github.com/lupafarma/web/security/advisories/new) en GitHub
2. O contacta directamente a los mantenedores

## Tipos de vulnerabilidad relevantes

Dado que Lupa es una aplicación 100% local sin backend, los vectores de ataque relevantes incluyen:

- **Filtración de datos a través de network requests no documentados.** Si descubres que Lupa hace cualquier petición de red tras la carga inicial, repórtalo. Esto sería una violación grave de la promesa de privacidad del producto.
- **Inyección de scripts** o vulnerabilidades XSS en el procesamiento de datos de entrada del usuario.
- **Dependencias con vulnerabilidades conocidas.** Si una dependencia tiene un CVE relevante, repórtalo aunque el impacto parezca menor.
- **Errores en los cálculos de detección** que produzcan falsos negativos sistemáticos (es decir, casos donde Lupa debería detectar una sobrecarga pero no lo hace).

## Lo que NO es una vulnerabilidad de seguridad

- Errores tipográficos en el contenido en castellano
- Fallos visuales que no afecten al cálculo
- Discrepancias entre los hallazgos de Lupa y otras herramientas (estos son issues funcionales, no vulnerabilidades)

## Tiempo de respuesta

Procuramos responder en un plazo de **7 días naturales**. Si la vulnerabilidad es crítica y reproducible, intentaremos publicar un parche en un plazo de **30 días**.

## Reconocimiento

Si reportas una vulnerabilidad válida y deseas ser reconocido públicamente, te incluiremos en los créditos del proyecto.
