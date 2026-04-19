# Publish To GitHub

## Recommended repository name

`executive-applied-ai-showcase`

## Suggested GitHub description

Compact portfolio of recruiter-friendly Applied AI, LLM, analytics and SQL examples focused on business execution and decision support.

## Suggested topics

- applied-ai
- llm
- rag
- generative-ai
- python
- sql
- analytics
- decision-support
- fraud-detection
- reporting
- power-bi
- ai-automation

## Publish checklist

- Use the contents of this folder as the root of the GitHub repository.
- Keep `README.md` as the homepage.
- Keep `assets/banner.svg` for the visual header.
- Keep `.github/workflows/smoke-tests.yml` to show basic repository discipline.
- Keep `.github/workflows/deploy-pages.yml` and `docs/` for a static GitHub Pages demo hub.
- Keep `requirements_optional.txt` to document the optional FastAPI and Streamlit entrypoints.

## GitHub Pages

The repository is now ready for a static Pages deployment from `docs/`.

- In GitHub, go to `Settings` -> `Pages`.
- Set the source to `GitHub Actions`.
- After the next push, the static demo hub should deploy from `.github/workflows/deploy-pages.yml`.

Once enabled, the expected Pages URL should follow the standard pattern:

`https://vinbourg.github.io/executive-applied-ai-showcase/`

Useful static entry points:

- `https://vinbourg.github.io/executive-applied-ai-showcase/`
- `https://vinbourg.github.io/executive-applied-ai-showcase/kpi-demo.html`
- `https://vinbourg.github.io/executive-applied-ai-showcase/sql-copilot.html`
- `https://vinbourg.github.io/executive-applied-ai-showcase/lead-automation.html`

## Recommended first impression

When sharing the repository, point reviewers first to:

1. `01_RAG_Knowledge_Assistant`
2. `13_AI_SQL_Analytics_Copilot`
3. `09_n8n_Lead_Enrichment_Automation`
4. `15_n8n_Document_Intake_Approval`
5. `16_Cloud_Data_Platform_Governance`
