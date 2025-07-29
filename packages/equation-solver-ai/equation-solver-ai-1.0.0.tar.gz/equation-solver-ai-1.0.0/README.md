# Equation Solver

A Python package for solving univariate polynomial equations (degree 1-4) with traditional methods and AI assistance.

## Features

- Solve 1st to 4th degree polynomial equations
- AI-assisted solving using local language models
- Server management for local AI models
- Expression rendering and approximation
- Caching for improved performance

## Installation

```bash
pip install equation-solver
```

## Basic Usage

### Traditional Solving

```python
from equation_solver import EquationSolver

solver = EquationSolver()
coefficients = solver.parse_input({
    "x⁴": "1",
    "x³": "0",
    "x²": "0",
    "x": "0",
    "常数项": "-1"
})

equation, degree = solver.build_equation(coefficients)

if degree > 0:
    solutions = solver.solve_equation(equation)
    processed = solver.process_solutions(solutions)
    print(f"Found {len(processed)} solutions")
```

### AI-Assisted Solving

```python
from equation_solver import EquationSolver, AISolver, ModelServer

# Start AI server
server = ModelServer()
server.start_server(model_path="path/to/model.gguf")

# Wait for server to start
import time
while server.status != "running":
    time.sleep(1)

# Solve with AI
solver = EquationSolver()
ai_solver = AISolver(port=5001)

coefficients = solver.parse_input({
    "x⁴": "1",
    "x³": "0",
    "x²": "0",
    "x": "0",
    "常数项": "-1"
})
equation, _ = solver.build_equation(coefficients)

equation_latex = sp.latex(equation)
ai_response = ai_solver.send_ai_request(equation_latex)
parsed = ai_solver.parse_ai_response(ai_response)

print("AI Solution:", parsed["clean_text"])
print("Solutions:", parsed["solutions"])

# Stop server
server.stop_server()
```

## API Documentation

### EquationSolver
- `parse_input(inputs)`: Parse user input coefficients
- `build_equation(coefficients)`: Build equation from coefficients
- `solve_equation(equation)`: Solve the equation
- `process_solutions(solutions)`: Prepare solutions for display
- `get_cache_key(coefficients)`: Generate cache key for solutions

### AISolver
- `send_ai_request(equation_latex)`: Send request to AI server
- `parse_ai_response(ai_text)`: Parse AI response text

### ModelServer
- `start_server(model_path, port)`: Start model server
- `stop_server()`: Stop model server
- `is_running()`: Check if server is running
- `get_logs(max_lines=100)`: Get server logs

## Dependencies

- SymPy
- Requests
- Matplotlib
- Pillow
- Psutil

## License

MIT License