import xml.etree.ElementTree as ET
import numpy as np
import mitsuba as mi

# Especificar la variante de Mitsuba antes de importar los paquetes
mi.set_variant('scalar_rgb')

# Crear el elemento raíz
root = ET.Element('scene', {'version': '0.6.0'})

# Agregar la cámara
camera = ET.SubElement(root, 'sensor', {'type': 'perspective'})
ET.SubElement(camera, 'float', {'name': 'fov', 'value': '45'})
ET.SubElement(camera, 'transform', {'name': 'to_world'})
ET.SubElement(camera.find('transform'), 'lookat', {
    'origin': '0, 1, 5',
    'target': '0, 0, 0',
    'up': '0, 1, 0'
})

# Agregar la iluminación
emitter = ET.SubElement(root, 'emitter', {'type': 'constant'})
ET.SubElement(emitter, 'spectrum', {'name': 'radiance', 'value': '1.0'})

# Agregar el piso
floor = ET.SubElement(root, 'shape', {'type': 'rectangle'})
ET.SubElement(floor, 'transform', {'name': 'to_world'})
ET.SubElement(floor.find('transform'), 'scale', {'value': '4, 1, 4'})
ET.SubElement(floor.find('transform'), 'translate', {'value': '-2, -2, 0'})
bsdf = ET.SubElement(floor, 'bsdf', {'type': 'diffuse'})
ET.SubElement(bsdf, 'rgb', {'name': 'reflectance', 'value': '0.8, 0.8, 0.8'})

# Agregar las paredes
walls = [
    ('1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -2, -2, 0, 1', '0.7, 0.7, 0.7'),  # Pared 1
    ('1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 2, -2, 0, 1', '0.7, 0.7, 0.7'),   # Pared 2
    ('1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -2, 2, 0, 1', '0.7, 0.7, 0.7'),   # Pared 3
    ('1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 2, -2, 0, 1', '0.7, 0.7, 0.7'),   # Pared 4
    ('1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1', '0.6, 0.6, 0.6'),    # Pared 5
    ('1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1', '0.6, 0.6, 0.6'),    # Pared 6
    ('1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0, 1', '0.6, 0.6, 0.6'),    # Pared 7
    ('1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, -1, 1, 0, 1', '0.6, 0.6, 0.6')    # Pared 8
]

for wall_transform, wall_color in walls:
    wall = ET.SubElement(root, 'shape', {'type': 'rectangle'})
    ET.SubElement(wall, 'transform', {'name': 'to_world'})
    ET.SubElement(wall.find('transform'), 'matrix', {'value': wall_transform})
    bsdf = ET.SubElement(wall, 'bsdf', {'type': 'diffuse'})
    ET.SubElement(bsdf, 'rgb', {'name': 'reflectance', 'value': wall_color})

# Agregar los parámetros de renderizado al archivo XML
integrator = ET.SubElement(root, 'integrator', {'type': 'path'})
ET.SubElement(integrator, 'integer', {'name': 'max_depth', 'value': '8'})

# Generar el archivo XML
tree = ET.ElementTree(root)
tree.write('floorplan.xml', encoding='utf-8', xml_declaration=True)

print("Archivo 'floorplan.xml' generado exitosamente.")

# Cargar la escena desde el archivo XML
scene = mi.load_file('floorplan.xml')

# Configurar los parámetros de renderizado
params = mi.SceneParameters()
params['sensor.perspective.fov'] = 45
params['sampler.type'] = 'independent'
params['sampler.sample_count'] = 256

# Renderizar la escena
img = mi.render(scene, spp=256)

# Guardar la imagen renderizada
mi.util.write_bitmap('floorplan.png', img)
print("Imagen 'floorplan.png' renderizada y guardada exitosamente.")