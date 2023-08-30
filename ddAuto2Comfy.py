
import struct
import re
import os
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

class PNGExtractor:
    def __init__(self, inputfile):
        with open(inputfile, 'rb') as f:
            self.imgdata = f.read()

    def searchTNK(self, thunk):
        result = []
        dmy1 = 0
        thunk_type = b''
        while thunk_type != (b'IEND',):
            thunk_type = struct.unpack_from(">4s", self.imgdata, dmy1)
            if thunk_type == (thunk,):
                thunk_length = struct.unpack_from(">I", self.imgdata, dmy1-4)
                thunk_value = struct.unpack_from(">"+str(thunk_length[0])+"s", self.imgdata, dmy1+4)
                s = thunk_value[0].split(b'\x00', 1)
                if len(s) > 1:
                    key = s[0].decode('ascii')
                    value = s[1].decode('ascii', 'ignore')
                    result.append((key, value))
            dmy1 += 1
        return result

def process_image(image_path):
    # Extract the text from image2.png
    #image_path = 'image2.png'
    extractor = PNGExtractor(image_path)
    text_info = extractor.searchTNK(b'tEXt')

    extracted_text = ""
    if text_info:
        keyword, value = text_info[0]
        extracted_text = f"Keyword: {keyword}\nValue: {value}"

   # Extracting values based on the given specifications
    seed_match = re.search(r'Seed: (\d+)', extracted_text)
    steps_match = re.search(r'Steps: (\d+)', extracted_text)
    cfg_scale_match = re.search(r'CFG scale: ([\d.]+)', extracted_text)
    sample_match = re.search(r'Sampler: (.*?)?,', extracted_text)
    model_match = re.search(r'Model: (.*?)?,', extracted_text)
   
    size_match = re.search(r'Size: (\d+)x(\d+)', extracted_text)
    value_match = re.search(r'Value: (.*?)\nNegative prompt:', extracted_text, re.DOTALL)
    negative_prompt_match = re.search(r'Negative prompt: (.*?)\nSteps:', extracted_text, re.DOTALL)
    lora =  re.search(r'Lora: (.*?)', extracted_text)
    print('')
    print("----extracted text")
    print(extracted_text)
   
   
    seed = seed_match.group(1) if seed_match else None
    steps = steps_match.group(1) if steps_match else None
    cfg_scale = cfg_scale_match.group(1) if cfg_scale_match else None
    sample = sample_match.group(1) if sample_match else None
    model = model_match.group(1) if sample_match else None
    print("----model")
    print(model)
    xres = size_match.group(1) if size_match else None
    yres = size_match.group(2) if size_match else None
    value = value_match.group(1).strip() if value_match else None
    negative_prompt = negative_prompt_match.group(1).strip() if negative_prompt_match else None
    #
    # Using regular expression to find all matches for the pattern
    matches = re.findall(r'<(lora|lyco):(.*?):', extracted_text)
    # Extracting the required part from the matches
    result = [match[1] for match in matches]
    print('----- LoRA')
    print(result)


    # Read the content of template.json and replace
    with open('template.json', 'r') as file:
        template_content = file.read()

    template_content = template_content.replace("Seed:", seed)
    template_content = template_content.replace("Steps:", steps)
    template_content = template_content.replace("CFG scale:", cfg_scale)
    sample = sample.lower()
    sample = sample.replace(' ','_')
    sample = sample.replace('_a','_ancestral')
    sample = sample.replace('dpm++','dpmpp')
    sample = sample.replace('_karras','')
    print('=====')
    print(sample)
    sample = sample.replace('sde_karras','sde')
    sample = sample.replace('lms_karras','lms')
    print('----- Done!')
    model = model.replace('absolutereality_v10','absolutereality_v16')
    model = model.replace('epicrealism_pureEvolutionV3','epicrealism_pureEvolutionV4')
    negative_prompt = negative_prompt.replace("\n", "")
    #print(negative_prompt)
    template_content = template_content.replace("Sampler:", '\"' + sample + '\"')
    template_content = template_content.replace("Model:", '\"SD/' + model + '.safetensors\"')
    template_content = template_content.replace("XRES:", xres)
    template_content = template_content.replace("YRES:", yres)
    #template_content = template_content.replace("Value:", value)
    if '\"' not in value:
        template_content = template_content.replace("Value:", '\"' + value + '\"')
    else:
        template_content = template_content.replace("Value:", value)
    #template_content = template_content.replace('\"\"', '\"')
    template_content = template_content.replace("Negative prompt:", '\"' + negative_prompt + '\"')

    # Save the modified content
    with open('updated_workflow.json', 'w') as file:
        file.write(template_content)

def on_drop(event):
    image_path = event.data
    process_image(image_path)

root = TkinterDnD.Tk()
root.title("Drag and Drop Image")
root.geometry("400x200")

label = tk.Label(root, text="Drag and Drop your image here")
label.pack(pady=70)
label.drop_target_register(DND_FILES)
label.dnd_bind('<<Drop>>', on_drop)

root.mainloop()
