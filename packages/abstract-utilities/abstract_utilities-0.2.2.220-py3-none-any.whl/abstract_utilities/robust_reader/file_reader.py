# file_reader.py
import os
import tempfile
import shutil
import logging
from typing import Union, Dict, List, Optional
import pandas as pd
import geopandas as gpd
import ezodf
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from docx import Document
import cv2
import numpy as np
from PIL import Image
import pytesseract
import PyPDF2
from pdf2image import convert_from_path
from ..json_utils import safe_json_loads,get_any_value,safe_read_from_json,get_value_from_path
from ..read_write_utils import write_to_file,read_from_file
from ..string_clean import eatAll
from ..path_utils import get_directory
from ..type_utils import is_media_type,get_all_file_types
from .pdf_utils import *
def if_none_return(obj,value):
    if obj is None:
        return value
    return obj
def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^a-zA-Z0-9\s:.,-]', '', text)
    text = text.strip()
    return text
def get_frame_number(file_path):
    file_path = '.'.join(file_path.split('.')[:-1])
    return int(file_path.split('_')[-1])
def sort_frames(frames=None,directory=None):
    if frames in [None,[]] and directory and os.path.isdir(directory):
        frames = get_all_file_types(types=['image'],directory=directory)
    frames = frames or []
    frames = sorted(
        frames,
        key=lambda x: get_frame_number(x) 
    )
    return frames
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s'
)
_logger = logging.getLogger(__name__)

# ─── PDF Functions ───────────────────────────────────────────────────────────

def is_pdf_path(file: str) -> bool:
    """Check if the provided file path corresponds to a valid PDF file."""
    basename = os.path.basename(file)
    filename,ext = os.path.splitext(basename)
    return is_file(file) and ext == '.pdf'

def read_pdf(file: str) -> PyPDF2.PdfReader:
    """Read and return a PDF reader object from the provided file path."""
    try:
        return PyPDF2.PdfReader(file)
    except Exception as e:
        _logger.error(f"Failed to read PDF '{file}': {e}")
        raise

def get_pdf_pages(pdf_file: Union[str, PyPDF2.PdfReader]) -> int:
    """Get the total number of pages in the PDF."""
    if isinstance(pdf_file, str):
        pdf_file = read_pdf(pdf_file)
    try:
        return len(pdf_file.pages)
    except Exception as e:
        _logger.error(f"Failed to get page count for PDF: {e}")
        return 0

def pdf_to_img_list(pdf_path: str, output_folder: Optional[str] = None) -> List[str]:
    """Convert a PDF file to a list of image files."""
    try:
        output_folder = if_none_return(get_directory(pdf_path), output_folder)
        basename = os.path.basename(pdf_path)
        filename,ext = os.path.splitext(basename)
        images = convert_from_path(pdf_path)
        image_paths = []
        for i, image in enumerate(images):
            image_path = os.path.join(output_folder, f"{file_name}_page_{i+1}.png")
            image.save(image_path, 'PNG')
            image_paths.append(image_path)
        return image_paths
    except Exception as e:
        _logger.error(f"Failed to convert PDF '{pdf_path}' to images: {e}")
        return []

def read_pdf_file(path: str, remove_phrases: Optional[List[str]] = None) -> pd.DataFrame:
    """Read text from a PDF file using OCR on converted images."""
    try:
        tmp_dir = tempfile.mkdtemp()
        image_paths = pdf_to_img_list(path, output_folder=tmp_dir)
        image_texts = []
        for image_path in image_paths:
            text = extract_text_from_image(image_path)
            if text:
                for phrase in (remove_phrases or []):
                    text = text.replace(phrase, '')
                image_texts.append({"frame": os.path.basename(image_path), "text": text})
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return pd.DataFrame(image_texts)
    except Exception as e:
        _logger.error(f"Failed to read PDF file '{path}': {e}")
        return pd.DataFrame()

# ─── OCR Functions ───────────────────────────────────────────────────────────

def preprocess_for_ocr(image_path: str) -> np.ndarray:
    """Preprocess an image for OCR to improve text extraction."""
    try:
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast = clahe.apply(gray)
        denoised = cv2.bilateralFilter(contrast, d=9, sigmaColor=75, sigmaSpace=75)
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, blockSize=11, C=2
        )
        kernel = np.ones((3, 3), np.uint8)
        morph = cv2.dilate(thresh, kernel, iterations=1)
        sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened = cv2.filter2D(morph, -1, sharpen_kernel)
        return sharpened
    except Exception as e:
        _logger.error(f"Failed to preprocess image '{image_path}': {e}")
        return np.array([])

def extract_text_from_image(image_path: str, preprocess: bool = True) -> str:
    """Extract text from an image using OCR."""
    try:
        if preprocess:
            processed_img = preprocess_for_ocr(image_path)
            if processed_img.size == 0:
                return ""
            pil_img = Image.fromarray(cv2.bitwise_not(processed_img))
        else:
            pil_img = Image.open(image_path)
        text = pytesseract.image_to_string(pil_img, lang='eng')
        return clean_text(text)
    except Exception as e:
        _logger.error(f"OCR Error for '{image_path}': {e}")
        return ""

def is_frame_analyzed(frame_file: str, video_text_data: List[Dict]) -> bool:
    """Check if a frame has already been analyzed."""
    for values in video_text_data:
        frame = values.get("frame") if isinstance(values, dict) else values
        if frame_file == frame:
            return True
    return False

def extract_text_from_frame(image_path: str, image_texts: List[Dict], remove_phrases: Optional[List[str]] = None) -> List[Dict]:
    """Extract text from a single image frame and append to results."""
    remove_phrases = remove_phrases or []
    basename = os.path.basename(image_path)
    if not is_frame_analyzed(basename, image_texts):
        if is_media_type(image_path, media_types=['image']):
            text = extract_text_from_image(image_path)
            if text:
                for phrase in remove_phrases:
                    text = text.replace(phrase, '')
                image_texts.append({"frame": basename, "text": text})
    return image_texts

def extract_image_texts_from_directory(directory: str, image_texts: Optional[List[Dict]] = None, remove_phrases: Optional[List[str]] = None) -> List[Dict]:
    """Extract text from all images in a directory."""
    image_texts = image_texts or []
    image_files = get_all_file_types(types=['image'], directory=directory)
    for image_path in image_files:
        image_texts = extract_text_from_frame(image_path, image_texts, remove_phrases)
    return sort_frames(image_texts)

# ─── Helper Functions ─────────────────────────────────────────────────────────

def convert_date_string(s: str) -> Optional[datetime]:
    """Convert a string to a datetime object."""
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        try:
            return pd.to_datetime(s)
        except Exception as e:
            _logger.warning(f"Failed to convert date string '{s}': {e}")
            return None

def read_from_file_with_multiple_encodings(file_path: str, encodings: Optional[List[str]] = None) -> Optional[str]:
    """Read a text file by trying multiple encodings."""
    COMMON_ENCODINGS = [
        'utf-8', 'utf-16', 'utf-16-be', 'utf-16-le', 'utf-32', 'utf-32-be', 'utf-32-le',
        'ISO-8859-1', 'windows-1252', 'latin-1'
    ]
    encodings = encodings or COMMON_ENCODINGS
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            continue
    _logger.error(f"No valid encoding found for '{file_path}'")
    return None

def ods_to_xlsx(ods_path: str, xlsx_path: str) -> None:
    """Convert ODS file to XLSX using pandas and openpyxl."""
    try:
        sheets = read_ods_file(ods_path)
        if not sheets:
            raise ValueError("No sheets found in ODS file")
        with pd.ExcelWriter(xlsx_path, engine='openpyxl') as writer:
            for sheet_name, df in sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    except Exception as e:
        _logger.error(f"Failed to convert ODS to XLSX: {e}")
        raise

# ─── Core Functions ───────────────────────────────────────────────────────────

def source_engine_for_ext(ext: str) -> Optional[str]:
    """Return the appropriate pandas engine for a file extension."""
    ext = ext.lower()
    mapping = {
        '.parquet': 'pyarrow',
        '.txt': 'python',
        '.csv': 'python',
        '.tsv': 'python',
        '.xlsx': 'openpyxl',
        '.xls': 'xlrd',
        '.xlsb': 'pyxlsb',
        '.ods': 'odf',
        '.geojson': 'GeoJSON',
    }
    return mapping.get(ext)

def is_valid_file_path(path: str) -> Optional[str]:
    """Check if the path is a valid file and return its extension."""
    if not (isinstance(path, str) and path.strip()):
        return None
    if os.path.isfile(path):
        return os.path.splitext(path)[1].lower()
    return None

def is_dataframe(obj) -> bool:
    """Check if the object is a DataFrame or GeoDataFrame."""
    return isinstance(obj, (pd.DataFrame, gpd.GeoDataFrame))

def create_dataframe(data=None, columns=None) -> pd.DataFrame:
    """Create a DataFrame from various input types."""
    if is_dataframe(data):
        return data.copy()
    data = data or {}
    if isinstance(data, dict):
        data = [data]
        if columns is None:
            all_keys = set()
            for row in data:
                if isinstance(row, dict):
                    all_keys.update(row.keys())
            columns = list(all_keys)
        if columns is False:
            columns = None
    try:
        return pd.DataFrame(data, columns=columns)
    except Exception as e:
        _logger.error(f"Failed to create DataFrame: {e}")
        return pd.DataFrame([], columns=columns)

def read_ods_file(path: str) -> Dict[str, pd.DataFrame]:
    """Read an ODS file and return a dictionary of DataFrames (one per sheet)."""
    if not is_valid_file_path(path):
        _logger.error(f"File not found or invalid: {path}")
        return {}
    try:
        doc = ezodf.opendoc(path)
    except Exception as e:
        _logger.error(f"Failed to open ODS document: {e}")
        return {}
    sheets: Dict[str, pd.DataFrame] = {}
    for sheet in doc.sheets:
        table_rows = []
        for row in sheet.rows():
            row_data = []
            for cell in row:
                if cell.value_type == 'date':
                    row_data.append(convert_date_string(str(cell.value)))
                else:
                    row_data.append(cell.value)
            table_rows.append(row_data)
        df = pd.DataFrame(table_rows)
        sheets[sheet.name] = df
        _logger.info(f"Processed sheet: {sheet.name}")
    return sheets

def read_ods_as_excel(path: str, xlsx_path: Optional[str] = None) -> pd.DataFrame:
    """Read an ODS file by converting it to XLSX."""
    if not is_valid_file_path(path):
        _logger.error(f"File not found or invalid: {path}")
        return pd.DataFrame()
    if xlsx_path is None:
        tmp_dir = tempfile.mkdtemp()
        xlsx_path = os.path.join(tmp_dir, os.path.basename(path) + '.xlsx')
        cleanup_temp = True
    else:
        cleanup_temp = False
    try:
        ods_to_xlsx(path, xlsx_path)
        df = pd.read_excel(xlsx_path, engine='openpyxl')
    except Exception as e:
        _logger.error(f"ODS→XLSX conversion or reading failed: {e}")
        df = pd.DataFrame()
    finally:
        if cleanup_temp:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    return df

def read_docx(path: str) -> pd.DataFrame:
    """Read a DOCX file and return its text content as a DataFrame."""
    try:
        doc = Document(path)
        text = '\n'.join(paragraph.text.strip() for paragraph in doc.paragraphs if paragraph.text.strip())
        cleaned_text = eatAll(text, ['\n', '', ' ', '\t'])
        return pd.DataFrame({'text': [cleaned_text]})
    except Exception as e:
        _logger.error(f"Failed to read DOCX file '{path}': {e}")
        return pd.DataFrame()

def read_text_file(path: str, sep: Optional[str] = None) -> pd.DataFrame:
    """Read a text file with multiple encoding attempts."""
    try:
        content = read_from_file_with_multiple_encodings(path)
        if content is None:
            raise ValueError("No valid encoding found")
        return pd.read_csv(path, sep=sep, encoding='utf-8')
    except Exception as e:
        _logger.error(f"Failed to read text file '{path}': {e}")
        return pd.DataFrame()

def read_image_file(path: str) -> pd.DataFrame:
    """Read text from an image file using OCR."""
    try:
        text = extract_text_from_image(path)
        return pd.DataFrame({'frame': [os.path.basename(path)], 'text': [text]})
    except Exception as e:
        _logger.error(f"Failed to read image file '{path}': {e}")
        return pd.DataFrame()

def filter_df(
    df: pd.DataFrame,
    nrows: Optional[int] = None,
    condition: Optional[pd.Series] = None,
    indices: Optional[List[int]] = None
) -> pd.DataFrame:
    """Apply filters to a DataFrame."""
    if nrows is not None:
        df = df.head(nrows)
    if condition is not None:
        df = df[condition]
    if indices is not None:
        df = df.iloc[indices]
    return df

def read_shape_file(path: str) -> Optional[gpd.GeoDataFrame]:
    """Read a shapefile or GeoJSON into a GeoDataFrame."""
    ext = is_valid_file_path(path)
    if not ext:
        _logger.error(f"Shape file not found: {path}")
        return None
    ext = ext.lower()
    try:
        if ext in ('.shp', '.cpg', '.dbf', '.shx'):
            return gpd.read_file(path)
        if ext == '.geojson':
            return gpd.read_file(path, driver='GeoJSON')
        if ext == '.prj':
            return gpd.read_file(path)
    except Exception as e:
        _logger.error(f"Failed to read spatial data ({path}): {e}")
        return None
    _logger.error(f"Unsupported spatial extension: {ext}")
    return None

def read_directory(root_path: str, remove_phrases: Optional[List[str]] = None) -> Dict[str, Union[pd.DataFrame, str]]:
    """Read all supported files in a directory and return a dictionary."""
    result = {}
    supported_extensions = (
        '.csv', '.tsv', '.txt', '.json', '.parquet',
        '.xlsx', '.xls', '.xlsb', '.ods', '.docx',
        '.shp', '.geojson', '.prj', '.cpg', '.dbf', '.shx',
        '.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.pdf'
    )
    image_texts = []
    try:
        for root, _, files in os.walk(root_path):
            for fname in files:
                if fname.lower().endswith(supported_extensions):
                    file_path = os.path.join(root, fname)
                    ext = os.path.splitext(fname)[1].lower()
                    if ext in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff'):
                        image_texts = extract_text_from_frame(file_path, image_texts, remove_phrases)
                    else:
                        df = get_df(file_path, remove_phrases=remove_phrases)
                        if df is not None:
                            result[file_path] = df
                        else:
                            result[file_path] = f"Failed to read: {file_path}"
        if image_texts:
            result['image_texts'] = pd.DataFrame(image_texts)
    except Exception as e:
        _logger.error(f"Failed to read directory '{root_path}': {e}")
    return result

class FileCollator:
    """Collate JSON files based on timestamp."""
    def __init__(self, files_list: List[str], key_value: str = 'query_response'):
        self.files_list = files_list or []
        self.key_value = key_value

    def get_collated_responses(self, files_list: Optional[List[str]] = None, key_value: Optional[str] = None) -> str:
        """Collate responses from JSON files by timestamp."""
        files_list = files_list or self.files_list
        key_value = key_value or self.key_value
        files = self.get_json_data(files_list, key_value)
        return self.collate_responses(files)

    def collate_responses(self, files: List[Dict]) -> str:
        """Combine JSON data in chronological order."""
        collate_str = ''
        nix_list = []
        for _ in files:
            lowest = self.get_oldest_first(files, nix_list)
            if lowest[0] is None:
                break
            nix_list.append(lowest[0])
            collate_str += '\n' + str(files[lowest[0]]["value"])
        return collate_str.strip()

    @staticmethod
    def get_json_data(files_list: List[str], key_value: str) -> List[Dict]:
        """Extract JSON data with timestamps and values."""
        files = []
        for file_path in files_list:
            try:
                data = safe_read_from_json(file_path)
                api_response = get_any_value(get_any_value(data, 'response'), 'api_response')
                response = get_any_value(data, 'response')
                created = get_any_value(response, 'created')
                if isinstance(created, list) and created:
                    created = created[0]
                files.append({'created': int(created), 'value': api_response})
            except Exception as e:
                _logger.error(f"Failed to process JSON file '{file_path}': {e}")
        return files

    @staticmethod
    def get_oldest_first(json_list: List[Dict], nix_list: List[int] = []) -> List[Optional[int]]:
        """Find the oldest JSON entry not yet processed."""
        lowest = [None, None]
        for i, values in enumerate(json_list):
            if i not in nix_list:
                if lowest[0] is None:
                    lowest = [i, int(values['created'])]
                elif int(values['created']) < int(lowest[1]):
                    lowest = [i, int(values['created'])]
        return lowest

def get_df(
    source: Union[
        str,
        pd.DataFrame,
        gpd.GeoDataFrame,
        dict,
        list,
        FileStorage
    ],
    nrows: Optional[int] = None,
    skiprows: Optional[Union[List[int], int]] = None,
    condition: Optional[pd.Series] = None,
    indices: Optional[List[int]] = None,
    remove_phrases: Optional[List[str]] = None
) -> Union[pd.DataFrame, gpd.GeoDataFrame, Dict[str, Union[pd.DataFrame, str]], None]:
    """
    Load a DataFrame or GeoDataFrame from various sources, then apply optional filters.
    If `source` is a directory, returns read_directory(source) instead (a dict).
    """
    # ─── Check for directory first ─────────────────────────────────────────────
    if isinstance(source, str) and os.path.isdir(source):
        _logger.info(f"Source is a directory: {source}")
        return read_directory(root_path=source, remove_phrases=remove_phrases)

    # ─── If already a DataFrame/GeoDataFrame, just filter and return ───────────
    if is_dataframe(source):
        _logger.info("Source is already a DataFrame/GeoDataFrame; applying filters.")
        return filter_df(source, nrows=nrows, condition=condition, indices=indices)

    if source is None:
        _logger.error("No source provided to get_df().")
        return None

    # ─── If source is a file path, read according to extension ───────────
    if isinstance(source, str) and os.path.isfile(source):
        ext = os.path.splitext(source)[1].lower()
        try:
            _logger.info(f"Loading file {source} with extension '{ext}'.")
            if ext in ('.csv', '.tsv', '.txt'):
                sep = {'.csv': ',', '.tsv': '\t', '.txt': None}.get(ext)
                df = pd.read_csv(source, skiprows=skiprows, sep=sep, nrows=nrows, encoding='utf-8')
            elif ext in ('.ods', '.xlsx', '.xls', '.xlsb'):
                engine = source_engine_for_ext(ext)
                if ext == '.ods':
                    df = read_ods_as_excel(source)
                else:
                    df = pd.read_excel(source, skiprows=skiprows, engine=engine, nrows=nrows)
            elif ext == '.json':
                df = safe_read_from_json(source)
            elif ext == '.parquet':
                df = pd.read_parquet(source)
            elif ext in ('.shp', '.cpg', '.dbf', '.shx', '.geojson', '.prj'):
                df = read_shape_file(source)
            elif ext == '.docx':
                df = read_docx(source)
            elif ext in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff'):
                df = read_image_file(source)
            elif ext == '.pdf':
                df = read_pdf_file(source, remove_phrases)
            else:
                df = read_from_file(source)
            return filter_df(df, nrows=nrows, condition=condition, indices=indices)
        except Exception as e:
            _logger.error(f"Failed to read '{source}': {e}")
            return None

    # ─── If source is FileStorage (uploaded) ───────────────────────────────────
    if isinstance(source, FileStorage):
        try:
            filename = secure_filename(source.filename or "uploaded.xlsx")
            ext = os.path.splitext(filename)[1].lower()
            _logger.info(f"Reading uploaded file: {filename}")
            if ext in ('.xlsx', '.xls', '.xlsb'):
                df = pd.read_excel(source.stream, nrows=nrows, engine=source_engine_for_ext(ext))
            elif ext in ('.csv', '.tsv'):
                sep = {'.csv': ',', '.tsv': '\t'}.get(ext)
                df = pd.read_csv(source.stream, nrows=nrows, sep=sep)
            elif ext == '.json':
                df = pd.read_json(source.stream)
            elif ext == '.docx':
                tmp_dir = tempfile.mkdtemp()
                tmp_path = os.path.join(tmp_dir, filename)
                source.save(tmp_path)
                df = read_docx(tmp_path)
                shutil.rmtree(tmp_dir, ignore_errors=True)
            elif ext in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff'):
                tmp_dir = tempfile.mkdtemp()
                tmp_path = os.path.join(tmp_dir, filename)
                source.save(tmp_path)
                df = read_image_file(tmp_path)
                shutil.rmtree(tmp_dir, ignore_errors=True)
            elif ext == '.pdf':
                tmp_dir = tempfile.mkdtemp()
                tmp_path = os.path.join(tmp_dir, filename)
                source.save(tmp_path)
                df = read_pdf_file(tmp_path, remove_phrases)
                shutil.rmtree(tmp_dir, ignore_errors=True)
            else:
                _logger.error(f"Unsupported uploaded file extension: {ext}")
                return pd.DataFrame()
            return filter_df(df, nrows=nrows, condition=condition, indices=indices)
        except Exception as e:
            _logger.error(f"Failed to read FileStorage: {e}")
            return None

    # ─── If source is dict or list, turn into DataFrame ────────────────────────
    if isinstance(source, (dict, list)):
        _logger.info("Creating DataFrame from in-memory data structure.")
        df = create_dataframe(source)
        return filter_df(df, nrows=nrows, condition=condition, indices=indices)

    _logger.error(f"Unsupported source type: {type(source)}")
    return None
def read_file_as_text(path: str) -> str:
    """
    Given a filesystem path, return its contents as a single string.
    
    1) If ext indicates plain-text (.txt, .md, .csv, .tsv, .log), read directly.
    2) Else attempt get_df(path) → DataFrame or GeoDataFrame → convert to CSV.
    3) If get_df returns dict (e.g. multiple sheets), join each sheet’s .to_string().
    4) If get_df returns list, convert to a DataFrame then CSV. Otherwise repr(...).
    
    Raises:
        FileNotFoundError if path does not exist.
        ValueError for unsupported or unreadable files.
    """
    if not isinstance(path, str) or not os.path.isfile(path):
        raise FileNotFoundError(f"Not a valid file: {path!r}")

    ext = os.path.splitext(path)[1].lower()

    # 1) Plain-text
    if ext in SUPPORTED_TEXT_EXTENSIONS:
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error reading text file {path!r}: {e}")

    # 2) Attempt to load via get_df()
    df_or_gdf = get_df(path)
    if df_or_gdf is None:
        raise ValueError(f"Could not read file as DataFrame: {path!r}")

    # 2a) If DataFrame or GeoDataFrame, convert to CSV
    if isinstance(df_or_gdf, (pd.DataFrame, gpd.GeoDataFrame)):
        try:
            if isinstance(df_or_gdf, gpd.GeoDataFrame):
                gdf = df_or_gdf.copy()
                gdf['geometry'] = gdf['geometry'].apply(lambda g: g.wkt if g is not None else '')
                return gdf.to_csv(index=False)
            else:
                return df_or_gdf.to_csv(index=False)
        except Exception as e:
            raise ValueError(f"Error converting DataFrame to text for {path!r}: {e}")

    # 3) If dict (e.g. read_ods_file returning {sheet_name: DataFrame})
    if isinstance(df_or_gdf, dict):
        parts = []
        for key, val in df_or_gdf.items():
            parts.append(f"=== Sheet: {key} ===\n{val.to_string(index=False)}")
        return "\n\n――――――――――――――――――\n\n".join(parts)

    # 4) If list of dicts, convert to DataFrame → CSV
    if isinstance(df_or_gdf, list):
        try:
            temp_df = pd.DataFrame(df_or_gdf)
            return temp_df.to_csv(index=False)
        except Exception:
            return str(df_or_gdf)

    # 5) Otherwise fallback to repr()
    return repr(df_or_gdf)

