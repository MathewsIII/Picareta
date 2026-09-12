import os
import zipfile
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter

# Configurações do layout
WIDTH, HEIGHT = 600, 600
CORNER_RADIUS = 30
BORDER_THICKNESS = 8
LINE_THICKNESS = 4
FONT_SIZE = 180

# Diretório temporário
output_dir = "etiquetas_img"
os.makedirs(output_dir, exist_ok=True)

# Tentar carregar fonte Serif estilo a da imagem (Times New Roman ou Georgia)
try:
    font = ImageFont.truetype("times.ttf", FONT_SIZE)
except OSError:
    try:
        font = ImageFont.truetype("georgia.ttf", FONT_SIZE)
    except OSError:
        font = ImageFont.load_default()

# Formato do código de barras (Code 128)
Code128 = barcode.get_barcode_class('code128')

for i in range(11, 201):
    num_str = f"{i:03d}"  # Garante 3 dígitos (ex: 011, 012, ..., 200)
    
    # Create base canvas
    img = Image.new("RGB", (WIDTH, HEIGHT), "white")
    draw = ImageDraw.Draw(img)
    
    # 1. Borda externa arredondada
    margin = 40
    rect = [margin, margin, WIDTH - margin, HEIGHT - margin]
    draw.rounded_rectangle(rect, radius=CORNER_RADIUS, outline="black", width=BORDER_THICKNESS)
    
    # 2. Desenhar o Texto (Número)
    # Obter bounding box do texto para centralizar
    bbox = font.getbbox(num_str)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = (WIDTH - text_width) // 2
    text_y = margin + 30
    draw.text((text_x, text_y), num_str, fill="black", font=font)
    
    # 3. Linha divisória horizontal
    line_y = text_y + text_height + 40
    line_margin = margin + 20
    draw.line([(line_margin, line_y), (WIDTH - line_margin, line_y)], fill="black", width=LINE_THICKNESS)
    
    # 4. Gerar Código de Barras
    rv = Code128(num_str, writer=ImageWriter())
    # Remove o texto padrão do código de barras
    options = {
        'write_text': False,
        'module_height': 15.0,
        'quiet_zone': 2.0
    }
    barcode_img = rv.render(writer_options=options).convert("RGB")
    
    # Redimensionar código de barras para se ajustar ao espaço inferior
    bc_w = WIDTH - (line_margin * 2)
    bc_h = (HEIGHT - line_y - margin) - 40
    barcode_resized = barcode_img.resize((bc_w, bc_h), Image.Resampling.LANCZOS)
    
    # Colar o código de barras na etiqueta
    img.paste(barcode_resized, (line_margin, line_y + 20))
    
    # Salvar imagem individual
    img.save(f"{output_dir}/etiqueta_{num_str}.png")

# 5. Compactar todas as imagens em um arquivo ZIP
zip_filename = "etiquetas_11_200.zip"
with zipfile.ZipFile(zip_filename, 'w') as zipf:
    for root, _, files in os.walk(output_dir):
        for file in files:
            zipf.write(os.path.join(root, file), file)

print(f"Sucesso! {len(range(11, 201))} etiquetas foram geradas e salvas em '{zip_filename}'.")
