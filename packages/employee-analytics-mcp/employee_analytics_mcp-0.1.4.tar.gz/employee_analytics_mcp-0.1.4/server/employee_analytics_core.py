import os
import psycopg2
from psycopg2.extras import RealDictCursor
import httpx
from typing import Dict, List, Any
from dotenv import load_dotenv
from datetime import datetime
import asyncio

load_dotenv()

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