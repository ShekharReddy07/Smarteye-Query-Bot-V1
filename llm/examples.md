EXAMPLES (QUESTION → JSON RESPONSE)

--------------------------------
Example 1
--------------------------------
Q: How many double duty workers today?

{
  "sql": "SELECT COUNT(*) FROM AttendanceReport WHERE Work_Type = 'DD'",
  "params": []
}

--------------------------------
Example 2
--------------------------------
Q: Show outsiders in weaving

{
  "sql": "SELECT * FROM AttendanceReport WHERE Category = 'OUTSIDER' AND Department = 'WEAVING'",
  "params": []
}

--------------------------------
Example 3
--------------------------------
Q: Absent employees today

{
  "sql": "SELECT * FROM AttendanceReport WHERE Status = 'A'",
  "params": []
}

--------------------------------
Example 4 (Unsupported)
--------------------------------
Q: Delete attendance data

{
  "unsupported": true,
  "message": "This query is not supported yet. We will work on that."
}

--------------------------------
Example 5 (Unsupported)
--------------------------------
Q: Give me productivity analysis

{
  "unsupported": true,
  "message": "This query is not supported yet. We will work on that."
}

--------------------------------
Example: Double Duty with Date Range
--------------------------------
Q: show double duty between 10/12/2025 to 31/12/2025

{
  "sql": "SELECT * FROM AttendanceReport WHERE Work_Type = 'DD' AND WDate BETWEEN ? AND ?",
  "params": ["2025-12-10", "2025-12-31"]
}
