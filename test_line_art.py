import ast
import numpy as np


def load_int_points():
    """Load only the int_points function from Line_art.py without running the script."""
    with open('Line_art.py', 'r') as f:
        source = f.read()
    module = ast.parse(source, filename='Line_art.py')
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == 'int_points':
            mod = ast.Module(body=[node], type_ignores=[])
            ns = {}
            exec(compile(ast.fix_missing_locations(mod), 'Line_art.py', 'exec'), {'np': np}, ns)
            return ns['int_points']
    raise RuntimeError('int_points not found')


def test_int_points_simple_diagonal():
    int_points = load_int_points()
    x, y = int_points((0, 0), (2, 2))
    expected = np.array([0.0, 2.0])
    assert np.array_equal(x, expected)
    assert np.array_equal(y, expected)
