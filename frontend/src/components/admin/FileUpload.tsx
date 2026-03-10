import { useRef, useState } from 'react';
import { ingestFile } from '../../services/api';

interface Props {
  apiKey: string;
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

export function FileUpload({ apiKey, onSuccess, onError }: Props) {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !['pdf', 'docx'].includes(ext)) {
      onError('Only PDF and DOCX files are supported.');
      return;
    }

    setFileName(file.name);
    setUploading(true);
    try {
      const res = await ingestFile(apiKey, file);
      onSuccess(res.message);
      setFileName(null);
    } catch (err) {
      onError(err instanceof Error ? err.message : 'Upload failed');
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = '';
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  return (
    <div className="space-y-3">
      <div
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => !uploading && inputRef.current?.click()}
        className={`relative flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 cursor-pointer transition ${
          isDragging
            ? 'border-brand-500 bg-brand-50'
            : 'border-slate-300 hover:border-slate-400 bg-white'
        } ${uploading ? 'pointer-events-none opacity-70' : ''}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
        />

        {uploading ? (
          <>
            <svg className="w-7 h-7 text-brand-500 animate-spin mb-2" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            <p className="text-sm font-medium text-slate-700">Ingesting <span className="text-brand-600">{fileName}</span>…</p>
            <p className="text-xs text-slate-400 mt-1">This may take a moment</p>
          </>
        ) : (
          <>
            <svg className="w-7 h-7 text-slate-400 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
            </svg>
            <p className="text-sm font-medium text-slate-700">Drop a file or click to upload</p>
            <p className="text-xs text-slate-400 mt-1">PDF, DOCX supported</p>
          </>
        )}
      </div>
    </div>
  );
}
