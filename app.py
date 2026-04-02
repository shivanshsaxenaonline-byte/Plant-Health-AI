from flask import Flask, render_template, request
import tensorflow as tf
import numpy as np
from PIL import Image
import io

app = Flask(__name__)

model = tf.keras.models.load_model("Pro_Universal_Crop_Model.h5")

class_names = [
    '00_Unknown', 'Cotton_diseased_cotton_leaf', 'Cotton_diseased_cotton_plant', 
    'Cotton_fresh_cotton_leaf', 'Cotton_fresh_cotton_plant', 'Maize_Blight', 
    'Maize_Common_Rust', 'Maize_Gray_Leaf_Spot', 'Maize_Healthy', 
    'Pepper__bell___Bacterial_spot', 'Pepper__bell___healthy', 'Potato___Early_blight', 
    'Potato___Late_blight', 'Potato___healthy', 'Rice_Bacterial_leaf_blight', 
    'Rice_Brown_spot', 'Rice_Leaf_smut', 'Tomato_Bacterial_spot', 
    'Tomato_Early_blight', 'Tomato_Late_blight', 'Tomato_Leaf_Mold', 
    'Tomato_Septoria_leaf_spot', 'Tomato_Spider_mites_Two_spotted_spider_mite', 
    'Tomato__Target_Spot', 'Tomato__Tomato_YellowLeaf__Curl_Virus', 
    'Tomato__Tomato_mosaic_virus', 'Tomato_healthy'
]

# KNOWLEDGE BASE: Added "Simple Language" support
disease_info = {
    '00_Unknown': {
        'desc': 'The AI could not recognize this as a valid plant leaf.',
        'sol': 'Please upload a clear, focused photo.',
        'simple_desc': 'AI is photo ko theek se pehchan nahi paya.',
        'simple_sol': 'Kripaya patti (leaf) ki ek saaf aur clear photo kheenchiye.'
    },
    'Potato___Late_blight': {
        'desc': 'A fast-moving disease that creates large, dark, greasy-looking leaf spots.',
        'sol': 'Use fungicides immediately and remove infected plant debris.',
        'simple_desc': 'Pattiyon par kaale aur geele dhabbe padne lagte hain. Ye tezi se failta hai.',
        'simple_sol': 'Kharab paudhon ko turant ukhad kar jala dein aur khet mein paani na bharne dein.'
    },
    'Tomato__Tomato_YellowLeaf__Curl_Virus': {
        'desc': 'Leaves curl upward and turn yellow. Spread by whiteflies.',
        'sol': 'Control whiteflies with sticky traps and remove infected plants.',
        'simple_desc': 'Pattiyan upar ki taraf mudne lagti hain (sikud jati hain) aur peeli pad jati hain.',
        'simple_sol': 'Ye safed makkhi se phelta hai. Khet mein peele sticky trap (chipchipe board) lagayein.'
    },
    'Rice_Bacterial_leaf_blight': {
        'desc': 'Bacterial disease causing water-soaked to yellowish stripes on leaf blades.',
        'sol': 'Use resistant varieties, avoid excess nitrogen fertilizer.',
        'simple_desc': 'Chawal ki pattiyon par peeli lambi dhariyan (stripes) ban jati hain.',
        'simple_sol': 'Khet mein Urea (Nitrogen) ka istemal kam karein aur saaf paani ka prabandh karein.'
    },
    # Default fallback for healthy plants
    'Tomato_healthy': {
        'desc': 'The tomato plant is in excellent condition!',
        'sol': 'Keep providing 6-8 hours of sunlight and consistent water.',
        'simple_desc': 'Aapka paudha ekdum swasth (healthy) aur hara-bhara hai.',
        'simple_sol': 'Samay par paani dete rahein, kisi dawai ki zaroorat nahi hai.'
    }
}

history = []

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return render_template("index.html", prediction="No file uploaded")

    file = request.files['file']
    
    img = Image.open(io.BytesIO(file.read())).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    index = int(np.argmax(prediction))
    confidence = round(float(np.max(prediction)) * 100, 2)

    THRESHOLD = 70.0 

    if class_names[index] == '00_Unknown':
        result = "Invalid/Unknown Image"
        info = disease_info['00_Unknown']
        
    elif confidence >= THRESHOLD:
        if 0 <= index < len(class_names):
            raw_name = class_names[index]
            result = raw_name.replace('_', ' ').replace('  ', ' ').strip()
            
            # Default info agar specific class database mein na ho
            info = disease_info.get(raw_name, {
                'desc': "Infection detected on the leaf surface.",
                'sol': "Apply standard broad-spectrum fungicide.",
                'simple_desc': "Patti par bimari ke lakshan dikh rahe hain.",
                'simple_sol': "Najdiki beej bhandar ya krishi kendra se salah lein."
            })
        else:
            result = "Error"
            info = {'desc': "Error", 'sol': "Error", 'simple_desc': "Error", 'simple_sol': "Error"}
    else:
        result = "Unrecognized Image"
        info = {
            'desc': f"The AI is only {confidence}% sure. Not confident enough.",
            'sol': "Please upload a clearer leaf photo.",
            'simple_desc': f"AI is photo ko lekar sirf {confidence}% sure hai.",
            'simple_sol': "Behtar result ke liye patti ki aur saaf photo dalein."
        }

    history.append(result)
    if len(history) > 5:
        history.pop(0)

    return render_template("index.html",
                           prediction=result,
                           confidence=confidence,
                           description=info['desc'],
                           solution=info['sol'],
                           simple_desc=info['simple_desc'],
                           simple_sol=info['simple_sol'],
                           history=history)

if __name__ == "__main__":
    app.run(debug=True)