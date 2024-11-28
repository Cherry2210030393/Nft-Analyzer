from flask import Flask, render_template, request
import os
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

app = Flask(__name__)

# Configure upload folder and max content length
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # Max file size of 10MB

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Home route and file upload
@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        
        # Ensure file is a CSV
        if not file.filename.endswith('.csv'):
            return "Please upload a valid CSV file.", 400
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)

        # Load the dataset
        df = pd.read_csv(filepath)

        # Display the columns for user to map or choose automatically
        column_names = df.columns.tolist()

        # Try to detect possible column names
        owner_col = None
        buyer_col = None
        token_id_col = None

        # Basic heuristic to detect relevant columns based on common terms
        for col in column_names:
            if 'owner' in col.lower():
                owner_col = col
            elif 'buyer' in col.lower():
                buyer_col = col
            elif 'token' in col.lower() or 'id' in col.lower():
                token_id_col = col

        if not owner_col or not buyer_col or not token_id_col:
            return "Could not automatically detect required columns. Please ensure the CSV contains columns for owner, buyer, and token ID.", 400

        # Create a graph from the CSV data
        G = nx.DiGraph()  # Directed graph for transactions
        for _, row in df.iterrows():
            G.add_edge(row[owner_col], row[buyer_col], token_id=row[token_id_col])

        # Create the graph visualization
        graph_path = os.path.join('static', 'graph.png')
        pos = nx.spring_layout(G, k=0.15, iterations=20)  # Spring layout for better aesthetics
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_color='skyblue', font_size=10, font_weight='bold')
        plt.savefig(graph_path)
        plt.close()

        # Render the graph image
        return render_template('graph.html', graph_path=graph_path)

    return render_template('upload.html')


if __name__ == "__main__":
    app.run(debug=True)
