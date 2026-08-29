import type { ReactNode } from "react";
import { PageHeader } from "../components/layout/Layout";

export function About() {
  return (
    <div className="page">
      <PageHeader title="About this project" />

      <Section title="Problem">
        <p>
          During disasters (floods, earthquakes, landslides, cyclones, etc.), people share large amounts of
          information online. Some of it is genuine; some is outdated, exaggerated, or entirely false. False
          information can cause panic, misdirect rescue teams, waste relief resources, and delay genuine response.
        </p>
      </Section>

      <Section title="Objectives">
        <ul>
          <li>Determine whether a piece of text is disaster-related, and if so, which disaster type</li>
          <li>Extract and resolve the hyperlocal location mentioned (locality/city/district/state)</li>
          <li>Classify the claim as TRUE, FAKE, or UNVERIFIED — never forcing a binary call under low confidence</li>
          <li>Separate the ML verdict from independently-sourced evidence, never conflating the two</li>
          <li>Produce a transparent, explainable reliability score and a relief-priority level</li>
          <li>Present all of this through a dashboard usable by a relief organization</li>
        </ul>
      </Section>

      <Section title="Technology">
        <ul>
          <li><strong>Backend:</strong> FastAPI + SQLAlchemy + SQLite</li>
          <li><strong>ML/NLP:</strong> scikit-learn (TF-IDF + Logistic Regression, compared against Random Forest and linear SVM), rule-based disaster-type and location extraction, a real India Post gazetteer</li>
          <li><strong>Frontend:</strong> React + TypeScript + Vite, Recharts, Leaflet/OpenStreetMap</li>
          <li><strong>Live data:</strong> USGS (earthquakes) and GDACS (multi-hazard) — both real, no API key. ReliefWeb's fetch/parse code is real but currently inactive pending an approved API appname (see below)</li>
        </ul>
      </Section>

      <Section title="Methodology">
        <p>
          The pipeline runs: preprocessing → disaster relevance detection → disaster type classification →
          location extraction → misinformation classification → evidence lookup (stored corpus + live feeds) →
          reliability scoring → priority scoring → persistence → dashboard. Every rule-based threshold (the
          misinformation UNVERIFIED band, the priority score weights, the reliability score weights) is documented
          in source comments with the reasoning behind it, and is stated as a judgment call rather than a learned
          constant where that's what it actually is.
        </p>
      </Section>

      <Section title="What's real vs. Future Enhancement">
        <div className="table-scroll">
          <table>
            <thead>
              <tr><th>Capability</th><th>Status</th></tr>
            </thead>
            <tbody>
              <Row a="Disaster relevance + type classification" b="Real — rule-based, 13 categories" />
              <Row a="Location extraction" b="Real — India Post gazetteer (~39,700 localities), fuzzy matching" />
              <Row a="Misinformation classification" b="Real — TF-IDF + Logistic Regression, compared against Random Forest and linear SVM" />
              <Row a="Stored-corpus verification" b="Real, but checks our own IFND corpus — not a live government source" />
              <Row a="USGS / GDACS live feeds" b="Real, no API key, polled periodically (not real-time)" />
              <Row a="ReliefWeb live feed" b="Code is real; inactive — requires an approved API appname we don't have yet" />
              <Row a="Location coordinates" b="Real, offline city/state centroids — locality-level claims render at their city's centroid, not a street-level point" />
              <Row a="Reliability score" b="Real, rule-based and documented — not a trained model" />
              <Row a="NewsAPI / Google Fact Check / Reddit / Telegram" b="Future Enhancement — credentials were never obtained" />
              <Row a="MuRIL / IndicBERT / LLM comparison classifiers" b="Future Enhancement — no labeled multilingual data exists yet" />
              <Row a="Emergency-service contact from alerts" b="Not implemented — alerts are for relief-org consideration only" />
            </tbody>
          </table>
        </div>
      </Section>

      <Section title="Future enhancements">
        <ul>
          <li>True real-time social-media stream processing (Kafka/RabbitMQ-based)</li>
          <li>More disaster APIs, once credentials are obtained</li>
          <li>Multilingual misinformation detection (Hindi/regional languages)</li>
          <li>Image/video misinformation analysis</li>
          <li>Satellite/remote-sensing evidence and advanced geospatial analysis</li>
          <li>Mobile application with push notifications</li>
          <li>NGO authentication and human-in-the-loop verification</li>
        </ul>
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="card" style={{ marginBottom: 20 }}>
      <h2 style={{ fontSize: "1.1rem", margin: "0 0 12px" }}>{title}</h2>
      {children}
    </div>
  );
}

function Row({ a, b }: { a: string; b: string }) {
  return (
    <tr>
      <td style={{ whiteSpace: "normal" }}>{a}</td>
      <td style={{ whiteSpace: "normal" }} className="muted">{b}</td>
    </tr>
  );
}
