import os
import base64
import numpy as np
import streamlit as st
from PIL import Image
from openai import OpenAI
from streamlit_drawable_canvas import st_canvas

# Configuración de la página y nuevo título
st.set_page_config(page_title='Cuentos Mágicos', page_icon='🎨')
st.title('🎨 Cuentos Mágicos: Dibuja tu Historia')

with st.sidebar:
    st.subheader("Acerca de:")
    st.write("Dibuja un boceto en el lienzo y la Inteligencia Artificial creará un cuento infantil mágico basado en tu obra de arte.")
    # Pedir la API key en el sidebar como contraseña
    ke = st.text_input('Ingresa tu Clave de OpenAI', type='password')

st.subheader("Dibuja tu personaje o escena y presiona el botón para crear el cuento")

# Parámetros del lienzo (canvas)
drawing_mode = "freedraw"
stroke_width = st.sidebar.slider('Selecciona el ancho de línea', 1, 30, 5)
stroke_color = "#000000" 
bg_color = '#FFFFFF'

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
            return encoded_image
    except FileNotFoundError:
        return "Error: La imagen no se encontró."

# Crear componente canvas
canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=300,
    width=400,
    drawing_mode=drawing_mode,
    key="canvas",
)

analyze_button = st.button("Crear cuento infantil ✨", type="primary")

# Lógica de ejecución cuando se presiona el botón
if analyze_button:
    if not ke:
        st.warning("⚠️ Por favor ingresa tu API key de OpenAI en el menú lateral.")
    elif canvas_result.image_data is not None:
        with st.spinner("Escribiendo una historia mágica... 🪄"):
            
            # Guardar la imagen del canvas
            input_numpy_array = np.array(canvas_result.image_data)
            input_image = Image.fromarray(input_numpy_array.astype('uint8'), 'RGBA')
            input_image.save('img.png')
            
            # Codificar la imagen en base64
            base64_image = encode_image_to_base64("img.png")
            
            # ---------------------------------------------------------
            # NUEVO PROMPT: Crear una historia para niños (Línea ~86)
            # ---------------------------------------------------------
            prompt_text = (
                "Eres un cuentacuentos infantil. A partir de la imagen adjunta (que es un dibujo o boceto hecho a mano), "
                "crea una historia corta, mágica y divertida para niños. Ponle un título creativo al cuento y usa algunos emojis."
            )
            
            try:
                # Inicializar el cliente de OpenAI con la key ingresada
                client = OpenAI(api_key=ke)
                
                # Hacer la petición a la API
                response = client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}",
                                    },
                                },
                            ],
                        }
                    ],
                    max_tokens=600,
                )
                
                # Mostrar el cuento generado en la aplicación
                historia = response.choices[0].message.content
                st.success("¡Tu cuento está listo!")
                st.write(historia)
                
            except Exception as e:
                st.error(f"Ocurrió un error con la API: {e}")
    else:
        st.warning("⚠️ Por favor, dibuja algo en el lienzo primero.")
