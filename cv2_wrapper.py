"""
HAADS SIH 26050 - Headless OpenCV Safe Wrapper
Attempts native cv2 import first.
If libGL.so.1 or headless OS error occurs on Streamlit Cloud, falls back to PIL / numpy
implementations so the application never crashes with ImportError.
"""

import sys
import io
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Constants
FONT_HERSHEY_SIMPLEX = 0
IMREAD_COLOR = 1
COLOR_BGR2RGB = 4

try:
    import cv2
    _NATIVE_CV2 = True
except (ImportError, Exception) as err:
    print(f"[cv2_wrapper] Native OpenCV import failed ({err}). Using PIL fallback wrapper.")
    _NATIVE_CV2 = False
    cv2 = None

# Inject fallback wrapper into sys.modules if native cv2 is unavailable
if not _NATIVE_CV2:
    sys.modules['cv2'] = sys.modules[__name__]



def imdecode(buf, flags=1):
    if _NATIVE_CV2 and cv2 is not None:
        try:
            return cv2.imdecode(buf, flags)
        except Exception:
            pass
    try:
        image_bytes = buf.tobytes() if hasattr(buf, "tobytes") else bytes(buf)
        pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        rgb_np = np.array(pil_img)
        bgr_np = rgb_np[:, :, ::-1].copy()
        return bgr_np
    except Exception as e:
        print(f"[cv2_wrapper] imdecode fallback error: {e}")
        return None


def imwrite(filename, img_bgr):
    if _NATIVE_CV2 and cv2 is not None:
        try:
            return cv2.imwrite(filename, img_bgr)
        except Exception:
            pass
    try:
        if img_bgr is None:
            return False
        rgb_np = img_bgr[:, :, ::-1] if (len(img_bgr.shape) == 3 and img_bgr.shape[2] == 3) else img_bgr
        pil_img = Image.fromarray(rgb_np)
        pil_img.save(filename)
        return True
    except Exception as e:
        print(f"[cv2_wrapper] imwrite fallback error: {e}")
        return False


def imread(filename, flags=1):
    if _NATIVE_CV2 and cv2 is not None:
        try:
            return cv2.imread(filename, flags)
        except Exception:
            pass
    try:
        pil_img = Image.open(filename).convert("RGB")
        rgb_np = np.array(pil_img)
        bgr_np = rgb_np[:, :, ::-1].copy()
        return bgr_np
    except Exception as e:
        print(f"[cv2_wrapper] imread fallback error: {e}")
        return None


def cvtColor(img, code):
    if _NATIVE_CV2 and cv2 is not None:
        try:
            return cv2.cvtColor(img, code)
        except Exception:
            pass
    if img is None:
        return None
    if len(img.shape) == 3 and img.shape[2] == 3:
        return img[:, :, ::-1].copy()
    return img


def rectangle(img, pt1, pt2, color, thickness=1):
    if _NATIVE_CV2 and cv2 is not None:
        try:
            return cv2.rectangle(img, pt1, pt2, color, thickness)
        except Exception:
            pass
    try:
        rgb_color = (color[2], color[1], color[0]) if len(color) >= 3 else color
        rgb_np = img[:, :, ::-1] if (len(img.shape) == 3 and img.shape[2] == 3) else img
        pil_img = Image.fromarray(rgb_np)
        draw = ImageDraw.Draw(pil_img)
        x1, y1 = pt1
        x2, y2 = pt2
        for t in range(max(1, thickness)):
            draw.rectangle([x1 - t, y1 - t, x2 + t, y2 + t], outline=rgb_color)
        res_rgb = np.array(pil_img)
        res_bgr = res_rgb[:, :, ::-1].copy()
        img[:] = res_bgr[:]
        return img
    except Exception:
        return img


def putText(img, text, org, fontFace, fontScale, color, thickness=1):
    if _NATIVE_CV2 and cv2 is not None:
        try:
            return cv2.putText(img, text, org, fontFace, fontScale, color, thickness)
        except Exception:
            pass
    try:
        rgb_color = (color[2], color[1], color[0]) if len(color) >= 3 else color
        rgb_np = img[:, :, ::-1] if (len(img.shape) == 3 and img.shape[2] == 3) else img
        pil_img = Image.fromarray(rgb_np)
        draw = ImageDraw.Draw(pil_img)
        x, y = org
        draw.text((x, max(0, y - 10)), text, fill=rgb_color)
        res_rgb = np.array(pil_img)
        res_bgr = res_rgb[:, :, ::-1].copy()
        img[:] = res_bgr[:]
        return img
    except Exception:
        return img


def line(img, pt1, pt2, color, thickness=1):
    if _NATIVE_CV2 and cv2 is not None:
        try:
            return cv2.line(img, pt1, pt2, color, thickness)
        except Exception:
            pass
    try:
        rgb_color = (color[2], color[1], color[0]) if len(color) >= 3 else color
        rgb_np = img[:, :, ::-1] if (len(img.shape) == 3 and img.shape[2] == 3) else img
        pil_img = Image.fromarray(rgb_np)
        draw = ImageDraw.Draw(pil_img)
        draw.line([pt1[0], pt1[1], pt2[0], pt2[1]], fill=rgb_color, width=thickness)
        res_rgb = np.array(pil_img)
        res_bgr = res_rgb[:, :, ::-1].copy()
        img[:] = res_bgr[:]
        return img
    except Exception:
        return img


def circle(img, center, radius, color, thickness=1):
    if _NATIVE_CV2 and cv2 is not None:
        try:
            return cv2.circle(img, center, radius, color, thickness)
        except Exception:
            pass
    try:
        rgb_color = (color[2], color[1], color[0]) if len(color) >= 3 else color
        rgb_np = img[:, :, ::-1] if (len(img.shape) == 3 and img.shape[2] == 3) else img
        pil_img = Image.fromarray(rgb_np)
        draw = ImageDraw.Draw(pil_img)
        x, y = center
        r = radius
        if thickness == -1:
            draw.ellipse([x - r, y - r, x + r, y + r], fill=rgb_color)
        else:
            draw.ellipse([x - r, y - r, x + r, y + r], outline=rgb_color, width=thickness)
        res_rgb = np.array(pil_img)
        res_bgr = res_rgb[:, :, ::-1].copy()
        img[:] = res_bgr[:]
        return img
    except Exception:
        return img


def setNumThreads(n):
    if _NATIVE_CV2 and cv2 is not None:
        try:
            cv2.setNumThreads(n)
        except Exception:
            pass
