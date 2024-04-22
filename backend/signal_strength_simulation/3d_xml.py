import xml.etree.ElementTree as ET

# Crear el elemento raíz
root = ET.Element('scene', {'version': '2.0.0'})

# Agregar la cámara
camera = ET.SubElement(root, 'sensor', {'type': 'perspective'})
ET.SubElement(camera, 'float', {'name': 'fov', 'value': '45'})
ET.SubElement(camera, 'transform', {'name': 'to_world'}).text = '0 1 5 1 0 0 0 0 1 0 0 0'

# Agregar la iluminación
emitter = ET.SubElement(root, 'emitter', {'type': 'constant'})
ET.SubElement(emitter, 'spectrum', {'name': 'intensity', 'value': '1.0'})

# Agregar el piso
floor = ET.SubElement(root, 'shape', {'type': 'rectangle'})
ET.SubElement(floor, 'transform', {'name': 'to_world'}).text = '0 0 1 4 0 0 0 4 0 -2 -2 0'
bsdf = ET.SubElement(floor, 'bsdf', {'type': 'diffuse'})
ET.SubElement(bsdf, 'rgb', {'name': 'reflectance', 'value': '0.8 0.8 0.8'})

# Agregar las paredes
walls = [
    ('0 0 0 1 0 0 0 0 2 -2 -2 0', '0.7 0.7 0.7'),  # Pared 1
    ('0 0 0 0 1 0 0 0 2 2 -2 0', '0.7 0.7 0.7'),   # Pared 2
    ('0 0 1 4 0 0 0 0 2 -2 2 0', '0.7 0.7 0.7'),   # Pared 3
    ('0 0 1 0 4 0 0 0 2 2 -2 0', '0.7 0.7 0.7'),   # Pared 4
    ('0 0 1 2 0 0 0 0 2 0 0 0', '0.6 0.6 0.6'),    # Pared 5
    ('0 0 1 0 2 0 0 0 2 0 0 0', '0.6 0.6 0.6'),    # Pared 6
    ('0 0 1 1 0 0 0 0 2 1 1 0', '0.6 0.6 0.6'),    # Pared 7
    ('0 0 1 0 1 0 0 0 2 -1 1 0', '0.6 0.6 0.6')    # Pared 8
]

for wall_transform, wall_color in walls:
    wall = ET.SubElement(root, 'shape', {'type': 'rectangle'})
    ET.SubElement(wall, 'transform', {'name': 'to_world'}).text = wall_transform
    bsdf = ET.SubElement(wall, 'bsdf', {'type': 'diffuse'})
    ET.SubElement(bsdf, 'rgb', {'name': 'reflectance', 'value': wall_color})

# Generar el archivo XML
tree = ET.ElementTree(root)
tree.write('floorplan.xml', encoding='utf-8', xml_declaration=True)