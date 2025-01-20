# deki

**deki** is an ML model (or several models) that detects UI elements in screenshots (such as containers, text, and icons) and provides structured descriptions of those elements. It can help with:

- Generating code for LLMs that need structured UI information.
- Automating device interactions by providing precise bounding box coordinates.
- Assisting visually impaired users by describing the UI.

---

## How It Works

1. **Object Detection**  
   Runs YOLO (trained to detect `View` containers, `Text`, `ImageView` icons/images, and `Line` elements) on the input image.

2. **Cropping & Processing**  
   - **Text boxes**: Crop each box and use a deep neural network (DNN) to enhance the text region, then perform OCR and apply a spell checker to correct mistakes.  
   - **View/Line boxes**: Extract background color and alpha information.  
   - **ImageView boxes**: Determine if the element is an icon-like graphic or a real image (e.g., a person or a car).

3. **Image Captioning (Optional)**  
   Use an image captioning model (e.g., BLIP-2, LLaMA-vision, etc.) to produce an overall description of the screenshot content.

---

## Where It Can Be Used

The ML model creates a long description of the screenshot that can be used for various purposes:

1. **Code Generation**: Provide structured UI details for LLMs that need vision-based input.  
2. **Device Control**: Automate interactions by detecting exact coordinates of all elements.  
3. **Accessibility**: Help visually impaired users understand the UI structure.

---

## Usage

Install dependencies (Python 3.12 recommended):

```bash
pip install -r requirements.txt
```

Full Pipeline

```bash
python3.12 wrapper.py \
  --input_image ./bb_1.jpeg \
  --weights_file ./best.pt \
  --icon_detection_path ./icon-image-detection-model.keras
```

YOLO-Only

```bash
python3.12 yolo_script.py \
  bb_1.jpeg \
  ./best.pt
```

And don't forget to include your HuggingFace and OpenAI tokens if you use blip2 or ChatGPT.

Also, to use this version you need to install llama-3.2-11b via ollama.

## Plans

    * Fine-tune the image captioning model for more accurate UI descriptions.
    * Fine-tune an LLM for generating UI code from detected elements.
    * Make the image captioning functionality optional.
    * Increase accuracy of the YOLO model (current model was trained on only 486 images).
    * Increase accuracy of the icon detection model by improving training data quality.

## Examples

You can see examples in the result/ and output/ folders.

I have not used the best examples that do not have errors, so as not to give
people a false impression of the accuracy of the model. The examples you see
are approximately the standard result that can usually be obtained using this
model.

## Contributing

Pull requests are welcome! 

## License

GPLv3
