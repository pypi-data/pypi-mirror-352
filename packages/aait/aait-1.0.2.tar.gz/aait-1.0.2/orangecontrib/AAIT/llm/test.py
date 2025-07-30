from gpt4all import GPT4All

# Load model
model = GPT4All(
    r"C:\Users\lucas\aait_store\Models\NLP\Qwen2.5-Dyanka-7B-Preview.Q6_K.gguf",
    model_path=r"C:\Users\lucas\aait_store\Models\NLP\Qwen2.5-Dyanka-7B-Preview.Q6_K.gguf",
    n_ctx=900,
    device="cuda",
    allow_download=False
)

# Manually enter the chat session context
chat_session = model.chat_session()
chat = chat_session.__enter__()

try:
    print("🤖 Chatbot is ready! Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        for token in chat.generate(user_input, max_tokens=512, streaming=True):
            print(token, end="")
        print()

finally:
    # Make sure the session is properly closed
    chat_session.__exit__(None, None, None)







# from gpt4all import GPT4All
# model = GPT4All(r"C:\Users\lucas\aait_store\Models\NLP\Qwen2.5-Dyanka-7B-Preview.Q6_K.gguf",
#                 model_path=r"C:\Users\lucas\aait_store\Models\NLP\Qwen2.5-Dyanka-7B-Preview.Q6_K.gguf",
#                 n_ctx=900, device="cuda", allow_download=False) # downloads / loads a 4.66GB LLM
# # Start a chat session
# with model.chat_session():
#     print("🤖 Chatbot is ready! Type 'exit' to quit.\n")
#
#     while True:
#         user_input = input("You: ")
#         if user_input.lower() in ["exit", "quit"]:
#             print("👋 Goodbye!")
#             break
#
#         for token in model.generate(user_input, max_tokens=512, streaming=True):
#             print(token, end="")



# import fitz  # PyMuPDF
# import numpy as np
# import cv2
# import os
# import shutil
# from test_functions import *
#
#
#
# pdf_path = r"C:\Users\lucas\Desktop\test\Plans\65280776-003_-A.pdf"
# pdf_cartouche = r"C:\Users\lucas\Desktop\test\cartouche.pdf"
# pdf_material = r"C:\Users\lucas\Desktop\test\material.pdf"
# img_cartouche = r"C:\Users\lucas\Desktop\test\cartouche.png"
# img_material = r"C:\Users\lucas\Desktop\test\material.png"
# img_pictograms = r"C:\Users\lucas\Desktop\test\found_pictograms.png"
# img_enlarged_picto = r"C:\Users\lucas\Desktop\test\found_pictograms_text.png"
#
# picto_path_1 = r"C:\Users\lucas\Desktop\test\Picto1.png"
# picto_path_2 = r"C:\Users\lucas\Desktop\test\Picto2.png"
# pictograms = [cv2.imread(picto_path_1), cv2.imread(picto_path_2)]
# labels = ["Hexag1", "Hexag2"]
#
#
# # Load the pdf
# doc = fitz.open(pdf_path)
#
# # Iterate through pages
# for num_page in range(len(doc)):
#     # Load page
#     page = doc.load_page(num_page)
#     # Create an OpenCV version
#     page_cv2 = page_to_image(page)
#     # Locate the cartouche
#     cartouche_cv2, bbox = find_cartouche(page, output_png_path=img_cartouche, output_pdf_path=pdf_cartouche)
#     print("Cartouche found")
#     # Locate the "MATIERE/MATERIAL" cell
#     crop_material_cv2 = find_cell(page, pattern="MATIERE/MATERIAL", output_png_path=img_material, output_pdf_path=pdf_material)
#     print("MATIERE/MATERIAL cell found")
#     # Identify which pictogram is contained in it
#     best_pictogram, score, label = find_best_match(crop_material_cv2, pictograms, labels=labels)
#     if score < 0.1:
#         print("No pictogram has been found in MATIERE/MATERIAL")
#     else:
#         print(f"Found a pictogram : {label} - confidence {score}")
#         # Search for this pictogram in the entire PDF
#         rectangles, confidences = find_pictogram_in_image(page_cv2, best_pictogram, threshold=0.8, output_png_path=img_pictograms)
#         print(f"Found {len(rectangles)} rectangles:", rectangles)
#         print("Confidences:", confidences)
#         # Merge the similar rectangles
#         rectangles, confidences = merge_rectangles(rectangles, confidences)
#         print(f"{len(rectangles)} rectangles after merging:", rectangles)
#         print(f"Confidences:", confidences)
#         if rectangles:
#             # Exclude detected pictograms that are present in the cartouche
#             filtered_rectangles = exclude_inner_rectangles(bbox, rectangles)
#             print(f"{len(filtered_rectangles)} rectangles not in cartouche")
#             # Get areas around detected pictograms ?????????
#             extracted_texts = []
#             for rect in filtered_rectangles:
#                 enlarged = enlarge_opencv_bbox(rect, 0, 0, 9, 3)
#                 img = draw_cv2_bbox(page_cv2, rect, color=(255, 0, 0))
#                 img = draw_cv2_bbox(img, enlarged, color=(255, 0, 0))
#                 cv2.imwrite(img_enlarged_picto, img)
#                 crop_picto_text = crop_cv2_bbox(page_cv2, enlarged)
#                 crop_picto_text = cv2.cvtColor(crop_picto_text, cv2.COLOR_BGR2RGB)
#                 # Get text in these areas
#                 result = apply_OCR(crop_picto_text, r"C:\Users\lucas\aait_store\Models\ComputerVision\.paddleocr\whl")
#                 all_t = []
#                 for line in result[0]:  # result[0] because it's for one image
#                     t = line[1][0]  # line[1] is ("text", confidence), so line[1][0] is the text
#                     all_t.append(t)
#                 full_string =  "\n".join(all_t)
#                 print("Full Extraction :\n", full_string)
#
#                 # Search for materials with database
#     break