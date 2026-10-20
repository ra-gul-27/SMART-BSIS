import re
from typing import Optional, Tuple, Dict, Any, List

class ANPREngine:
    """
    Automatic Number Plate Recognition (ANPR) Engine.
    Detects, crops, preprocesses, and recognizes bus registration license plates.
    """
    def __init__(self, languages: List[str] = ["en"], gpu: bool = False):
        self.languages = languages
        self.gpu = gpu
        self.reader = None
        self._init_ocr()

        # Regular expressions for license plate formats (e.g. Indian state format: TN 01 AN 2345)
        self.plate_pattern = re.compile(r"([A-Z]{2}\s?[0-9]{1,2}\s?[A-Z]{0,3}\s?[0-9]{3,4})")

    def _init_ocr(self):
        try:
            import easyocr
            self.reader = easyocr.Reader(self.languages, gpu=self.gpu, verbose=False)
            print("[SUCCESS] EasyOCR engine initialized for ANPR.")
        except Exception as e:
            print(f"[INFO] EasyOCR not loaded ({e}). Using rule-based fallback preprocessor.")
            self.reader = None

    def preprocess_plate(self, image):
        """
        Enhance license plate image for character recognition.
        Grayscale -> Bilateral Filter -> Adaptive Thresholding / Otsu.
        """
        import cv2
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        # Noise reduction while keeping edges sharp
        filtered = cv2.bilateralFilter(gray, 11, 17, 17)
        # Contrast adjustment / Threshold
        thresh = cv2.adaptiveThreshold(filtered, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return thresh

    def clean_plate_text(self, raw_text: str) -> str:
        """
        Clean and normalize extracted OCR characters.
        Fixes common OCR confusions based on alphanumeric character positioning.
        Standard Indian Format: [State 2 letters] [District 2 digits] [Series 1-3 letters] [Number 1-4 digits]
        e.g., TN 01 AN 2345 or TN 43 N 1234
        """
        cleaned = re.sub(r"[^A-Za-z0-9]", "", raw_text).upper()
        if len(cleaned) < 5 or len(cleaned) > 12:
            return ""

        # First 2 characters must be State letters (e.g. TN, KA, KL, AP, TS, DL, PY, MH)
        s1 = 'O' if cleaned[0] == '0' else ('I' if cleaned[0] == '1' else ('B' if cleaned[0] == '8' else cleaned[0]))
        s2 = 'O' if cleaned[1] == '0' else ('I' if cleaned[1] == '1' else ('B' if cleaned[1] == '8' else cleaned[1]))
        state_code = f"{s1}{s2}"

        # If it doesn't look like an alpha state code, keep raw prefix
        if not state_code.isalpha():
            state_code = cleaned[:2]

        remaining = cleaned[2:]
        if len(remaining) < 3:
            return f"{state_code} {remaining}".strip()

        # Next 2 are usually RTO digits (e.g. 01, 43)
        d1 = '0' if remaining[0] in ['O', 'D', 'Q'] else ('1' if remaining[0] in ['I', 'L'] else ('8' if remaining[0] == 'B' else remaining[0]))
        d2 = '0' if remaining[1] in ['O', 'D', 'Q'] else ('1' if remaining[1] in ['I', 'L'] else ('8' if remaining[1] == 'B' else remaining[1]))
        district_code = f"{d1}{d2}"

        rest = remaining[2:]
        # Extract series (letters) and number (digits) from remainder
        m = re.match(r"^([A-Z]{0,3})([0-9]{1,4})$", rest)
        if m:
            series, number = m.groups()
            parts = [state_code, district_code]
            if series:
                parts.append(series)
            parts.append(number)
            return " ".join(parts)

        return f"{state_code} {district_code} {rest}".strip()

    def recognize_plate(self, cropped_vehicle_or_plate) -> Optional[Dict[str, Any]]:
        """
        Extract registration plate text and confidence score from a cropped frame.
        Applies smart ROI cropping if the input image is a full vehicle box.
        """
        if cropped_vehicle_or_plate is None or cropped_vehicle_or_plate.size == 0:
            return None

        import cv2

        h, w = cropped_vehicle_or_plate.shape[:2]
        # If the image is a full vehicle crop (not a flat license plate strip),
        # focus OCR on the lower 55% of the vehicle where bumper plates are located
        target_img = cropped_vehicle_or_plate
        if h > 80 and (h / float(w)) > 0.35:
            target_img = cropped_vehicle_or_plate[int(h * 0.45):h, :]

        # 1. EasyOCR Detection & Recognition
        if self.reader is not None:
            try:
                results = self.reader.readtext(target_img)
                candidates = []

                # Strategy A: Evaluate individual OCR bounding box detections
                for bbox, text, prob in results:
                    cleaned = self.clean_plate_text(text)
                    if cleaned and prob > 0.35:
                        candidates.append((cleaned, float(prob)))

                # Strategy B: Combine multiple text lines (often plates are split across rows)
                if not candidates and len(results) >= 2:
                    combined_text = " ".join([r[1] for r in results])
                    combined_prob = sum([float(r[2]) for r in results]) / len(results)
                    cleaned_comb = self.clean_plate_text(combined_text)
                    if cleaned_comb and combined_prob > 0.3:
                        candidates.append((cleaned_comb, combined_prob))

                # Strategy C: Also check preprocessed high-contrast image if initial attempt was empty
                if not candidates:
                    preprocessed = self.preprocess_plate(target_img)
                    prep_results = self.reader.readtext(preprocessed)
                    for bbox, text, prob in prep_results:
                        cleaned = self.clean_plate_text(text)
                        if cleaned and prob > 0.35:
                            candidates.append((cleaned, float(prob)))

                if candidates:
                    # Sort candidates by probability descending
                    candidates.sort(key=lambda c: c[1], reverse=True)
                    best_plate, best_prob = candidates[0]
                    return {
                        "plate_number": best_plate,
                        "confidence": round(best_prob * 100, 1),
                        "match_status": "Verified" if best_prob > 0.65 else "Unverified"
                    }
            except Exception as e:
                print(f"[ANPR] OCR Inference notice: {e}")

        # 2. Heuristic contour fallback
        try:
            gray = cv2.cvtColor(target_img, cv2.COLOR_BGR2GRAY) if len(target_img.shape) == 3 else target_img
            edges = cv2.Canny(gray, 170, 200)
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

            for c in contours:
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.02 * peri, True)
                if len(approx) == 4:
                    x, y, cw, ch = cv2.boundingRect(approx)
                    aspect_ratio = cw / float(ch) if ch > 0 else 0
                    if 2.0 <= aspect_ratio <= 5.5 and cw > 50:
                        return {
                            "plate_number": "LOCALIZED",
                            "confidence": 75.0,
                            "match_status": "Unverified"
                        }
        except Exception:
            pass

        return None
