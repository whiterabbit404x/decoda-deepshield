"use client";

import { type ChangeEvent, useMemo, useRef, useState } from "react";

import { analyzeDetections, uploadEvidence } from "@/lib/api";
import { type DetectionOutput } from "@/types/api";

interface UploadPanelProps {
  onDetections: (detections: DetectionOutput[]) => void;
  onRefreshDashboardData: () => Promise<void>;
}

const MAX_SIZE = 50 * 1024 * 1024;
const ALLOWED_EXTENSIONS = [".json", ".csv", ".pcap", ".pcapng", ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"];

export function UploadPanel({ onDetections, onRefreshDashboardData }: UploadPanelProps) {
  const [uploadStatus, setUploadStatus] = useState("");
  const [analysisStatus, setAnalysisStatus] = useState("");
  const [evidenceId, setEvidenceId] = useState<string | null>(null);
  const [apiError, setApiError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [progress, setProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [sha256Hash, setSha256Hash] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const statusTone = useMemo(() => (apiError ? "state-error" : ""), [apiError]);

  const validateFile = (file: File) => {
    const lowerName = file.name.toLowerCase();
    const extensionAllowed = ALLOWED_EXTENSIONS.some((ext) => lowerName.endsWith(ext));
    const mimeAllowed = file.type.startsWith("audio/") || file.type.startsWith("video/") || file.type === "application/json" || file.type === "text/csv" || file.type === "application/vnd.tcpdump.pcap";
    if (!extensionAllowed && !mimeAllowed) return "Invalid file type. Use supported audio/video, JSON, CSV, or PCAP files.";
    if (file.size > MAX_SIZE) return "File too large. Max 50 MB.";
    return null;
  };

  const uploadFile = async (file: File) => {
    const validation = validateFile(file);
    if (validation) {
      setApiError(validation);
      return;
    }
    setApiError(null);
    setAnalysisStatus("");
    setIsUploading(true);
    setProgress(20);
    setUploadStatus("Uploading evidence…");
    setEvidenceId(null);
    setSha256Hash(null);

    try {
      const result = await uploadEvidence(file);
      setProgress(100);
      setEvidenceId(result.evidence_id);
      setSha256Hash(result.sha256_hash);
      setUploadStatus("Upload successful");
      await onRefreshDashboardData();
    } catch (error) {
      setUploadStatus("");
      setApiError(error instanceof Error ? `API error: ${error.message}` : "API error: Upload failed");
      setProgress(0);
    } finally {
      setIsUploading(false);
    }
  };

  const onFileChosen = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) await uploadFile(file);
  };

  const runAnalysis = async () => {
    if (!evidenceId) return;
    setIsAnalyzing(true);
    setApiError(null);
    setAnalysisStatus("Analyzing evidence…");

    try {
      const result = await analyzeDetections(evidenceId);
      onDetections([result]);
      setAnalysisStatus("Detection completed");
      await onRefreshDashboardData();
    } catch (error) {
      setAnalysisStatus("");
      setApiError(error instanceof Error ? `API error: ${error.message}` : "API error: Analysis failed");
    } finally {
      setIsAnalyzing(false);
    }
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
        <p className="muted">Audio/video (e.g. MP3, WAV, M4A, MP4, MOV, MKV, WEBM), JSON, CSV, PCAP up to 50 MB</p>
      </div>
      <input ref={inputRef} type="file" accept="audio/*,video/*,.json,.csv,.pcap,.pcapng,.mp3,.wav,.m4a,.aac,.flac,.ogg,.opus,.mp4,.mov,.mkv,.webm,.avi,.m4v,application/json,text/csv,application/vnd.tcpdump.pcap" hidden onChange={onFileChosen} aria-label="Choose evidence files" />
      <button className="upload-btn" onClick={() => inputRef.current?.click()} aria-label="Choose files for upload">Choose Files</button>
      {isUploading ? <div className="progress" aria-label="Upload progress"><span style={{ width: `${progress}%` }} /></div> : null}
      {uploadStatus ? <p className="state-text">{uploadStatus}</p> : null}
      {evidenceId ? <p className="state-text">Evidence ID: <code>{evidenceId}</code></p> : null}
      {sha256Hash ? <p className="state-text">SHA-256: <code>{sha256Hash}</code></p> : null}
      {analysisStatus ? <p className="state-text">{analysisStatus}</p> : null}
      {apiError ? <p className={`state-text ${statusTone}`}>{apiError}</p> : null}

      <button className="upload-btn secondary" onClick={runAnalysis} disabled={isAnalyzing || !evidenceId}>
        {isAnalyzing ? "Analyzing…" : "Analyze evidence"}
      </button>
    </article>
  );
}
