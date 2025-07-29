from agentops_ai.agentops_core.analyzer import analyze_file_with_parents

def test_analyze_simple_code():
    code = '''
import os

def foo(x: int) -> str:
    """Returns a string"""
    return str(x)

class Bar:
    def method(self, y):
        return y
'''
    # Write code to a temp file and analyze it
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.py', delete=True) as tmp:
        tmp.write(code)
        tmp.flush()
        result = analyze_file_with_parents(tmp.name)
    print("FUNCTIONS:", result['functions'])
    print("CLASSES:", result['classes'])
    assert 'functions' in result
    assert any(f.name == 'foo' for f in result['functions'])
    assert 'classes' in result
    assert any(c.name == 'Bar' for c in result['classes']) 