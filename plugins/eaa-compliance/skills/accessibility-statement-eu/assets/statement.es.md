# Declaración de accesibilidad (ES)

> **Plantilla.** Sustituir todos los `{{MARCADOR}}`. Eliminar esta nota antes de publicar. No inventar el contacto de comentarios, el plazo de respuesta ni la autoridad competente — marcar cualquier valor ausente como `PENDIENTE DEL CLIENTE` y resolverlo antes de la publicación. Las denominaciones y bases jurídicas deben verificarse para el Estado miembro correspondiente (`VERIFY`).

---

# Declaración de accesibilidad de {{NOMBRE_DEL_PRODUCTO}}

{{RAZÓN_SOCIAL}} se compromete a hacer que {{NOMBRE_DEL_PRODUCTO}} sea accesible de conformidad con los requisitos de la Directiva (UE) 2019/882, tal como ha sido transpuesta al ordenamiento nacional aplicable.

**Ámbito:** {{ÁMBITO — sitio web, aplicación, servicio y versión}}
**Fecha de la declaración:** {{FECHA_PUBLICADA}}
**Última revisión:** {{FECHA_REVISADA}}
**Última evaluación:** {{FECHA_EVALUADA}}

## Estado de conformidad

{{NOMBRE_DEL_PRODUCTO}} se ha evaluado conforme a las **Web Content Accessibility Guidelines (WCAG) 2.1 nivel AA**{{, y a la norma EN 301 549 cuando resulte aplicable}}.

**Estado de conformidad: {{PLENAMENTE CONFORME | PARCIALMENTE CONFORME | NO CONFORME}}.**

{{EN CASO DE CONFORMIDAD PARCIAL — indicar con precisión lo que no se cumple:}}
Los siguientes elementos aún no cumplen plenamente la norma. Cada uno tiene un responsable y una fecha objetivo:

| Área | Limitación | Responsable | Fecha objetivo |
|---|---|---|---|
| {{ÁREA}} | {{LIMITACIÓN}} | {{CLIENTE | TERCERO | PLATAFORMA}} | {{FECHA}} |

{{EN CASO DE CRITERIOS NO EVALUADOS — declararlo en lugar de asumirlo:}}
Los siguientes criterios no fueron evaluados en la última evaluación y se consignan como **no evaluados**, no como conformes: {{LISTA}}. Las pruebas necesarias para cerrarlos están previstas para el {{FECHA}}.

## Contenidos no accesibles

{{LIMITACIONES — ser específico y nombrar a la parte responsable. Nunca dar a entender control sobre una superficie ajena.}}

- **{{COMPONENTE_DE_TERCERO}}** lo proporciona {{PROVEEDOR}} y se muestra fuera de nuestro control. {{DESCRIBIR_LA_BARRERA}}. Hemos solicitado su corrección por escrito el {{FECHA}} y {{ESTAMOS_EVALUANDO_ALTERNATIVAS | ESPERAMOS_RESPUESTA}}.
- **{{SUPERFICIE_DE_PLATAFORMA}}** — por ejemplo, un proceso de pago alojado o un marco de pago — no es modificable por nuestra parte. {{DESCRIBIR_LA_LIMITACIÓN}}.

## Medidas para garantizar la accesibilidad

- {{CADENCIA_DE_PRUEBAS}} — por ejemplo: análisis automatizado frente a WCAG 2.1 A y AA en la integración continua en cada publicación, con bloqueo ante nuevas incidencias.
- **Pruebas manuales** de los siguientes recorridos de cliente en cada publicación, únicamente con teclado y con {{LECTOR_DE_PANTALLA_Y_VERSIÓN}}: {{RECORRIDOS — habitualmente cesta, pago, inicio de sesión}}.
- {{PROCESO_DE_CORRECCIÓN}} — cómo se priorizan, ejecutan y cierran los hallazgos.
- {{FORMACIÓN}} — requisitos de accesibilidad para los equipos de diseño y desarrollo.

## Combinaciones probadas

{{NOMBRE_DEL_PRODUCTO}} se ha probado con las siguientes combinaciones:

| Navegador | Sistema operativo | Tecnología de apoyo |
|---|---|---|
| {{NAVEGADOR_VERSIÓN}} | {{SO_VERSIÓN}} | {{TA_VERSIÓN, o «ninguna»}} |

{{SEÑALAR_CUALQUIER_DETERIORO_CONOCIDO_EN_UNA_COMBINACIÓN_NO_PROBADA,_O_INDICAR_QUE_LAS_DEMÁS_COMBINACIONES_NO_FUERON_EVALUADAS.}}

## Comentarios e información de contacto

Si encuentra una barrera de accesibilidad, o si necesita la información en otro formato, contacte con nosotros:

- **Correo electrónico:** {{CORREO_SUPERVISADO}}
- **Formulario:** {{URL_FORMULARIO}}
- **Correo postal:** {{DIRECCIÓN_POSTAL}}

Indíquenos la página o pantalla afectada, qué intentaba hacer y qué navegador y tecnología de apoyo utilizaba. **Respondemos en un plazo de {{N}} días laborables** y proponemos una solución en los {{N}} días laborables siguientes a esa respuesta.

Puede solicitar gratuitamente cualquier contenido de este sitio en un formato alternativo accesible.

## Procedimiento de reclamación

Si no queda satisfecho con nuestra respuesta, puede dirigirse a la autoridad competente:

{{AUTORIDAD_NACIONAL — tomar de references/details.md o marcar VERIFY. No inventar nunca la denominación de una autoridad.}}

- **Autoridad:** {{NOMBRE_AUTORIDAD}} `{{VERIFY — comprobar contra el instrumento nacional vigente}}`
- **Contacto:** {{CONTACTO_AUTORIDAD}}
- **Base jurídica:** {{CITA_INSTRUMENTO_NACIONAL}} por la que se transpone la Directiva (UE) 2019/882

{{CUANDO_PROCEDA,_mencionar el procedimiento de resolución alternativa de litigios o la vía de reclamación disponible para los consumidores en ese Estado miembro.}}

## Elaboración de esta declaración

- **Método:** {{MÉTODO — análisis automatizado, análisis estático del código fuente, pruebas manuales de teclado, pruebas con lector de pantalla, y por quién}}
- **Evaluado por:** {{EVALUADOR — equipo interno, proveedor designado o «autoevaluación»}}
- **Alcance evaluado:** {{RUTAS,_PLANTILLAS_Y_VERSIONES_EVALUADAS}}
- **Excluido:** {{QUÉ_NO_SE_EVALUÓ_Y_POR_QUÉ}}

Esta declaración es documentación elaborada a partir de una evaluación técnica. No constituye una certificación de conformidad ni asesoramiento jurídico. Únicamente un evaluador independiente puede certificar la conformidad, y cualquier cuestión jurídica sobre la aplicabilidad de la Directiva (UE) 2019/882 debe confirmarla un abogado cualificado en el Estado miembro correspondiente.

---

**{{RAZÓN_SOCIAL}}** · {{URL_PÁGINA_CONTACTO}} · Esta declaración se publicó el {{FECHA_PUBLICADA}}.
