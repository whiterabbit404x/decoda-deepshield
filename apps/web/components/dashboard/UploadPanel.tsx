"use client";

import { type ChangeEvent, useMemo, useRef, useState } from "react";

import { analyzeDetections, uploadEvidence } from "@/lib/api";
import { type DetectionOutput, type EvidenceUploadResponse } from "@/types/api";

interface UploadPanelProps {
  onDetections: (detections: DetectionOutput[]) => void;
}

const MAX_SIZE = 50 * 1024 * 1024;
const ALLOWED = ["application/json", "text/csv", "application/vnd.tcpdump.pcap"];

export function UploadPanel({ onDetections }: UploadPanelProps) {
  const [textToAnalyze, setTextToAnalyze] = useState("");
  const [uploadStatus, setUploadStatus] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const statusTone = useMemo(() => uploadStatus.includes("failed") || uploadStatus.includes("Invalid") ? "state-error" : "", [uploadStatus]);

  const validateFile = (file: File) => {
    if (!ALLOWED.includes(file.type)) return "Invalid file type. Use JSON, CSV, or PCAP.";
    if (file.size > MAX_SIZE) return "File too large. Max 50 MB.";
    return null;
  };

  const uploadFile = async (file: File) => {
    const validation = validateFile(file);
    if (validation) {
      setUploadStatus(validation);
      return;
    }
    setIsUploading(true);
    setProgress(20);
    setUploadStatus("Uploading evidence…");
    try {
      const text = await file.text();
      setProgress(65);
      const result: EvidenceUploadResponse = await uploadEvidence(file.name, { content: text });
      setProgress(100);
      setUploadStatus(result.message ?? `Upload ${result.status}`);
    } catch (error) {
      setUploadStatus(error instanceof Error ? error.message : "Upload failed");
      setProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  const onFileChosen = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) await uploadFile(file);
  };

  return (
    <article className="card upload-panel">
      <h2>Evidence Upload</h2>
      <p className="muted">Drop IOC files or forensic bundles for automated triage.</p>
      <div
        className={`drop-zone ${isDragging ? "drag-active" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          const file = e.dataTransfer.files?.[0];
          if (file) void uploadFile(file);
        }}
        tabIndex={0}
        aria-label="Drag and drop files to upload"
      >
        <p>Drag & drop evidence files here</p>
        <p className="muted">JSON, CSV, PCAP up to 50 MB</p>
      </div>
      <input ref={inputRef} type="file" hidden onChange={onFileChosen} aria-label="Choose evidence files" />
      <button className="upload-btn" onClick={() => inputRef.current?.click()} aria-label="Choose files for upload">Choose Files</button>
      {isUploading ? <div className="progress" aria-label="Upload progress"><span style={{ width: `${progress}%` }} /></div> : null}
      {uploadStatus ? <p className={`state-text ${statusTone}`}>{uploadStatus}</p> : null}

      <textarea className="analyze-input" placeholder="Paste IOC evidence, logs, or suspicious activity summary…" value={textToAnalyze} onChange={(event) => setTextToAnalyze(event.target.value)} />
      <button className="upload-btn secondary" onClick={async () => {
        setIsAnalyzing(true);
        onDetections([{ label: "Pending model analysis…" }]);
        try { const result = await analyzeDetections(textToAnalyze); onDetections(result.detections); }
        finally { setIsAnalyzing(false); }
      }} disabled={isAnalyzing || !textToAnalyze.trim()}>{isAnalyzing ? "Analyzing…" : "Analyze Detections"}</button>
    </article>
  );
}
