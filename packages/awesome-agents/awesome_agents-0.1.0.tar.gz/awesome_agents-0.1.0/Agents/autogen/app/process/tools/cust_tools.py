# app/process/tools/cust_tools.py

def get_weather(city: str) -> str:
    """Get the weather for a city."""
    return f"The weather in {city} is 73 degrees and Sunny."

def get_temperature(city: str) -> str:
    """Get the weather for a city."""
    return f"The weather in {city} is 73 degrees and Sunny."

def calculator(a: float, b: float, operator: str) -> str:
    try:
        if operator == '+':
            return str(a + b)
        elif operator == '-':
            return str(a - b)
        elif operator == '*':
            return str(a * b)
        elif operator == '/':
            if b == 0:
                return 'Error: Division by zero'
            return str(a / b)
        else:
            return 'Error: Invalid operator. Please use +, -, *, or /'
    except Exception as e:
        return f'Error: {str(e)}'