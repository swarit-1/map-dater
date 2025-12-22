import { useRef, useState } from 'react';

interface MapUploadPanelProps {
  onFileSelect: (file: File) => void;
  isAnalyzing?: boolean;
}

export function MapUploadPanel({ onFileSelect, isAnalyzing = false }: MapUploadPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
      onFileSelect(file);
    } else {
      alert('Please upload an image file');
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8
          transition-all duration-200
          ${dragActive ? 'border-sepia-500 bg-parchment-200' : 'border-sepia-400 bg-parchment-50'}
          ${isAnalyzing ? 'opacity-50 pointer-events-none' : 'hover:border-sepia-500 cursor-pointer'}
        `}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={handleButtonClick}
      >
        <input
          ref={fileInputRef}
          type="file"
          className="hidden"
          accept="image/*"
          onChange={handleChange}
          disabled={isAnalyzing}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          {preview ? (
            <div className="w-full">
              <img
                src={preview}
                alt="Map preview"
                className="max-h-64 mx-auto rounded border-2 border-sepia-300 shadow-paper"
              />
              <p className="text-center mt-4 text-sm text-sepia-700">
                {isAnalyzing ? 'Analyzing map...' : 'Click to upload a different map'}
              </p>
            </div>
          ) : (
            <>
              <svg
                className="w-16 h-16 text-sepia-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <div className="text-center">
                <p className="text-lg font-serif text-ink">
                  Drop your map here, or click to browse
                </p>
                <p className="text-sm text-sepia-600 mt-2">
                  Accepts JPG, PNG, or other image formats
                </p>
              </div>
            </>
          )}

          {isAnalyzing && (
            <div className="absolute inset-0 flex items-center justify-center bg-parchment-100 bg-opacity-90 rounded-lg">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-sepia-200 border-t-sepia-600 mx-auto mb-4"></div>
                <p className="font-serif text-ink text-lg">Analyzing historical clues...</p>
                <p className="text-sm text-sepia-600 mt-2">
                  Examining entities, dates, and cartographic features
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
