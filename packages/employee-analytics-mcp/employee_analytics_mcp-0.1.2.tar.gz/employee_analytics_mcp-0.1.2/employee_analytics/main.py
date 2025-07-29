import asyncio
from .employee_analytics import main as employee_analytics_main

def main():
    asyncio.run(employee_analytics_main())


if __name__ == "__main__":
    main()
