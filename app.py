from flask import Flask , render_template, request, send_file 
from PIL import Image
import os

app = Flask(__name__)

def hide_message(image_path, secret_text):
    img = Image.open(image_path)
    pixels = img.load()
    width, height = img.size

    bits = ''.join(format(ord(i),'08b')for i in secret_text)
    bits += '1111111111111110'

    bit_idx = 0
    for y in range(height):
        for x in range(width):
            if bit_idx < len(bits):

                pixel_data = list(pixels[x,y])
                r = pixel_data[0]

                if bits[bit_idx] == '1':
                    if r % 2 == 0: r += 1
                else:
                    if r % 2 != 0: r -= 1

                pixel_data[0] = r
                pixels[x,y] = tuple(pixel_data) 
                bit_idx += 1

        output_path = "secret_output.png"
        img.save(output_path)
        return output_path
    
def reveal_message(image_path):
        img = Image.open(image_path)
        pixels = img.load()
        width, height = img.size
    
        extracted_bits = ""
        for y in range(height):
            for x in range(width):
                r = pixels[x, y][0] # Grab just the Red value
                extracted_bits += "1" if r % 2 != 0 else "0"
            
            # Check for our "Stop Sign"
                if extracted_bits.endswith('1111111111111110'):
                    clean_bits = extracted_bits[:-16]
                # Convert bits back to letters
                    chars = [chr(int(clean_bits[i:i+8], 2)) for i in range(0, len(clean_bits), 8)]
                    return "".join(chars)
        return "No secret message found."
   
@app.route('/')
def home():
     return render_template('index.html')
    
@app.route('/encode' , methods=['POST'])
def encode():

        file = request.files['image']
        message = request.form['message']

        file.save("temp_input.png")
        result_file = hide_message("temp_input.png",message)

        return send_file(result_file , as_attachment=True)
    
@app.route('/decode', methods=['POST'])
def decode():
        file = request.files['image']
        file.save("to_decode.png")

        message = reveal_message("to_decode.png")

        return f"<h1>Found Message: {message}</h1><br><a href='/'>Go Back</a>"
    
if __name__ == '__main__':
        print("--- SERVER STARTING ---") # This helps us see if it's working!
        app.run(debug=True, port=5000)