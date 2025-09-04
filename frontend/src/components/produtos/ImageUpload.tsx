import React, { useRef, useState } from 'react';
import { Upload, X, Image as ImageIcon } from 'lucide-react';
import { Button } from '../ui/button';

interface ImageUploadProps {
  value?: File | null;
  onChange: (file: File | null) => void;
  preview?: string;
  label?: string;
}

const ImageUpload: React.FC<ImageUploadProps> = ({
  value,
  onChange,
  preview,
  label = 'Imagem do Produto'
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(preview || null);

  const handleFileSelect = (file: File) => {
    if (file && file.type.startsWith('image/')) {
      onChange(file);
      
      // Criar preview
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files[0]) {
      handleFileSelect(files[0]);
    }
  };

  const handleRemove = () => {
    onChange(null);
    setPreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-foreground">
        {label}
      </label>
      
      <div className="space-y-4">
        {/* Preview da imagem */}
        {(previewUrl || preview) && (
          <div className="relative inline-block">
            <img
              src={previewUrl || preview}
              alt="Preview"
              className="w-32 h-32 object-cover rounded-lg border"
            />
            <Button
              type="button"
              variant="destructive"
              size="sm"
              className="absolute -top-2 -right-2 h-6 w-6 rounded-full p-0"
              onClick={handleRemove}
            >
              <X className="h-3 w-3" />
            </Button>
          </div>
        )}
        
        {/* Área de upload */}
        <div
          className={`
            border-2 border-dashed rounded-lg p-6 text-center transition-colors cursor-pointer
            ${dragActive 
              ? 'border-primary bg-primary/5' 
              : 'border-muted-foreground/25 hover:border-primary/50'
            }
          `}
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onClick={openFileDialog}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileInputChange}
            className="hidden"
          />
          
          <div className="space-y-2">
            {previewUrl || preview ? (
              <ImageIcon className="mx-auto h-8 w-8 text-muted-foreground" />
            ) : (
              <Upload className="mx-auto h-8 w-8 text-muted-foreground" />
            )}
            
            <div>
              <p className="text-sm text-foreground">
                {previewUrl || preview ? 'Clique para alterar a imagem' : 'Clique para selecionar ou arraste uma imagem'}
              </p>
              <p className="text-xs text-muted-foreground">
                PNG, JPG, WEBP até 5MB
              </p>
            </div>
          </div>
        </div>
        
        {/* Informações do arquivo selecionado */}
        {value && (
          <div className="text-xs text-muted-foreground">
            <p>Arquivo: {value.name}</p>
            <p>Tamanho: {(value.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ImageUpload;