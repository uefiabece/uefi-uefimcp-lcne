"""
Ferramentas de navegação curricular — específicas para a Licenciatura em
Ciências Naturais e Exatas (LCNE) da UFABC.

Estas ferramentas complementam as ferramentas genéricas do template com
funcionalidades voltadas para a navegação do currículo de um curso inteiro,
não apenas de uma disciplina individual. A LCNE é um curso interdisciplinar
de primeiro ciclo: a partir dela o estudante segue para uma licenciatura
específica de segundo ciclo (ex: Licenciatura em Ciências Biológicas).
"""

from __future__ import annotations

from mcp import types

from ..resources.loader import ContentLoader


def register_curriculum_tools(
    tools: list[types.Tool],
    handlers: dict,
    loader: ContentLoader,
    config: dict,
) -> None:
    if not config.get("features", {}).get("curriculum_navigation"):
        return

    course_name = config.get("course_name", "Licenciatura em Ciências Naturais e Exatas")
    metadata = config.get("metadata", {})
    ppc_version = metadata.get("ppc_version") or "vigente"
    ppc_versions = metadata.get("ppc_versions_available") or []

    ppc_schema: dict = {
        "type": "string",
        "description": f"Versão do PPC a consultar. Padrão: {ppc_version}.",
    }
    if ppc_versions:
        ppc_schema["enum"] = ppc_versions

    # --- get_curriculum_structure ---
    tools.append(
        types.Tool(
            name="get_curriculum_structure",
            description=(
                f"Retorna a estrutura curricular completa da {course_name}: "
                "disciplinas obrigatórias (incluindo as pedagógicas), de opção limitada, "
                "livres, estágio supervisionado, extensão e atividades complementares. "
                "Baseado nos arquivos carregados em content/syllabus/."
            ),
            inputSchema={
                "type": "object",
                "properties": {"ppc": ppc_schema},
                "required": [],
            },
        )
    )

    async def handle_get_curriculum_structure(args: dict) -> str:
        ppc = args.get("ppc", ppc_version)

        # Try to find PPC-specific syllabus files first
        all_syllabus = loader.get_section("syllabus")
        ppc_items = [i for i in all_syllabus if ppc in i["name"]]
        items = ppc_items if ppc_items else all_syllabus

        if not items:
            # Fall back to searching bibliography for PPC documents
            bib_results = loader.search(f"ppc_{ppc}", section="bibliography")
            bib_results += loader.search("obrigatória", section="bibliography")
            if bib_results:
                snippets = "\n\n".join(r["snippet"] for r in bib_results[:5])
                return (
                    f"## Estrutura Curricular — {course_name} (PPC {ppc})\n\n"
                    f"[Extraído da bibliografia]\n\n{snippets}\n\n"
                    f"[O assistente deve apresentar a estrutura curricular completa "
                    f"com base nos trechos acima e no seu conhecimento da {course_name}.]"
                )
            return (
                "Nenhum arquivo de ementa carregado ainda. "
                "Adicione arquivos em content/syllabus/ ou verifique se os PDFs do PPC "
                "estão em content/bibliography/ e se o suporte a PDF está instalado "
                "(`pip install -e \".[pdf]\"`). "
            )

        combined = "\n\n---\n\n".join(f"# {i['name']}\n\n{i['text']}" for i in items)
        return (
            f"## Estrutura Curricular — {course_name} (PPC {ppc})\n\n"
            f"{combined}"
        )

    handlers["get_curriculum_structure"] = handle_get_curriculum_structure

    # --- list_subjects_by_area ---
    tools.append(
        types.Tool(
            name="list_subjects_by_area",
            description=(
                "Lista as disciplinas da LCNE agrupadas por área "
                "(ex: Matemática, Física, Química, Biologia, Ciências da Terra, "
                "Educação e Práticas de Ensino). "
                "Útil para explorar opções limitadas e livres."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": (
                            "Área a filtrar (ex: 'matemática', 'física', 'química', 'biologia', "
                            "'educação', 'práticas de ensino', 'estágio'). Omita para listar todas."
                        ),
                    }
                },
                "required": [],
            },
        )
    )

    async def handle_list_subjects_by_area(args: dict) -> str:
        area = args.get("area", "").strip().lower()

        query = area if area else "disciplina"
        results = loader.search(query, section="syllabus")
        if not results:
            results = loader.search(query, section="bibliography")

        context_block = ""
        if results:
            snippets = "\n\n".join(r["snippet"] for r in results[:6])
            context_block = f"\n\n## Trechos relevantes dos materiais\n\n{snippets}"

        area_label = f" — Área: {area.title()}" if area else ""
        return (
            f"## Disciplinas da {course_name}{area_label}\n"
            f"{context_block}\n\n"
            f"[O assistente deve listar as disciplinas da LCNE"
            f"{' na área de ' + area if area else ''}, "
            f"organizadas por categoria (obrigatória / opção limitada / livre), "
            f"separando conteúdos científicos e disciplinas pedagógicas, "
            f"baseando-se nos materiais acima e no conhecimento do currículo da LCNE da UFABC.]"
        )

    handlers["list_subjects_by_area"] = handle_list_subjects_by_area

    # --- get_disciplinas_limitadas ---
    tools.append(
        types.Tool(
            name="get_disciplinas_limitadas",
            description=(
                "Retorna as disciplinas de opção limitada da LCNE e as disciplinas com "
                "oferta restrita, a partir do PPC ou do planejamento de oferta carregado. "
                "Útil para planejar a matrícula com antecedência."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "area": {
                        "type": "string",
                        "description": "Filtrar por área ou nome de disciplina (opcional).",
                    }
                },
                "required": [],
            },
        )
    )

    async def handle_get_disciplinas_limitadas(args: dict) -> str:
        area = args.get("area", "").strip()

        results = loader.search("limitad", section="syllabus")
        results += loader.search("limitad", section="bibliography")
        if area:
            results = [r for r in results if area.lower() in r["snippet"].lower()] or results

        if not results:
            return (
                "Nenhum material sobre disciplinas de opção limitada encontrado. "
                "Adicione o PPC da LCNE ou a lista de oferta em content/bibliography/ "
                "e verifique se o suporte a PDF está instalado "
                "(`pip install -e \".[pdf]\"`). "
            )

        snippets = "\n\n".join(r["snippet"] for r in results[:8])
        filter_note = f" (filtrado por: '{area}')" if area else ""
        return (
            f"## Disciplinas de Opção Limitada{filter_note}\n\n"
            f"{snippets}\n\n"
            f"[O assistente deve apresentar as disciplinas de opção limitada "
            f"listadas nos trechos acima de forma organizada, indicando nomes e códigos.]"
        )

    handlers["get_disciplinas_limitadas"] = handle_get_disciplinas_limitadas

    # --- get_progression_requirements ---
    tools.append(
        types.Tool(
            name="get_progression_requirements",
            description=(
                "Retorna os requisitos de progressão e formatura da LCNE: créditos mínimos "
                "por categoria, estágio supervisionado, prática como componente curricular, "
                "extensão, coeficientes, jubilamento e regras de passagem para as "
                "licenciaturas específicas de segundo ciclo."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": (
                            "Aspecto específico a consultar, ex: 'estágio supervisionado', "
                            "'extensão', 'segundo ciclo', 'reserva de vaga', "
                            "'coeficiente de rendimento'."
                        ),
                    }
                },
                "required": [],
            },
        )
    )

    async def handle_get_progression_requirements(args: dict) -> str:
        topic = args.get("topic", "").strip()

        query = topic if topic else "créditos"
        results = loader.search(query, section="syllabus")
        if not results:
            results = loader.search(query, section="bibliography")

        context_block = ""
        if results:
            snippets = "\n\n".join(r["snippet"] for r in results[:5])
            context_block = f"\n\n## Trechos relevantes dos materiais\n\n{snippets}"

        topic_note = f" — {topic.title()}" if topic else ""
        return (
            f"## Requisitos de Progressão e Formatura — {course_name}{topic_note}\n"
            f"{context_block}\n\n"
            f"[O assistente deve descrever os requisitos{' relacionados a ' + topic if topic else ''} "
            f"para progressão e formatura na LCNE da UFABC (PPC {ppc_version}), "
            f"baseando-se nos materiais acima e no conhecimento do PPC. "
            f"Se não houver material carregado, avise que a resposta não está fundamentada "
            f"nos documentos oficiais.]"
        )

    handlers["get_progression_requirements"] = handle_get_progression_requirements

    # --- plan_academic_journey ---
    tools.append(
        types.Tool(
            name="plan_academic_journey",
            description=(
                "Gera um planejamento acadêmico sugerido para a LCNE, "
                "considerando o quadrimestre atual, disciplinas já cursadas e a "
                "licenciatura específica pretendida no segundo ciclo. "
                "Sugere disciplinas para os próximos quadrimestres."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "current_quarter": {
                        "type": "integer",
                        "description": "Quadrimestre atual na UFABC (contando desde o ingresso na LCNE).",
                    },
                    "completed_subjects": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Lista de disciplinas já concluídas (nomes ou códigos).",
                    },
                    "target_second_cycle": {
                        "type": "string",
                        "description": (
                            "Licenciatura específica pretendida no segundo ciclo, ex: "
                            "'Licenciatura em Ciências Biológicas'."
                        ),
                    },
                },
                "required": ["current_quarter"],
            },
        )
    )

    async def handle_plan_academic_journey(args: dict) -> str:
        quarter = args.get("current_quarter", 1)
        completed = args.get("completed_subjects", [])
        target = args.get("target_second_cycle", "")

        # Pull curriculum context
        syllabus_items = loader.get_section("syllabus")
        syllabus_text = (
            "\n\n".join(i["text"] for i in syllabus_items)
            if syllabus_items
            else "Nenhuma ementa carregada."
        )

        completed_note = (
            f"\nDisciplinas concluídas: {', '.join(completed)}" if completed else ""
        )
        target_note = f"\nLicenciatura pretendida no segundo ciclo: {target}" if target else ""

        return (
            f"## Planejamento Acadêmico — {course_name}\n"
            f"**Quadrimestre atual:** {quarter}"
            f"{completed_note}"
            f"{target_note}\n\n"
            f"## Referência curricular\n\n{syllabus_text}\n\n"
            f"[O assistente deve sugerir um planejamento quadrimestral a partir do "
            f"quadrimestre {quarter}, priorizando pré-requisitos das disciplinas "
            f"obrigatórias ainda não cursadas, distribuindo as disciplinas pedagógicas e o "
            f"estágio supervisionado ao longo do curso"
            f"{' e antecipando as disciplinas relevantes para ' + target if target else ''}. "
            f"Apresente o plano em tabela ou lista por quadrimestre.]"
        )

    handlers["plan_academic_journey"] = handle_plan_academic_journey
