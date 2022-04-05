from manim_lexer import ManimLexer

def setup(app):
    # choose one, both ok
    app.add_lexer('python', ManimLexer)
    app.add_lexer('Python', ManimLexer)
    app.add_lexer('python3', ManimLexer)
    # app.add_lexer('my_lang', PythonLexer)