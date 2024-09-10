from flask import Flask, request, jsonify, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/lcoe', methods=['POST'])
def get_lcoe():
    if 'file' not in request.files:
        return jsonify({"message": "No file provided"}), 400

    file = request.files['file']

    if not file.filename.endswith('.csv'):
        return jsonify({"message": "Invalid file format. Please upload a CSV file."}), 400

    try:
        df = pd.read_csv(file)

        for k, i in enumerate(df['Cost/Operating cost ($/yr)']):
            if i >= 0:
                return jsonify({"LCOE": df['Cost/LCOE ($/kWh)'][k]})
        
        return jsonify({"message": "No valid LCOE found"}), 404
    
    except Exception as e:
        return jsonify({"message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True , port= 3000)
