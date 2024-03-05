import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

const FileUpload = ({ onFileUploaded }) => {
  const onDrop = useCallback(acceptedFiles => {
    // Suponiendo que la subida se maneja aquí
    const file = acceptedFiles[0];
    console.log(file); // Hacer algo con el archivo, e.g., subirlo a un servidor
    onFileUploaded(file);
  }, [onFileUploaded]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div {...getRootProps()} className="border-dashed border-4 border-gray-300 p-10 text-center cursor-pointer">
      <input {...getInputProps()} />
      {
        isDragActive ?
          <p>Suelta el archivo aquí...</p> :
          <p>Arrastra y suelta un archivo aquí, o haz clic para seleccionar archivo</p>
      }
    </div>
  );
};

export default FileUpload;
