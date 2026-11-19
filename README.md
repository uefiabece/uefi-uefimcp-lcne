# uefi-uefimcp-lcne

Servidor MCP da **Licenciatura em Ciências Naturais e Exatas (LCNE)**, UFABC. Nível: **curso** (primeiro ciclo, interdisciplinar). É a porta de entrada para as licenciaturas específicas de segundo ciclo, como a Licenciatura em Ciências Biológicas (`uefi-uefimcp-bio`).

## Origem

Derivado de [`uefi-uefimcp`](https://github.com/uefiabece/uefi-uefimcp) por `git clone`
(commit de origem registrado em `config/subject.json`), sem importar materiais acadêmicos.

- Do `uefi-uefimcp-bct`: leitura opcional de PDF no `ContentLoader` e ferramentas de navegação curricular (`src/tools/curriculum.py`, adaptado à LCNE: disciplinas pedagógicas, estágio supervisionado e licenciatura de segundo ciclo pretendida).
- Do `uefi-uefimcp-neuro`: SDK MCP restrito à v1 (`mcp>=1.27,<2`), `config/mcp.example.json` e o teste de conexão `scripts/check_mcp.py`.

```text
uefi-uefimcp
  ├── uefi-uefimcp-bct  ──→ Bacharelados (comp, dados, bio/bacharelado, ...)
  └── uefi-uefimcp-lcne ──→ Licenciaturas (bio/licenciatura, ...)
```

## Executar

Requer Python 3.11 ou superior. No diretório deste repositório:

```sh
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[pdf]"
.venv/Scripts/python run.py
```

O processo usa transporte **stdio**: deve ser iniciado por um cliente MCP.
Em Linux/macOS, use `.venv/bin/python`.

## Conectar

Claude Code:

```sh
claude mcp add --scope user uefi-uefimcp-lcne -- "CAMINHO_ABSOLUTO/uefi-uefimcp-lcne/.venv/Scripts/python.exe" "CAMINHO_ABSOLUTO/uefi-uefimcp-lcne/run.py"
```

Outros clientes: veja `config/mcp.example.json`.

## Ferramentas

17 ferramentas:

- **Conteúdo / ensino / exercícios (template):** `get_syllabus`, `get_bibliography`, `get_past_exams`, `search_content`, `get_notes`, `explain_concept`, `get_topic_outline`, `generate_study_plan`, `get_exercises`, `solve_exercise`, `generate_exercise`, `generate_flashcards`
- **Navegação curricular** (`curriculum_navigation: true`): `get_curriculum_structure`, `list_subjects_by_area`, `get_disciplinas_limitadas`, `get_progression_requirements`, `plan_academic_journey`

Prompts: `teach` e `solve`.

## Conteúdo

As pastas de `content/` estão vazias. Sugestões:

- `content/bibliography/` — PPC da LCNE (PDF), planejamento de oferta, normas de estágio
- `content/syllabus/curriculo_lcne.md` — síntese estrutural do currículo (como `curriculo_bct.md` no BCT)

Ao adicionar o PPC, preencha `ppc_version`, `ppc_versions_available`, `total_credits_approx`,
`duration_years` e a lista `second_cycle_courses` em `config/subject.json`.
Sem materiais, as consultas retornam a ausência de conteúdo.

## Verificar

```sh
.venv/Scripts/python scripts/check_mcp.py
```
