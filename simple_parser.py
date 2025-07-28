import os
import pdfplumber
import fitz  # PyMuPDF
import re
import json
from collections import defaultdict
from PIL import Image
import io
import numpy as np

def is_question_start(text):
    """
    REGEX FOR GETTING THE STARTING OF QUESTION AS QUESTION CAN BE MULTILINE
    :param text:
    :return:
    """
    return re.match(r'^\d+\.', text.strip()) is not None

def is_answer_line(text):
    """
    REGEX FOR MATCHING ANSWER
    :param text:
    :return:
    """
    return re.match(r'Ans\.\s*\(?(\d)\)?', text.strip()) is not None

def is_solution_start(text):
    """
    No regex requires simple string matching works
    :param text:
    :return:
    """
    return text.strip().startswith("Sol.")

def extract_text_and_bounds(line):
    """
    Get geometry of the line
    :param line:
    :return:
    """
    sorted_line = sorted(line, key=lambda w: w['x0'])
    text = " ".join([w['text'] for w in sorted_line])
    top = min(w['top'] for w in sorted_line)
    bottom = max(w['bottom'] for w in sorted_line)
    left = min(w['x0'] for w in sorted_line)
    right = max(w['x1'] for w in sorted_line)
    return text.strip(), top, bottom, left, right

def group_words_by_line(words, y_tolerance=3.0):
    lines = defaultdict(list)
    for word in words:
        y0 = round(word['top'] / y_tolerance) * y_tolerance
        lines[y0].append(word)
    return list(lines.values())

def is_image_blank(img, threshold=10):
    """Check if an image is mostly blank by calculating pixel variance."""
    img_array = np.array(img.convert('L'))  # Convert to grayscale
    variance = np.var(img_array)
    return variance < threshold

def extract_jee_questions(pdf_path, output_json="data/jsons/questions_output.json", image_dir="data/images"):
    questions = []
    os.makedirs(image_dir, exist_ok=True)  # Create image directory if it doesn't exist

    # Open PDF with pdfplumber for text extraction
    with pdfplumber.open(pdf_path) as pdf:
        # Open PDF with PyMuPDF for image extraction
        pdf_doc = fitz.open(pdf_path)

        for page_num, (page, fitz_page) in enumerate(zip(pdf.pages, pdf_doc), start=1):
            width = page.width
            height = page.height
            mid_x = width / 2
            # splitting the page into two parts as the dataset used is having two columns

            for side, crop_box in [("Part 1", (0, 0, mid_x, height)), ("Part 2", (mid_x, 0, width, height))]:
                crop = page.crop(crop_box)
                words = crop.extract_words(use_text_flow=True, keep_blank_chars=True)
                lines = group_words_by_line(words)

                current_q_lines = []
                current_solution_lines = []
                current_bounds = {'top': float('inf'), 'bottom': 0, 'left': float('inf'), 'right': 0}
                options = {}
                answer = None
                question_number = None
                in_solution = False
                current_images = []

                for line in lines:
                    text, top, bottom, left, right = extract_text_and_bounds(line)

                    if is_question_start(text): # start of question
                        if current_q_lines and question_number is not None:
                            question_text = " ".join(current_q_lines)
                            solution_text = " ".join(current_solution_lines) if current_solution_lines else ""
                            questions.append({
                                "question_number": question_number,
                                "question_text": question_text,
                                "options": options,
                                "answer": answer,
                                "solution": solution_text,
                                "bounds": current_bounds,
                                "page": page_num,
                                "side": side,
                                "images": current_images
                            })

                        current_q_lines = [text]
                        current_solution_lines = []
                        current_images = []
                        question_number = int(re.match(r'^(\d+)', text).group(1))
                        current_bounds = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
                        options = {}
                        answer = None
                        in_solution = False

                    elif is_answer_line(text): # finding answer
                        ans_match = re.search(r'Ans\.\s*\(?(\d)\)?', text)
                        if ans_match:
                            answer = f"({ans_match.group(1)})"
                        current_bounds['top'] = min(current_bounds['top'], top)
                        current_bounds['bottom'] = max(current_bounds['bottom'], bottom)
                        current_bounds['left'] = min(current_bounds['left'], left)
                        current_bounds['right'] = max(current_bounds['right'], right)

                    elif is_solution_start(text): # finding solution
                        in_solution = True
                        current_solution_lines.append(text.replace("Sol.", "").strip())
                        current_bounds['top'] = min(current_bounds['top'], top)
                        current_bounds['bottom'] = max(current_bounds['bottom'], bottom)
                        current_bounds['left'] = min(current_bounds['left'], left)
                        current_bounds['right'] = max(current_bounds['right'], right)

                    elif re.findall(r'\((1|2|3|4)\)', text):
                        # finding options as opetion always starts from (1) or (2) or (3) or (4)
                        for opt in re.findall(r'\((\d)\)\s*([^\(\)]+)', text):
                            key = f"({opt[0]})"
                            options[key] = opt[1].strip()
                        current_bounds['top'] = min(current_bounds['top'], top)
                        current_bounds['bottom'] = max(current_bounds['bottom'], bottom)
                        current_bounds['left'] = min(current_bounds['left'], left)
                        current_bounds['right'] = max(current_bounds['right'], right)

                    else:
                        if in_solution:
                            current_solution_lines.append(text)
                        else:
                            current_q_lines.append(text)
                        current_bounds['top'] = min(current_bounds['top'], top)
                        current_bounds['bottom'] = max(current_bounds['bottom'], bottom)
                        current_bounds['left'] = min(current_bounds['left'], left)
                        current_bounds['right'] = max(current_bounds['right'], right)

                # Render question region as image to capture diagrams
                if question_number is not None:
                    try:
                        """
                        Image Extraction is not perfect"""
                        img_bbox = (
                            max(0, current_bounds['left']  if side == "Part 1" else current_bounds['left'] ),
                            max(0, current_bounds['top'] ),
                            min(width, current_bounds['right'] if side == "Part 1" else current_bounds['right']),
                            min(height, current_bounds['bottom'])
                        )
                        if img_bbox[2] <= img_bbox[0] or img_bbox[3] <= img_bbox[1]:
                            print(f"Skipping invalid bbox for question {question_number} on page {page_num}: {img_bbox}")
                        else:
                            pix = fitz_page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72), clip=img_bbox)
                            img = Image.open(io.BytesIO(pix.tobytes()))
                            if not is_image_blank(img):
                                img_filename = f"page{page_num}_q{question_number}_diagram.png"
                                save_path = os.path.join(image_dir, img_filename)
                                img.save(save_path)
                                current_images.append(img_filename)
                            else:
                                print(f"Skipped blank diagram for question {question_number} on page {page_num}")
                    except Exception as e:
                        print(f"Error rendering diagram for question {question_number} on page {page_num}: {e}")

                if current_q_lines and question_number is not None:
                    question_text = " ".join(current_q_lines)
                    solution_text = " ".join(current_solution_lines) if current_solution_lines else ""
                    # final dict item appended in list
                    questions.append({
                        "question_number": question_number,
                        "question_text": question_text,
                        "options": options,
                        "answer": answer,
                        "solution": solution_text,
                        "bounds": current_bounds,
                        "page": page_num,
                        "side": side,
                        "images": current_images
                    })

        pdf_doc.close()

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)
        # writing json here
    print(f"Saved extracted questions to {output_json}")



def runner(data_dir,pdf_dir):
    pdf_files = os.listdir(pdf_dir)
    images_folder_name = []
    json_files_name = []
    for file in pdf_files:
        file_name = file.split(".")[0] # not the best way ideally I would be using Pathlib
        image_path = os.path.join(data_dir,f"images/{file_name}")
        os.makedirs(image_path,exist_ok = True)
        images_folder_name.append(image_path)

        json_file_path_name = os.path.join(data_dir,f"json/{file_name}.json")
        json_files_name.append(json_file_path_name)
    for i in range(len(pdf_files)):
        pdf_file_path = os.path.join(pdf_dir,pdf_files[i])
        image_dir = images_folder_name[i]
        json_file_name = json_files_name[i]
        extract_jee_questions(pdf_path=pdf_file_path,output_json=json_file_name,image_dir=image_dir)


# sample data dpwnload link: https://www.esaral.com/jee/jee-main-2025-question-paper/
if __name__ == "__main__":
    # extract_jee_questions("data/raw/13629-JEE-Main-2025-Question-Paper-with-Solution-22-Jan-Shift-1-PDF.pdf",
    #                       output_json="data/jsons/13629-JEE-Main-2025-Question-Paper-with-Solution-22-Jan-Shift-1-PDF.json",
    #                       image_dir="data/images/13629-JEE-Main-2025-Question-Paper-with-Solution-22-Jan-Shift-1-PDF")
    runner(data_dir= "data", pdf_dir="data/pdf")