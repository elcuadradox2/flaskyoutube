import os
from flask import Flask, request, render_template_string, send_file
from yt_dlp import YoutubeDL

app = Flask(__name__)

# Plantilla HTML para seleccionar la calidad
QUALITY_SELECTION_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Seleccione la Calidad</title>
</head>
<body>
    <h1>Seleccione la calidad del video</h1>
    <form action="/download" method="post">
        <input type="hidden" name="url" value="{{ url }}">
        <label for="quality">Calidad:</label>
        <select name="quality" id="quality">
            {% for option in options %}
                <option value="{{ option['format_id'] }}">{{ option['format_note'] }} ({{ option['filesize_approx'] | default('Desconocido') }} MB)</option>
            {% endfor %}
        </select>
        <button type="submit">Descargar</button>
    </form>
</body>
</html>
'''

# Plantilla HTML inicial
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Descargador de YouTube</title>
</head>
<body>
    <h1>Descargador de YouTube</h1>
    <form action="/select-quality" method="post">
        <label for="url">Ingrese la URL del video:</label>
        <input type="text" id="url" name="url" required>
        <button type="submit">Obtener Calidades</button>
    </form>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)

@app.route('/select-quality', methods=['POST'])
def select_quality():
    url = request.form['url']
    try:
        # Obtener las opciones de calidad
        ydl_opts = {'noplaylist': True}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])

            # Filtrar las opciones combinadas de video+audio y en formato mp4
            video_options = [
                {
                    'format_id': f['format_id'],
                    'format_note': f.get('format_note', 'Desconocida'),
                    'filesize_approx': f.get('filesize_approx', None) // (1024 * 1024) if f.get('filesize_approx') else None
                }
                for f in formats if f.get('acodec') != 'none' and f.get('vcodec') != 'none' and 'mp4' in f['ext']
            ]

        return render_template_string(QUALITY_SELECTION_TEMPLATE, options=video_options, url=url)
    except Exception as e:
        return f"<h1>Error al obtener las opciones de calidad: {e}</h1>"

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    quality = request.form['quality']
    output_dir = './downloads'
    os.makedirs(output_dir, exist_ok=True)

    try:
        # Descargar el video en la calidad seleccionada (solo combinados)
        ydl_opts = {
            'format': quality,
            'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s')
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return f"<h1>Error al descargar el video: {e}</h1>"

if __name__ == '__main__':
    app.run(debug=True)
