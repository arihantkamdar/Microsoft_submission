# Microsoft_submission

# Question Paper Extractor

This Python utility extracts structured question data from dual-column **JEE Mains PDF question papers with solutions**, including:

- Question text  
- Options  
- Answers  
- Solutions  
- Bounding boxes  
- Extracted diagrams or images (if present)  

It outputs:
- A **JSON** file per paper with structured data  
- Extracted **images** of diagrams for each question  

---

## 📂 Project Structure

```
project-root/
├── data/
│   ├── pdf/          # Input PDFs
│   ├── images/       # Output directories for question diagrams
│   └── json/         # Output JSONs with question details
├── main.py           # Entry point to run the parser
└── README.md         # This file
```

---

##  Features

-  Handles **dual-column PDFs** (splits pages into left/right halves)
-  Identifies:
  - Question numbers using `^\d+\.` pattern
  - Options using `\((1|2|3|4)\)`
  - Answer using pattern like `Ans. (3)`
  - Solutions starting with `Sol.`
-  Extracts bounding box for each question region
-  Captures **images** within question bounds if not blank
-  Saves structured output in **JSON format**

---

##  Requirements

Install the dependencies via:

```bash
pip install pdfplumber PyMuPDF pillow numpy
```

---

## 🚀 Usage

### Step 1: Add PDFs

Place your PDFs in the `data/pdf/` folder.

### Step 2: Run the script

```bash
python main.py
```

This will:
- Parse all PDFs in `data/pdf/`
- Generate:
  - JSON output in `data/json/`
  - Diagram images in `data/images/<pdf_name>/`

---

## 🧪 Example

For a PDF named:

```
data/pdf/13629-JEE-Main-2025-Question-Paper-with-Solution-22-Jan-Shift-1-PDF.pdf
```

You’ll get:

- `data/json/13629-JEE-Main-2025-Question-Paper-with-Solution-22-Jan-Shift-1-PDF.json`
- `data/images/13629-JEE-Main-2025-Question-Paper-with-Solution-22-Jan-Shift-1-PDF/`  
  (containing extracted diagram images)

---

## 🛠 Internals

### Key Functions

| Function              | Purpose                                                  |
|-----------------------|----------------------------------------------------------|
| `is_question_start`   | Detects question number start like `1.`                  |
| `is_answer_line`      | Detects answer line like `Ans. (3)`                      |
| `is_solution_start`   | Detects start of solution using `Sol.`                   |
| `group_words_by_line` | Groups words based on vertical position to form lines    |
| `extract_text_and_bounds` | Extracts the bounding box for each line             |
| `is_image_blank`      | Detects and skips nearly blank images                   |

---

## 📌 Notes

- Currently supports questions where:
  - Options are inline or multi-line with (1)...(4) format
  - Solutions follow immediately after "Sol."
- Diagrams are extracted from question bounding box and filtered using variance threshold to skip blanks.

---

## 📄 Sample PDF Source

Download sample JEE papers:  
🔗 [eSaral JEE Paper Downloads](https://www.esaral.com/jee/jee-main-2025-question-paper/)

---

## 🙌 Credits

Developed by **Arihant Kamdar**  
📧 For inquiries, improvements, or contributions, feel free to open an issue or pull request.
