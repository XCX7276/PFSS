from flask import Flask, render_template, request, redirect, url_for
from collections import Counter
import os
import re
import math
from docx import Document

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'docx', 'doc'}
 
  
all_documents = []

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']
 
def read_file(filepath, filename):
    if filename.endswith('.txt'):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    elif filename.endswith(('.docx', '.doc')):
        doc = Document(filepath)
        return ' '.join([para.text for para in doc.paragraphs])
    return ""

def process_text(text):
    words = re.findall(r'\b[а-яА-Яa-zA-Z]+\b', text.lower())
    total_words = len(words)
    word_counts = Counter(words)
     
    tf = {word: count / total_words for word, count in word_counts.items()}
    return tf, word_counts

def calculate_idf(word, all_docs):
    docs_with_word = sum(1 for doc in all_docs if word in doc)
    return math.log(len(all_docs) / (docs_with_word + 1))  

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global all_documents
    
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename): 
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath) 
            text = read_file(filepath, file.filename)
            os.remove(filepath)   
            tf, word_counts = process_text(text)
             
            all_documents.append(word_counts) 
            top_words = word_counts.most_common(50)
            results = []
            
            for word, count in top_words:
                idf = calculate_idf(word, all_documents)
                tf_idf = tf[word] * idf
                results.append({
                    'word': word,
                    'tf': tf[word],
                    'idf': idf
                })
            
            return render_template('results.html', results=results)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)