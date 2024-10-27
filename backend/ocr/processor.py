import cv2
from PIL import Image
import pytesseract
import re

def preprocess_and_crop(image_path):
    # 画像を読み込み
    img = cv2.imread(image_path)

    # 必要な領域だけをトリミング（x, y, width, height）
    cropped_img = img[300:1000, 50:700]  # 適切な座標に調整

    # グレースケール変換
    gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)

    # ノイズ軽減のためのぼかし
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # コントラストの強調と二値化
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 前処理した画像を保存（デバッグ用）
    cv2.imwrite("cropped_image.png", binary)

    return "cropped_image.png"

def perform_ocr(image_path: str) -> str:
    # トリミングした画像を使用
    cropped_image = preprocess_and_crop(image_path)
    img = Image.open(cropped_image)
    
    # 日本語OCRの実行
    text = pytesseract.image_to_string(img, lang='jpn')
    return text

def extract_ingredients(text: str):
    """
    OCR結果から食材名と個数を抽出し、不要な文字列を除外する。
    """
    # 不要な行を除去するフィルタ（例：特定の単語や記号）
    lines = text.splitlines()
    filtered_lines = [line for line in lines if not re.search(r'(バッグ|もどる|デフォルト|どうぐ)', line)]

    # 必要な情報を含む行を正規表現で抽出
    pattern = r"([ぁ-んァ-ン一-龥ー]+)\s*[xX×]\s*(\d+)"
    matches = re.findall(pattern, "\n".join(filtered_lines))

    # 食材名と個数を辞書形式に変換
    ingredients = {name: int(quantity) for name, quantity in matches}
    return ingredients

