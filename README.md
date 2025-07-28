
# 📘 Question Paper Extractor

A Python utility to extract structured question data—including diagrams—from dual-column **JEE Mains PDF question papers with solutions**.

---

## 📦 Output

- Structured **JSON** per paper with:
  - Question text  
  - Options  
  - Answers  
  - Solutions  
  - Bounding boxes  
  - Diagram/image file names (if present)

- Extracted **images** for questions containing diagrams

---

## 🧾 Project Structure

```
project-root/
├── data/
│   ├── pdf/          # Input PDFs
│   ├── images/       # Output directories for question diagrams
│   └── json/         # Output JSONs with question details
├── simple_parser.py  # Entry point to run the parser
└── README.md         # Documentation
```

---

## 🔧 Features

- ✅ Handles **dual-column PDFs**
- ✅ Identifies question parts:
  - Questions using `^\d+\.` pattern
  - Options using `(1)` to `(4)`
  - Answers using `Ans. (X)` format
  - Solutions starting with `Sol.`
- ✅ Extracts bounding boxes for question content
- ✅ Captures and filters out blank diagrams
- ✅ Saves clean structured output as **JSON**

---

## 🛠 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

1. **Add PDFs**  
   Drop your question papers in `data/pdf/`.

2. **Run the extractor**  
   ```bash
   python simple_parser.py
   ```

3. **Output**  
   - JSON files → `data/json/`  
   - Diagram images → `data/images/<pdf_name>/`

---

## 📁 Example

For a PDF file:

```
data/pdf/13629-JEE-Main-2025-Question-Paper-with-Solution-22-Jan-Shift-1-PDF.pdf
```

The output includes:
- `data/json/13629-JEE-Main-2025-Question-Paper-with-Solution-22-Jan-Shift-1-PDF.json`
- Diagram images in:
  `data/images/13629-JEE-Main-2025-Question-Paper-with-Solution-22-Jan-Shift-1-PDF/`

---

## 🧠 High-Level Approach

### 1. PDF Initialization
- Load each PDF using:
  - `pdfplumber` for extracting text and word positions
  - `PyMuPDF (fitz)` for extracting diagrams

### 2. Page Splitting
- Each page is split vertically into two halves:
  - Left (`Part 1`) and Right (`Part 2`) for dual-column layout

### 3. Word Grouping
- Group words into lines using their vertical (`y`) positions
- Ensures multi-line questions and options are handled properly

### 4. Question Parsing
- Detects:
  - Start of question (e.g., `1.`)
  - Options in form `(1)`, `(2)`, ...
  - Answers like `Ans. (3)`
  - Solutions starting with `Sol.`
- Maintains:
  - Question lines
  - Options dictionary
  - Solution lines
  - Bounding box coordinates
  - Image references

### 5. Diagram Extraction
- Calculate bounding box of each question
- Render it using PyMuPDF
- If image is not blank (checked by pixel variance), save it
- Link image filename in JSON

### 6. Structured Output
- Each question saved with:
  - `question_number`, `question_text`, `options`, `answer`, `solution`, `images`, etc.
- Saved in a `.json` file

### 7. Batch Mode
- The `runner()` supports multiple PDFs from `data/pdf/`
- Creates corresponding `images/` and `json/` folders

---

## 🔎 Key Functions

| Function              | Purpose                                                  |
|-----------------------|----------------------------------------------------------|
| `is_question_start`   | Detects question start using regex                       |
| `is_answer_line`      | Detects line starting with `Ans.`                        |
| `is_solution_start`   | Detects solution lines starting with `Sol.`              |
| `group_words_by_line` | Groups words to form lines using vertical proximity      |
| `extract_text_and_bounds` | Computes bounding boxes for lines                    |
| `is_image_blank`      | Filters out blank diagram images                         |

---

## 🔗 Sample PDF Source

Download sample PDFs:  
📥 [eSaral JEE Question Papers](https://www.esaral.com/jee/jee-main-2025-question-paper/)

---

## 🙌 Credits

Developed by **Arihant Kamdar**  
📧 For inquiries, improvements, or contributions, feel free to open an issue or pull request.

---
