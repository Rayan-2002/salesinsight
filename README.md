## Author

Rayan HEDIDAR

# SalesInsight — AI Business Data Assistant

An AI engineering portfolio project exploring how natural-language questions can be answered using structured sales data and the Model Context Protocol (MCP).

**Status: work in progress — planning and initial setup.**

## The problem

Business users often need answers about revenue, products, and regional performance without writing SQL. SalesInsight aims to turn their questions into calls to predefined analytics tools and explain the returned results.

Example questions:
- What was our monthly revenue between January and June 2026?
- Which five products generated the most revenue in September 2026?
- How did sales by region change between August and September 2026?

## Planned first version

- A reproducible synthetic sales dataset in SQLite.
- Three read-only analytics tools exposed through an MCP server.
- An LLM integration that selects tools and supplies structured arguments.
- A Streamlit interface displaying answers, tables, and tool-call evidence.
- An evaluation set of 20–30 questions with expected database results.

SQL and Python will calculate business metrics. The model will interpret questions and explain the results. This separation does not guarantee correct answers: tool selection, arguments, and final explanations will also be evaluated.

## Planned architecture

1. The user submits a question through the Streamlit interface.
2. The host application discovers tools through its MCP client and supplies their definitions to the model.
3. The model requests a tool call with structured arguments.
4. The host validates the request and uses its MCP client to call the MCP server.
5. The server executes the corresponding parameterized SQL query against SQLite.
6. The host sends the tool result back to the model for an explanation and displays the answer with supporting data.

The host manages the interaction; the MCP client implements protocol communication. The model itself does not directly connect to the database.

## Planned technology stack

| Component | Technology |
| --- | --- |
| Application and analytics | Python |
| Data storage | SQLite and SQL |
| Tool integration | MCP Python SDK |
| Language model | Provider and model to be selected |
| Interface | Streamlit |
| Automated checks | pytest |

## Planned analytics tools

| Tool | Purpose |
| --- | --- |
| `sales_by_month(start_date, end_date)` | Return monthly revenue and order counts |
| `top_products(start_date, end_date, limit)` | Rank products by revenue |
| `sales_by_region(start_date, end_date)` | Aggregate revenue by region |

The initial implementation will use predefined queries rather than unrestricted model-generated SQL. Metric definitions, date boundaries, and treatment of cancelled orders will be documented before implementation.

## Roadmap

- [ ] Define the sales schema and metric definitions.
- [ ] Generate reproducible synthetic data.
- [ ] Implement and verify the three SQL analytics functions.
- [ ] Expose the functions through an MCP server.
- [ ] Connect an MCP client and an LLM.
- [ ] Add a minimal chat interface and tool-call display.
- [ ] Handle invalid inputs, missing data, and unsupported questions.
- [ ] Evaluate results and document failure cases.
- [ ] Record a short demonstration.

Target scope: four weeks at approximately ten hours per week. Charts, deployment, authentication, RAG, and multiple agents are outside the first-version scope.

## Evaluation plan

Compare assistant responses with independently verified SQL results. Record tool-selection correctness, argument correctness, numerical accuracy, response latency, and representative failures. Include ambiguous questions and periods with no sales. Publish actual results once available; no accuracy claims are made yet.

## Running the project

Implementation has not started. Dependency installation, database generation, configuration, and launch commands will be added once verified. No API credentials are needed to read this repository. A hosted model may require separate API access and usage charges.

## Data and credentials

Use synthetic data for the public demonstration. Keep local credentials in an ignored `.env` file and publish only placeholder values in `.env.example`. Local databases, logs, virtual environments, and private data are excluded by `.gitignore`. Version-control the future data-generation script so reviewers can reproduce the demo database.

## Learning goals

- Explain MCP host, client, server, and tool responsibilities.
- Understand tool calling, structured arguments, and LLM limitations.
- Design relational data and reliable SQL aggregations.
- Validate model-driven operations and inspect execution evidence.
- Evaluate an AI application against known answers.

## Learning resources and attribution

- [Microsoft MCP for Beginners](https://github.com/microsoft/mcp-for-beginners)
- [Model Context Protocol documentation](https://modelcontextprotocol.io/)

This project is an independent implementation informed by these resources. Any copied or adapted source code will retain applicable license notices and attribution.