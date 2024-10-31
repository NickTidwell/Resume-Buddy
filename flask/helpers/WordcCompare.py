import difflib
# from flask import Flask, request, render_template_string
# app = Flask(__name__)

def compare_strings(original, new):
    # Convert strings into lists of characters
    original_chars = list(original)
    new_chars = list(new)

    # Perform the comparison
    differ = difflib.Differ()
    diff = list(differ.compare(original_chars, new_chars))
    
    return diff

def generate_html_diff(diff):
    original_html = []
    new_html = []

    for char in diff:
        if char.startswith(' '):
            original_html.append(f'<span>{char[2:]}</span>')
            new_html.append(f'<span>{char[2:]}</span>')
        elif char.startswith('-'):
            original_html.append(f'<span style="background-color: #fdd; color: #d00;">{char[2:]}</span>')
        elif char.startswith('+'):
            new_html.append(f'<span style="background-color: #dfd; color: #080;">{char[2:]}</span>')

    # Add empty spaces for alignment
    max_len = max(len(original_html), len(new_html))
    original_html.extend(['<span>&nbsp;</span>'] * (max_len - len(original_html)))
    new_html.extend(['<span>&nbsp;</span>'] * (max_len - len(new_html)))

    return (''.join(original_html), ''.join(new_html))

# @app.route('/')
# def index():
#     return '''
#         <h1>Letter-by-Letter Comparison</h1>
#         <form action="/compare" method="post">
#             <label for="original">Original Text:</label><br>
#             <textarea name="original" id="original" rows="4" cols="50" required></textarea><br><br>
#             <label for="new">New Text:</label><br>
#             <textarea name="new" id="new" rows="4" cols="50" required></textarea><br><br>
#             <input type="submit" value="Compare">
#         </form>
#     '''

# @app.route('/compare', methods=['POST'])
# def compare():
#     original = request.form['original']
#     new = request.form['new']

#     diff = compare_strings(original, new)
#     original_html, new_html = generate_html_diff(diff)

#     return render_template_string('''
#         <h1>Comparison Result</h1>
#         <div style="display: flex; font-family: monospace;">
#             <div style="width: 50%; border-right: 1px solid #ccc; padding: 10px; box-sizing: border-box;">
#                 <h2>Original Text</h2>
#                 <div style="white-space: pre-wrap;">{{ original | safe }}</div>
#             </div>
#             <div style="width: 50%; padding: 10px; box-sizing: border-box;">
#                 <h2>Updated Text</h2>
#                 <div style="white-space: pre-wrap;">{{ new | safe }}</div>
#             </div>
#         </div>
#         <a href="/">Compare Another</a>
#     ''', original=original_html, new=new_html)

# if __name__ == '__main__':
#     app.run(debug=True)
