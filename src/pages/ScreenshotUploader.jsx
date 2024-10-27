import React, { useState } from "react";
import axios from "axios";

const ScreenshotUploader = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [ocrResult, setOcrResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) setSelectedImage(file);
  };

  const handleUpload = async () => {
    if (!selectedImage) return alert("Please upload an image.");

    const formData = new FormData();
    formData.append("file", selectedImage);

    setLoading(true);
    try {
      const response = await axios.post("http://localhost:5000/ocr", formData);
      console.log("OCRレスポンス:", response.data.ingredients);  // レスポンスをログに出力
      setOcrResult(JSON.stringify(response.data.ingredients, null, 2));  // 整形して表示
    } catch (error) {
      console.error("Error uploading image:", error);
      alert("OCR failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center min-h-screen bg-gray-100 p-4">
      <div className="card w-full max-w-lg bg-white shadow-md rounded-lg p-6">
        <h1 className="text-2xl font-bold text-center mb-4">Screenshot Uploader</h1>

        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className="file-input file-input-bordered w-full mb-4"
        />

        <button onClick={handleUpload} className="btn btn-primary w-full" disabled={loading}>
          {loading ? "Analyzing..." : "Analyze Screenshot"}
        </button>

        {ocrResult && (
          <div className="mt-6 p-4 bg-green-100 text-green-800 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">OCR Result:</h2>
            <pre className="whitespace-pre-wrap">{ocrResult}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScreenshotUploader;

