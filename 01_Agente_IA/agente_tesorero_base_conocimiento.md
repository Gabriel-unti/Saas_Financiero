# Guía de Estudio: Implementación de un Agente Tesorero con IA para PYMEs Peruanas

Esta guía proporciona una síntesis técnica y estratégica para el desarrollo de un agente de inteligencia artificial especializado en la gestión de tesorería. El enfoque se centra en la automatización del procesamiento de datos bancarios, la clasificación inteligente de transacciones, la integración con fuentes oficiales de datos económicos (BCRP) y la visualización de flujos de caja.

---

## 1. Capas Técnicas del Agente Tesorero

### Capa I: Procesamiento y Parsing de Documentos (PDF y Excel)
El desafío fundamental en la tesorería es la extracción precisa de datos desde extractos bancarios. Basado en estudios comparativos de herramientas de parsing, se identifican dos enfoques:

*   **Herramientas Basadas en Reglas:**
    *   **PyMuPDF y pypdfium2:** Recomendadas para la extracción de texto general debido a su alto rendimiento en métricas de similitud de Levenshtein y puntuación BLEU-4. Son ideales para mantener la integridad de los párrafos y el orden de las palabras.
    *   **pdfplumber y pdfminer.six:** Útiles para análisis de diseño automático, aunque pueden presentar variaciones de rendimiento según el formato del banco.
    *   **Camelot y Tabula:** Especializadas en la extracción de tablas. Camelot destaca en documentos con líneas demarcadas (modo *lattice*), mientras que Tabula es eficiente en tablas basadas en espacios en blanco (modo *stream*).

*   **Herramientas Basadas en Aprendizaje Profundo (Deep Learning):**
    *   **Table Transformer (TATR):** Superior para la detección de tablas complejas, especialmente en documentos financieros, utilizando métricas de Intersección sobre Unión (IoU).
    *   **Nougat:** Recomendado si el extracto contiene fórmulas matemáticas complejas o estructuras no convencionales que las herramientas de reglas no logran procesar.

### Capa II: Clasificación Automática de Transacciones
Una vez extraídos los datos, el agente debe categorizar cada movimiento (Planilla, Proveedores, Impuestos, Ingresos).
*   **Búsqueda Semántica:** Utilización de *Sentence Transformers* para identificar la intención de una transacción basándose en la descripción del movimiento bancario.
*   **Etiquetado y Supervisión Débil:** Herramientas como **Argilla** permiten implementar flujos de trabajo de *Active Learning* y supervisión débil para etiquetar grandes volúmenes de transacciones bancarias de forma eficiente, permitiendo que el modelo aprenda de feedback constante.

### Capa III: Conversión de Moneda y Conexión con BCRP
Para la gestión multi-moneda (USD a PEN), es imperativo el uso de tipos de cambio (TC) oficiales.
*   **Librería `bcrpy`:** Cliente Python para la API del Banco Central de Reserva del Perú.
*   **Patrón de Código:**
    ```text
    import bcrpy
    banco = bcrpy.Marco()
    banco.codes = ["PN01288PM"] # Código de ejemplo para series de datos
    banco.start = "2023-1"
    df = banco.GET()
    ```
*   **Recomendación Técnica:** Usar la librería `rlish` para guardar y cargar DataFrames de manera segura y portable, superando las limitaciones de *pickle*.

### Capa IV: Proyección de Flujo de Caja y Power BI
*   **Proyección:** El sistema debe consolidar los datos clasificados para proyectar saldos en horizontes de 7 a 14 días.
*   **Actualización vía API:** Los datos procesados se envían a Power BI a través de su API para actualizar tableros de control en tiempo real, permitiendo a la PYME visualizar su liquidez de forma inmediata.

---

## 2. Glosario de Términos Clave

| Término | Definición Técnica |
| :--- | :--- |
| **BLEU (Bilingual Evaluation Understudy)** | Métrica que mide la superposición de n-gramas entre el texto extraído y el texto real; evalúa el orden y la identificación de palabras. |
| **Similitud de Levenshtein** | Medida de la distancia entre dos cadenas de texto basada en el número de operaciones (inserción, eliminación, sustitución) necesarias para transformarlas. |
| **IoU (Intersection over Union)** | Métrica utilizada para evaluar la precisión en la detección de tablas, comparando el área de superposición entre la predicción y el valor real. |
| **Supervisión Débil (Weak Supervision)** | Enfoque de aprendizaje donde se utilizan fuentes de ruido o reglas heurísticas para etiquetar datos a escala, ideal para clasificar transacciones bancarias. |
| **Búsqueda Semántica** | Técnica que utiliza modelos de lenguaje para encontrar información basada en el significado del contexto en lugar de coincidencias exactas de palabras clave. |
| **Parsing de PDF** | Proceso de convertir las instrucciones de colocación de caracteres de un archivo PDF en texto estructurado legible por máquina. |

---

## 3. Cuestionario de Práctica (Respuestas Cortas)

1.  **¿Qué librería de Python se recomienda para obtener el tipo de cambio oficial en Perú y qué objeto principal utiliza?**
2.  **¿Cuál es la diferencia principal entre el modo *lattice* y el modo *stream* en Camelot?**
3.  **¿Por qué se prefiere la similitud de Levenshtein normalizada sobre la distancia de Levenshtein estándar?**
4.  **En la detección de tablas, ¿qué herramienta de aprendizaje profundo demuestra mayor versatilidad según el contexto financiero?**
5.  **¿Qué ventaja ofrece la librería `rlish` frente a `pickle` en el manejo de DataFrames?**

---

## 4. Temas para Ensayos y Profundización

### Análisis Comparativo de Parsing
*Argumente sobre las ventajas y desventajas de utilizar herramientas basadas en reglas (como PyMuPDF) frente a modelos basados en visión (como Nougat o TATR) para el procesamiento de extractos bancarios que contienen tanto tablas extensas como gráficos de comportamiento de saldo.*

### Ética y Precisión en la Clasificación Financiera
*Explique la importancia de la supervisión humana en los flujos de trabajo de "Active Learning" al clasificar transacciones críticas como el pago de impuestos y planillas. ¿Cómo impacta un error de clasificación en la proyección de flujo de caja de 14 días de una PYME?*

### Integración de APIs en la Gestión de Tesorería
*Desarrolle una propuesta técnica sobre cómo la integración de la API del BCRP y la API de Power BI transforma la toma de decisiones en una PYME peruana, pasando de un registro manual en Excel a un Agente Tesorero automatizado.*