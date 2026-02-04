## IMPORTANT AGGREGATION RULES (MANDATORY)

The following rules MUST ALWAYS be followed:

1. For OUTSIDER attendance:
   - Presence is calculated using:
     SUM(WORK_HR) / 8
   - NEVER use COUNT(*)

2. For DOUBLE DUTY attendance:
   - Presence is calculated using:
     SUM(WORK_HR) / 8
   - NEVER use COUNT(*)

3. For OVERTIME attendance:
   - Presence is calculated using:
     SUM(WORK_HR) / 8
   - NEVER use COUNT(*)

4. COUNT(*) is ONLY allowed when explicitly counting records
   (example: "how many records", "how many rows").

5. When user says:
   - "how many outsiders"
   - "how many double duty"
   - "how many overtime"

   It ALWAYS means:
   SUM(WORK_HR) / 8


### Example 1
User: show attendance of nz1073

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE ECode = ?",
  "params": ["NZ1073"]
}

---

### Example 2
User: attendance of nz1073 on 10 dec 2025

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE ECode = ? AND WDate = ?",
  "params": ["NZ1073", "2025-12-10"]
}

---

### Example 3 (Unsupported)
User: who was absent yesterday

Output:
{
  "unsupported": true,
  "message": "This query is not supported yet. We will work on that."
}

---

### Example 4
User: spinning department attendance today

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE Dept_Code = ? AND WDate = CAST(GETDATE() AS DATE)",
  "params": [5]
}

---

### Example 5
User: show all attendance records for weaving hessian dept

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE Dept_Code = ?",
  "params": [10]
}

---

### Example 6 (Unsupported)
User: give attendance report

Output:
{
  "unsupported": true,
  "message": "This query is not supported yet. We will work on that."
}

---

### Example: Employee attendance for date range and department
User: show me the attendance for 731498 between 10/12/2025 to 31/12/2025 in the jute department

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE ECode = ? AND Dept_Code = ? AND WDate BETWEEN ? AND ?",
  "params": ["731498", 1, "2025-12-10", "2025-12-31"]
}

---

### Example: Outsider attendance
User: show outsider attendance

Output:
{
  "sql": "SELECT SUM(Work_HR) / 8 AS Outsider_Present FROM AttendanceReport WHERE Work_Type = ?",
  "params": ["VOUCHER"]
}

---

### Example: Outsider attendance between dates
User: show outsider attendance between 01/01/2025 to 31/12/2025

Output:
{
  "sql": "SELECT SUM(Work_HR) / 8 AS Outsider_Present FROM AttendanceReport WHERE Work_Type = ? AND WDate BETWEEN ? AND ?",
  "params": ["VOUCHER", "2025-01-01", "2025-12-31"]
}

---

### Example: Outsider attendance in jute department
User: show outsider attendance in jute department

Output:
{
  "sql": "SELECT SUM(Work_HR) / 8 AS Outsider_Present FROM AttendanceReport WHERE Work_Type = ? AND Dept_Code = ?",
  "params": ["VOUCHER", 1]
}

---

### Example: Outsider attendance in jute department between dates
User: show outsider attendance in jute department between 01/01/2025 to 31/12/2025

Output:
{
  "sql": "SELECT SUM(Work_HR) / 8 AS Outsider_Present FROM AttendanceReport WHERE Work_Type = ? AND Dept_Code = ? AND WDate BETWEEN ? AND ?",
  "params": ["VOUCHER", 1, "2025-01-01", "2025-12-31"]
}

---

### Example: Display double duty attendance
User: show double duty attendance

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE Work_Type = ?",
  "params": ["DD"]
}

---

### Example: Display double duty present yesterday
User: show double duty present yesterday

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE Work_Type = ? AND WDate = CAST(GETDATE()-1 AS DATE)",
  "params": ["DD"]
}

---

### Example: Display double duty between dates
User: show double duty between 10/12/2025 to 31/12/2025

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE Work_Type = ? AND WDate BETWEEN ? AND ?",
  "params": ["DD", "2025-12-10", "2025-12-31"]
}

---

### Example: Display double duty in jute department
User: show double duty in jute department

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE Work_Type = ? AND Dept_Code = ?",
  "params": ["DD", 1]
}

### Example: double duty present today
User: how many double duty workers are present today

Output:
{
  "sql": "SELECT SUM(WORK_HR)/8 AS Double_Duty_Count FROM AttendanceReport WHERE Work_Type IN (?) AND WDate = CAST(GETDATE()-1 AS DATE)",
  "params": ["DD"]
}

---

### Example: Display overtime attendance
User: show overtime attendance

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE Work_Type IN (?, ?)",
  "params": ["SO", "WO"]
}

---

### Example: Display overtime present yesterday
User: show overtime present yesterday

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE Work_Type IN (?, ?) AND WDate = CAST(GETDATE()-1 AS DATE)",
  "params": ["SO", "WO"]
}

---

### Example: Display overtime between dates
User: show overtime between 10/12/2025 to 31/12/2025

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE Work_Type IN (?, ?) AND WDate BETWEEN ? AND ?",
  "params": ["SO", "WO", "2025-12-10", "2025-12-31"]
}

---

### Example: Display overtime in jute department
User: show overtime in jute department

Output:
{
  "sql": "SELECT * FROM AttendanceReport WHERE Work_Type IN (?, ?) AND Dept_Code = ?",
  "params": ["SO", "WO", 1]
}

---

### Example: Count overtime present
User: how many overtime are present

Output:
{
  "sql": "SELECT SUM(WORK_HR)/8 AS Overtime_Count FROM AttendanceReport WHERE Work_Type IN (?, ?)",
  "params": ["SO", "WO"]
}

---

### Example: Count overtime in jute department yesterday
User: how many overtime were present yesterday in jute department

Output:
{
  "sql": "SELECT SUM(WORK_HR)/8 AS Overtime_Count FROM AttendanceReport WHERE Work_Type IN (?, ?) AND Dept_Code = ? AND WDate = CAST(GETDATE()-1 AS DATE)",
  "params": ["SO", "WO", 1]
}

--------------------------------
Example: Month-wise attendance comparison
--------------------------------
User: show month wise attendance for nz1073 between 01/01/2025 to 31/12/2025

Output:
{
  "sql": "SELECT A.mon, A.work_days, B.attn_days FROM ( SELECT MONTH(WDate) AS mon, COUNT(DISTINCT WDate) AS work_days FROM AttendanceReport WHERE WDate BETWEEN ? AND ? GROUP BY MONTH(WDate) HAVING SUM(DUTY) > 0 ) A JOIN ( SELECT MONTH(WDate) AS mon, COUNT(DISTINCT WDate) AS attn_days FROM AttendanceReport WHERE WDate BETWEEN ? AND ? AND ECode = ? GROUP BY MONTH(WDate) HAVING SUM(DUTY) > 0 ) B ON A.mon = B.mon ORDER BY A.mon",
  "params": ["2025-01-01", "2025-12-31", "2025-01-01", "2025-12-31", "NZ1073"]
}

