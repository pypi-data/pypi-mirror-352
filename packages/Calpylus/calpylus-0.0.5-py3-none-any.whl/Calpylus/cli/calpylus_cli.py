def launch_cli():
    import sys
    print("Welcome to CalPylus CLI")
    print("Type 'exit' to quit")
    while True:
        try:
            expr = input("Enter expression to simplify: ")
            if expr.lower() == 'exit': break
            from .. import simplify_expr
            result = simplify_expr(expr)
            print("Result:", result)
        except Exception as e:
            print("Error:", e)

