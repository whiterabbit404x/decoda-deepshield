"use client";

import { useState } from "react";

import { analyzeDetections, uploadEvidence } from "@/lib/api";
import { type DetectionOutput, type EvidenceUploadResponse } from "@/types/api";

interface UploadPanelProps {
  onDetections: (detections: DetectionOutput[]) => void;
}

export function UploadPanel({ onDetections }: UploadPanelProps) {
  const [textToAnalyze, setTextToAnalyze] = useState("");
  const [uploadStatus, setUploadStatus] = useState<string>("");
  const [analyzeStatus, setAnalyzeStatus] = useState<string>("");
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleUpload = async () => {
    setIsUploading(true);
    setUploadStatus("Uploading evidence…");

    try {
      const result: EvidenceUploadResponse = await uploadEvidence("manual-entry.json", {
        content: textToAnalyze
      });
      setUploadStatus(result.message ?? `Upload ${result.status}`);
    } catch (error) {
      setUploadStatus(error instanceof Error ? error.message : "Upload failed");
    } finally {
      setIsUploading(false);
    }
  };

  const handleAnalyze = async () => {
    setIsAnalyzing(true);
    setAnalyzeStatus("Analyzing evidence…");
    onDetections([{ label: "Pending model analysis…" }]);

    try {
      const result = await analyzeDetections(textToAnalyze);
      onDetections(result.detections);
      setAnalyzeStatus(result.summary ?? `Analysis complete (${result.detections.length} detections)`);
    } catch (error) {
      onDetections([]);
      setAnalyzeStatus(error instanceof Error ? error.message : "Analysis failed");
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <article className="card upload-panel">
      <h2>Upload Intelligence</h2>
      <p className="muted">Drop IOC files or forensic bundles for automated triage.</p>
      <textarea
        className="analyze-input"
        placeholder="Paste IOC evidence, logs, or suspicious activity summary…"
        value={textToAnalyze}
        onChange={(event) => setTextToAnalyze(event.target.value)}
      />
      <button className="upload-btn" onClick={handleUpload} disabled={isUploading || !textToAnalyze.trim()}>
        {isUploading ? "Uploading…" : "Upload Evidence"}
      </button>
      <button className="upload-btn secondary" onClick={handleAnalyze} disabled={isAnalyzing || !textToAnalyze.trim()}>
        {isAnalyzing ? "Analyzing…" : "Analyze Detections"}
      </button>
      {uploadStatus ? <p className="state-text">{uploadStatus}</p> : null}
      {analyzeStatus ? <p className="state-text">{analyzeStatus}</p> : null}
      <div className="upload-meta">
        <p>Supported: CSV, JSON, PCAP</p>
        <p>Max size: 4 GB</p>
      </div>
    </article>
  );
}
