import cv2
import pytesseract
from PIL import Image
import re

def preprocess_image(image_path):
    """ OCR精度向上のための前処理を行う。 """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.medianBlur(gray, 3)
    enhanced = cv2.equalizeHist(blurred)
    _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite("preprocessed_image.png", binary)
    return "preprocessed_image.png"

def find_label_position(data, keywords=["表示", "順", "デフォルト"]):
    """ OCR結果からラベルの位置を探す。 """
    for i, text in enumerate(data['text']):
        for keyword in keywords:
            if keyword in text:
                return data['top'][i] + data['height'][i]  # ラベルの下の位置を返す
    return None

def resize_region(img, x, y, w, h, scale=2):
    """ 指定された領域を拡大する。 """
    region = img[y:y + h, x:x + w]
    resized = cv2.resize(region, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    return resized

def crop_image_below_label(image_path):
    """ ラベルの下から画像をトリミングし、小さい文字領域を拡大する。 """
    img = cv2.imread(image_path)
    data = pytesseract.image_to_data(img, lang='jpn', output_type=pytesseract.Output.DICT)
    y_start = find_label_position(data)

    if y_start is None:
        print("ラベルが見つかりませんでした。OCR結果:")
        print(data['text'])  # デバッグ用
        raise ValueError("ラベルが見つかりませんでした。")

    cropped_img = img[y_start:, :]

    # 小さい文字領域を特定して拡大
    for i in range(len(data['text'])):
        if data['height'][i] < 20:  # 高さが小さい文字を拡大対象に
            x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
            resized_region = resize_region(cropped_img, x, y - y_start, w, h)
            cropped_img[y - y_start:y - y_start + resized_region.shape[0], x:x + resized_region.shape[1]] = resized_region

    cropped_path = "cropped_image.png"
    cv2.imwrite(cropped_path, cropped_img)
    return cropped_path

def perform_ocr(image_path):
    """ OCRを実行し、テキストを抽出する。 """
    try:
        preprocessed_image = preprocess_image(image_path)
        cropped_image = crop_image_below_label(preprocessed_image)
        img = Image.open(cropped_image)
        text = pytesseract.image_to_string(img, lang='jpn', config='--psm 6')
        print("OCR結果:")
        print(text)
        return text
    except Exception as e:
        print(f"OCRの実行中にエラーが発生しました: {e}")
        raise

def extract_ingredients(text):
    """ OCR結果から食材名と個数を抽出する。 """
    corrections = {
        "やったウン": "あったかジンジャー",
    }
    lines = text.splitlines()
    filtered_lines = [line for line in lines if re.search(r'[ぁ-んァ-ン一-龥]', line)]
    cleaned_text = "\n".join(filtered_lines)
    cleaned_text = re.sub(r'[^\wぁ-んァ-ン一-龥ー\sxX×]', '', cleaned_text)

    for wrong, correct in corrections.items():
        cleaned_text = cleaned_text.replace(wrong, correct)

    pattern = r"([ぁ-んァ-ン一-龥ー]+)\s*[xX×]\s*(\d+)"
    matches = re.findall(pattern, cleaned_text)
    ingredients = {name: int(quantity) for name, quantity in matches}
    print("抽出された食材:", ingredients)
    return ingredients

