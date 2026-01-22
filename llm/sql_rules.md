BUSINESS RULES FOR ATTENDANCE QUERIES

--------------------------------
DOUBLE DUTY (DD)
--------------------------------
Definition:
- Double duty is identified ONLY by:
  Work_Type = 'DD'

Rules:
- If the question asks "how many", "count", or "total":
  → Use COUNT(*)
- If the question asks "show", "list", or "display":
  → Use SELECT *

Restrictions:
- NEVER infer double duty from hours, OT, or grade
- NEVER use any column other than Work_Type

--------------------------------
OUTSIDER
--------------------------------
Definition:
- Outsider is identified ONLY by:
  Category = 'OUTSIDER'

Rules:
- Count outsiders → COUNT(*)
- List outsiders → SELECT *

Restrictions:
- NEVER infer outsider from name, vendor, or department

--------------------------------
ATTENDANCE STATUS
--------------------------------
- Present → Status = 'P'
- Absent  → Status = 'A'

--------------------------------
GENERAL RULES
--------------------------------
- Use WHERE conditions explicitly
- Prefer exact matches
- If date is mentioned (today, yesterday), use appropriate date filter
- If logic is unclear, mark query as unsupported
