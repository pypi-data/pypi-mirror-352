from mcp.server.fastmcp.server import FastMCP
from server.employee_analytics_core import EmployeeAnalyticsMCP

mcp = FastMCP()
analytics = EmployeeAnalyticsMCP()

@mcp.tool(
    name="analyze_employee",
    description="Analyze an employee's performance and project relevance."
)
async def analyze_employee(employee_id: int):
    return await analytics.analyze_employee(employee_id)

@mcp.tool(
    name="compare_employees",
    description="Compare multiple employees' performance and project relevance."
)
async def compare_employees(employee_ids: list[int]):
    return await analytics.compare_employees(employee_ids)

@mcp.tool(
    name="search_by_skill",
    description="Search for employees with specific skills or project experience."
)
async def search_by_skill(skill: str):
    return await analytics.search_employee_by_skill(skill)

if __name__ == "__main__":
    mcp.run()
