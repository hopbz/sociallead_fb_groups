# backend/app/captcha_solver.py
"""
CAPTCHA solver tổng hợp.
Các thư viện nặng (cv2, pytesseract, speech_recognition, pydub) được import
theo kiểu optional — nếu chưa cài thì các class liên quan sẽ bị vô hiệu hoá
thay vì crash toàn bộ ứng dụng.

Cài đặt tuỳ chọn:
    pip install opencv-python-headless pillow pytesseract
    pip install SpeechRecognition pydub
"""
from __future__ import annotations

import os
import re
import time
import random
import requests
from io import BytesIO
from typing import Optional, Tuple

# ── Optional heavy deps ──────────────────────────────────────────────────────
try:
    import cv2
    import numpy as np
    _CV2_AVAILABLE = True
except ImportError:
    _CV2_AVAILABLE = False

try:
    from PIL import Image as PilImage
    _PIL_AVAILABLE = True
except ImportError:
    _PIL_AVAILABLE = False

try:
    import speech_recognition as sr
    _SR_AVAILABLE = True
except ImportError:
    _SR_AVAILABLE = False

try:
    from pydub import AudioSegment
    _PYDUB_AVAILABLE = True
except ImportError:
    _PYDUB_AVAILABLE = False

try:
    import pytesseract as _pytesseract_mod
    _TESSERACT_AVAILABLE = True
except ImportError:
    _TESSERACT_AVAILABLE = False

# ── Selenium deps (đã có trong requirements.txt) ─────────────────────────────
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# ─────────────────────────────────────────────────────────────────────────────
class ImageCaptchaSolver:
    """Giải CAPTCHA ảnh bằng Tesseract OCR."""

    def __init__(self, tesseract_cmd: Optional[str] = None) -> None:
        self.available = _TESSERACT_AVAILABLE and _CV2_AVAILABLE and _PIL_AVAILABLE
        if self.available and tesseract_cmd:
            _pytesseract_mod.pytesseract.tesseract_cmd = tesseract_cmd
        if not self.available:
            print("[ImageCaptchaSolver] Không khả dụng. Hãy cài: pip install opencv-python-headless pillow pytesseract")

    def preprocess(self, image: "PilImage.Image") -> "PilImage.Image":  # type: ignore[name-defined]
        gray = image.convert("L")
        arr = np.array(gray)
        _, thresh = cv2.threshold(arr, 127, 255, cv2.THRESH_BINARY)
        denoised = cv2.medianBlur(thresh, 3)
        return PilImage.fromarray(denoised)

    def solve(
        self,
        image_source: str,
        config: str = "--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    ) -> Optional[str]:
        if not self.available:
            return None
        try:
            if image_source.startswith(("http://", "https://")):
                resp = requests.get(image_source, timeout=10)
                image = PilImage.open(BytesIO(resp.content))
            else:
                image = PilImage.open(image_source)
            processed = self.preprocess(image)
            raw = _pytesseract_mod.image_to_string(processed, config=config)
            result = re.sub(r"[^A-Za-z0-9]", "", raw).strip()
            return result or None
        except Exception as exc:
            print(f"[ImageCaptchaSolver] Lỗi: {exc}")
            return None


# ─────────────────────────────────────────────────────────────────────────────
class RecaptchaAudioSolver:
    """Giải reCAPTCHA audio bằng Google Speech Recognition."""

    def __init__(self) -> None:
        self.available = _SR_AVAILABLE and _PYDUB_AVAILABLE
        if not self.available:
            print("[RecaptchaAudioSolver] Không khả dụng. Hãy cài: pip install SpeechRecognition pydub")

    def solve(self, audio_url: str) -> Optional[str]:
        if not self.available:
            return None
        recognizer = sr.Recognizer()
        try:
            resp = requests.get(audio_url, timeout=30)
            temp_mp3 = "temp_captcha_audio.mp3"
            temp_wav = "temp_captcha_audio.wav"
            with open(temp_mp3, "wb") as fh:
                fh.write(resp.content)
            AudioSegment.from_mp3(temp_mp3).export(temp_wav, format="wav")
            with sr.AudioFile(temp_wav) as source:
                audio_data = recognizer.record(source)
                text: str = recognizer.recognize_google(audio_data)  # type: ignore[attr-defined]
            for f in (temp_mp3, temp_wav):
                try:
                    os.remove(f)
                except OSError:
                    pass
            return text
        except Exception as exc:
            print(f"[RecaptchaAudioSolver] Lỗi: {exc}")
            return None


# ─────────────────────────────────────────────────────────────────────────────
class RecaptchaV2SolverFree:
    """Giải reCAPTCHA v2 qua audio fallback, kết hợp SeleniumBase."""

    def __init__(self, driver: object) -> None:
        self.driver = driver
        self.audio_solver = RecaptchaAudioSolver()

    def solve_checkbox(self, timeout: int = 30) -> bool:
        try:
            iframe = WebDriverWait(self.driver, timeout).until(  # type: ignore[arg-type]
                EC.presence_of_element_located(
                    (By.XPATH, "//iframe[contains(@src,'recaptcha/api2')]")
                )
            )
            self.driver.switch_to.frame(iframe)  # type: ignore[attr-defined]
            checkbox = WebDriverWait(self.driver, 10).until(  # type: ignore[arg-type]
                EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
            )
            checkbox.click()
            time.sleep(2)
            self.driver.switch_to.default_content()  # type: ignore[attr-defined]
            if self._is_image_challenge():
                return self._solve_image_challenge()
            return True
        except Exception as exc:
            print(f"[reCAPTCHA] Lỗi: {exc}")
            return False

    def _is_image_challenge(self) -> bool:
        try:
            elems = self.driver.find_elements(  # type: ignore[attr-defined]
                By.XPATH, "//iframe[contains(@src,'recaptcha/api2/bframe')]"
            )
            return len(elems) > 0
        except Exception:
            return False

    def _solve_image_challenge(self) -> bool:
        try:
            iframe = self.driver.find_element(  # type: ignore[attr-defined]
                By.XPATH, "//iframe[contains(@src,'recaptcha/api2/bframe')]"
            )
            self.driver.switch_to.frame(iframe)  # type: ignore[attr-defined]
            audio_btn = WebDriverWait(self.driver, 10).until(  # type: ignore[arg-type]
                EC.element_to_be_clickable((By.ID, "recaptcha-audio-button"))
            )
            audio_btn.click()
            time.sleep(2)
            audio_src = self.driver.find_element(By.ID, "audio-source").get_attribute("src")  # type: ignore[attr-defined]
            if audio_src:
                solution = self.audio_solver.solve(audio_src)
                if solution:
                    self.driver.find_element(By.ID, "audio-response").send_keys(solution)  # type: ignore[attr-defined]
                    self.driver.find_element(By.ID, "recaptcha-verify-button").click()  # type: ignore[attr-defined]
                    time.sleep(2)
                    self.driver.switch_to.default_content()  # type: ignore[attr-defined]
                    return True
            self.driver.switch_to.default_content()  # type: ignore[attr-defined]
            return False
        except Exception as exc:
            print(f"[reCAPTCHA Image] Lỗi: {exc}")
            try:
                self.driver.switch_to.default_content()  # type: ignore[attr-defined]
            except Exception:
                pass
            return False


# ─────────────────────────────────────────────────────────────────────────────
class HCaptchaSolver:
    """Giải hCaptcha bằng cách click checkbox."""

    def __init__(self, driver: object) -> None:
        self.driver = driver

    def solve(self, timeout: int = 60) -> bool:
        try:
            iframes = self.driver.find_elements(  # type: ignore[attr-defined]
                By.XPATH, "//iframe[contains(@src,'hcaptcha')]"
            )
            for iframe in iframes:
                self.driver.switch_to.frame(iframe)  # type: ignore[attr-defined]
                checkbox = WebDriverWait(self.driver, 10).until(  # type: ignore[arg-type]
                    EC.element_to_be_clickable((By.ID, "checkbox"))
                )
                checkbox.click()
                time.sleep(3)
                self.driver.switch_to.default_content()  # type: ignore[attr-defined]
                if self._is_solved():
                    return True
            return False
        except Exception as exc:
            print(f"[hCaptcha] Lỗi: {exc}")
            try:
                self.driver.switch_to.default_content()  # type: ignore[attr-defined]
            except Exception:
                pass
            return False

    def _is_solved(self) -> bool:
        try:
            return (
                len(
                    self.driver.find_elements(  # type: ignore[attr-defined]
                        By.XPATH, "//*[contains(@class,'success')]"
                    )
                )
                > 0
            )
        except Exception:
            return False


# ─────────────────────────────────────────────────────────────────────────────
class UltimateCaptchaSolver:
    """Tích hợp toàn bộ solver, tự động phát hiện loại CAPTCHA."""

    def __init__(self, driver: Optional[object] = None) -> None:
        self.image_solver = ImageCaptchaSolver()
        self.recaptcha_solver: Optional[RecaptchaV2SolverFree] = None
        self.hcaptcha_solver: Optional[HCaptchaSolver] = None
        if driver is not None:
            self.set_driver(driver)

    def set_driver(self, driver: object) -> None:
        self.driver = driver
        self.recaptcha_solver = RecaptchaV2SolverFree(driver)
        self.hcaptcha_solver = HCaptchaSolver(driver)

    def detect_captcha_type(self) -> str:
        driver = getattr(self, "driver", None)
        if driver is None:
            return "none"
        src: str = driver.page_source.lower()  # type: ignore[attr-defined]
        if "recaptcha/api2" in src or "recaptcha/enterprise" in src:
            return "recaptcha_v2"
        if "recaptcha/api3" in src:
            return "recaptcha_v3"
        if "hcaptcha" in src:
            return "hcaptcha"
        if "captcha" in src and ("img" in src or "image" in src):
            return "image"
        return "none"

    def solve_captcha(self, timeout: int = 60) -> Tuple[bool, str]:
        driver = getattr(self, "driver", None)
        if driver is None:
            return False, "Driver chưa được thiết lập"
        time.sleep(2)
        ctype = self.detect_captcha_type()
        print(f"[CAPTCHA] Phát hiện: {ctype}")

        if ctype == "recaptcha_v2" and self.recaptcha_solver:
            ok = self.recaptcha_solver.solve_checkbox(timeout=timeout)
            return ok, "reCAPTCHA v2 đã giải" if ok else "reCAPTCHA v2 thất bại"

        if ctype == "hcaptcha" and self.hcaptcha_solver:
            ok = self.hcaptcha_solver.solve(timeout=timeout)
            return ok, "hCaptcha đã giải" if ok else "hCaptcha thất bại"

        if ctype == "image":
            imgs = driver.find_elements(By.TAG_NAME, "img")  # type: ignore[attr-defined]
            for img in imgs:
                src_attr: str = img.get_attribute("src") or ""
                if "captcha" in src_attr.lower():
                    result = self.image_solver.solve(src_attr)
                    if result:
                        return True, f"Image CAPTCHA đã giải: {result}"
            return False, "Không thể giải Image CAPTCHA"

        if ctype == "recaptcha_v3":
            return True, "reCAPTCHA v3 (không cần hành động)"

        return True, "Không phát hiện CAPTCHA"

    def solve_with_seleniumbase(self) -> bool:
        """Fallback sử dụng method có sẵn của SeleniumBase."""
        driver = getattr(self, "driver", None)
        if driver is None:
            return False
        try:
            if hasattr(driver, "uc_gui_click_captcha"):
                driver.uc_gui_click_captcha()  # type: ignore[attr-defined]
                return True
            if hasattr(driver, "solve_captcha"):
                driver.solve_captcha()  # type: ignore[attr-defined]
                return True
        except Exception as exc:
            print(f"[SeleniumBase fallback] Lỗi: {exc}")
        return False