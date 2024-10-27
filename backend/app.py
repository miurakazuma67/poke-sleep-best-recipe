from flask import Flask, request, jsonify
from ocr.processor import perform_ocr, extract_ingredients
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # CORSを許可

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    file.save('uploaded_image.png')

    # OCRの実行
    ocr_result = perform_ocr('uploaded_image.png')
    print(f"OCRの結果: {ocr_result}")  # OCRの結果をサーバーのログに出力

    # 食材名と個数の抽出
    ingredients = extract_ingredients(ocr_result)

    return jsonify({'ingredients': ingredients})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


