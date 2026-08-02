from google.adk.agents.llm_agent import Agent

def solve_math_expression(expression: str) -> dict:
    """Evaluates a mathematical expression and returns the result.
    
    Args:
        expression: The mathematical expression to solve (e.g. '2 + 2' or '5 * (10 + 2)').
    """
    try:
        # A simple mathematical evaluator
        # Note: docstrings are used by ADK to generate schema descriptions for the model
        allowed_names = {"__builtins__": None}
        result = str(eval(expression, allowed_names, {}))
        return {"status": "success", "result": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Define the root agent for the ADK CLI runtime
root_agent = Agent(
    model='gemini-3.5-flash',
    name='calc_agent',
    description="An assistant that helps users solve and explain math equations.",
    instruction="You are a friendly math assistant. Always use the 'solve_math_expression' tool to solve calculations and explain the steps to the user.",
    tools=[solve_math_expression]
)
