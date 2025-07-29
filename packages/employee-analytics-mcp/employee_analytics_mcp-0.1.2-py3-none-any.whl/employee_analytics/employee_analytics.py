import os
import sys
import json
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor
import httpx
from typing import Dict, List, Any
from datetime import datetime
import asyncio
import re

load_dotenv()

def json_default(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    return str(obj)

class EmployeeAnalyticsMCP:
    def __init__(self):
        self.db_conn = psycopg2.connect(
            dbname=os.getenv("SUPABASE_DB"),
            user=os.getenv("SUPABASE_USER"),
            password=os.getenv("SUPABASE_PASS"),
            host=os.getenv("SUPABASE_HOST"),
            port=os.getenv("SUPABASE_PORT")
        )
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.serper_url = "https://google.serper.dev/search"

    async def search_web(self, query: str) -> Dict[str, Any]:
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }
        payload = {'q': query, 'gl': 'us', 'hl': 'en'}
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.serper_url,
                headers=headers,
                json=payload,
                timeout=30.0
            )
            return response.json()

    def get_employee_data(self, employee_id: int = None) -> List[Dict[str, Any]]:
        with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            if employee_id:
                cur.execute("""
                    SELECT e.*, d.name as department_name
                    FROM employees e
                    JOIN departments d ON e.department_id = d.id
                    WHERE e.id = %s
                """, (employee_id,))
            else:
                cur.execute("""
                    SELECT e.*, d.name as department_name
                    FROM employees e
                    JOIN departments d ON e.department_id = d.id
                """)
            return cur.fetchall()

    def get_employee_projects(self, employee_id: int) -> List[Dict[str, Any]]:
        with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT p.*, d.name as department_name
                FROM projects p
                JOIN departments d ON p.department_id = d.id
                WHERE p.department_id = (
                    SELECT department_id FROM employees WHERE id = %s
                )
            """, (employee_id,))
            return cur.fetchall()

    def get_employee_feedback(self, employee_id: int) -> List[Dict[str, Any]]:
        with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT f.*, e.name as employee_name
                FROM feedback f
                JOIN employees e ON f.employee_id = e.id
                WHERE f.employee_id = %s
            """, (employee_id,))
            return cur.fetchall()

    async def analyze_employee(self, employee_id: int) -> Dict[str, Any]:
        employee_data = self.get_employee_data(employee_id)
        if not employee_data:
            return {"error": "Employee not found"}
        employee = employee_data[0]
        projects = self.get_employee_projects(employee_id)
        feedback = self.get_employee_feedback(employee_id)
        role_query = f"latest trends in {employee['title']} role and skills"
        role_search = await self.search_web(role_query)
        project_analyses = []
        for project in projects:
            project_query = f"current state and future of {project['name']} technology or methodology"
            project_search = await self.search_web(project_query)
            project_analyses.append({
                "project": project,
                "market_analysis": project_search
            })
        avg_rating = sum(f['rating'] for f in feedback) / len(feedback) if feedback else 0
        return {
            "employee": employee,
            "projects": projects,
            "feedback": {
                "entries": feedback,
                "average_rating": avg_rating
            },
            "market_analysis": {
                "role_trends": role_search,
                "project_analyses": project_analyses
            }
        }

    async def compare_employees(self, employee_ids: List[int]) -> Dict[str, Any]:
        comparisons = []
        for emp_id in employee_ids:
            analysis = await self.analyze_employee(emp_id)
            comparisons.append(analysis)
        return {
            "comparisons": comparisons,
            "timestamp": datetime.now().isoformat()
        }

    async def search_employee_by_skill(self, skill: str) -> List[Dict[str, Any]]:
        with self.db_conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT DISTINCT e.*, d.name as department_name
                FROM employees e
                JOIN departments d ON e.department_id = d.id
                JOIN projects p ON p.department_id = d.id
                WHERE e.title ILIKE %s 
                   OR p.name ILIKE %s 
                   OR p.description ILIKE %s
            """, (f'%{skill}%', f'%{skill}%', f'%{skill}%'))
            return cur.fetchall()

    def close(self):
        self.db_conn.close()

def parse_natural_language_command(text):
    text = text.lower().strip()

    # Analyze a single employee
    match = re.search(r'(?:details|analyze|info).*employee id (\d+)', text)
    if match:
        return {"command": "analyze_employee", "employee_id": int(match.group(1))}

    # Compare multiple employees
    match = re.search(r'compare.*employee ids? ([\d, ]+)', text)
    if match:
        ids = [int(i) for i in re.findall(r'\d+', match.group(1))]
        return {"command": "compare_employees", "employee_ids": ids}

    # Search by skill
    match = re.search(r'(?:search|find).*skill[s]? ([\w ]+)', text)
    if match:
        skill = match.group(1).strip()
        return {"command": "search_by_skill", "skill": skill}

    return {"error": "Could not understand the command"}

async def main():
    analytics = EmployeeAnalyticsMCP()
    try:
        print(json.dumps({
            "serverInfo": {
                "name": "employee_analytics",
                "version": "0.1.2",
                "description": "An MCP server for employee analytics"
            }
        }), flush=True)
        for line in sys.stdin:
            try:
                print("Received line:", line, file=sys.stderr)
                try:
                    req = json.loads(line)
                except json.JSONDecodeError:
                    req = parse_natural_language_command(line.strip())
                cmd = req.get("command")
                if cmd == "listOfferings":
                    # Respond with the tools this MCP provides
                    offerings = {
                        "tools": [
                            {
                                "name": "analyze_employee",
                                "description": "Analyze an employee's performance and project relevance.",
                                "parameters": [
                                    {"name": "employee_id", "type": "int"}
                                ]
                            },
                            {
                                "name": "compare_employees",
                                "description": "Compare multiple employees' performance and project relevance.",
                                "parameters": [
                                    {"name": "employee_ids", "type": "list[int]"}
                                ]
                            },
                            {
                                "name": "search_by_skill",
                                "description": "Search for employees with specific skills or project experience.",
                                "parameters": [
                                    {"name": "skill", "type": "str"}
                                ]
                            }
                        ]
                    }
                    print(json.dumps(offerings, default=json_default), flush=True)
                    continue
                elif cmd == "analyze_employee":
                    employee_id = req.get("employee_id")
                    result = await analytics.analyze_employee(employee_id)
                elif cmd == "compare_employees":
                    employee_ids = req.get("employee_ids")
                    result = await analytics.compare_employees(employee_ids)
                elif cmd == "search_by_skill":
                    skill = req.get("skill")
                    result = await analytics.search_employee_by_skill(skill)
                elif cmd == "getServerInfo":
                    info = {
                        "serverInfo": {
                            "name": "employee_analytics",
                            "version": "0.1.1",
                            "description": "An MCP server for employee analytics"
                        }
                    }
                    print(json.dumps(info), flush=True)
                    continue
                else:
                    result = {"error": "Unknown command"}
                print(json.dumps(result, default=json_default), flush=True)
            except Exception as e:
                print(json.dumps({"error": str(e)}, default=json_default), flush=True)
    finally:
        analytics.close()

if __name__ == "__main__":
    asyncio.run(main())