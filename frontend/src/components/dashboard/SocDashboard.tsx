import { useEffect, useMemo, useState } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  LayoutDashboard,
  ListTodo,
  Radar,
  ScrollText,
  Shield,
  ShieldCheck,
  Siren,
  TriangleAlert,
  XCircle,
} from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { Badge } from "../ui/badge";
import { Button } from "../ui/button";
import { Card } from "../ui/card";
import { Dialog } from "../ui/dialog";

type ThreatClass = "Critical" | "Blind Spot" | "Suspicious";
type ActionType = "approve" | "modify";

type BlindSpotEvent = {
  id: string;
  source: string;
  threatClass: ThreatClass;
  confidenceScore: number;
  timestamp: string;
  attackText: string;
  mitreTechnique: string;
  generatedCypherRule: string;
  shap: Array<{ feature: string; value: number }>;
};

type AuditEvent = {
  id: string;
  title: string;
  subtitle: string;
  icon: "red" | "blue" | "blind" | "approved";
};

const MOCK_BLIND_SPOTS: BlindSpotEvent[] = [
  {
    id: "BS-2026-031",
    source: "SMS Gateway · Tunis",
    threatClass: "Blind Spot",
    confidenceScore: 92,
    timestamp: "2026-04-05T09:11:00Z",
    attackText:
      "Ya weldi compte el BIAT mte3ek tblocked, verify taw b lien sécurisé: http://secure-biat-alert.ru/login",
    mitreTechnique: "T1566.001 - Spearphishing Attachment",
    generatedCypherRule:
      "MATCH (a:Attack) WHERE a.text =~ '(?i).*(biat|compte|verify|\.ru).*' MERGE (r:Rule {name:'Darija_BIAT_RU_Phish'}) SET r.updated_at=datetime()",
    shap: [
      { feature: "Uses urgent Darija keywords", value: 0.6 },
      { feature: "Contains '.ru' link", value: 0.4 },
      { feature: "Impersonates Tunisian bank", value: 0.33 },
      { feature: "Credential verification intent", value: 0.29 },
    ],
  },
  {
    id: "BS-2026-032",
    source: "Mail Ingestor · SOC-01",
    threatClass: "Critical",
    confidenceScore: 96,
    timestamp: "2026-04-05T09:15:30Z",
    attackText:
      "Objet: Mise à jour Tunisie Telecom urgente. Veuillez installer la pièce jointe pour réactiver la ligne entreprise.",
    mitreTechnique: "T1204.002 - Malicious File",
    generatedCypherRule:
      "MATCH (a:Attack) WHERE a.channel='email' AND a.text =~ '(?i).*(tunisie telecom|pi[eè]ce jointe|urgente).*' MERGE (r:Rule {name:'TT_Malicious_Attachment_Urgent'})",
    shap: [
      { feature: "Attachment execution lure", value: 0.58 },
      { feature: "Brand impersonation signal", value: 0.44 },
      { feature: "Urgency phrase in French", value: 0.31 },
      { feature: "Service disruption threat", value: 0.22 },
    ],
  },
  {
    id: "BS-2026-033",
    source: "Web Intake · Citizen Portal",
    threatClass: "Suspicious",
    confidenceScore: 84,
    timestamp: "2026-04-05T09:23:08Z",
    attackText:
      "تم تعليق حساب البريد التونسي الخاص بك. أدخل رمز OTP في الصفحة الجديدة لتفادي الإغلاق.",
    mitreTechnique: "T1111 - Multi-Factor Authentication Interception",
    generatedCypherRule:
      "MATCH (a:Attack) WHERE a.text =~ '(?i).*(otp|تم تعليق|البريد التونسي).*' MERGE (r:Rule {name:'OTP_Interception_Arabic_Local'})",
    shap: [
      { feature: "OTP harvesting intent", value: 0.55 },
      { feature: "Account suspension social pressure", value: 0.37 },
      { feature: "Arabic phishing phrasing", value: 0.25 },
      { feature: "Trusted service impersonation", value: 0.19 },
    ],
  },
];

const AUDIT_FLOW: AuditEvent[] = [
  {
    id: "AT-1",
    title: "Red Team Attack Generated",
    subtitle: "Synthetic spearphishing campaign seeded with Tunisian context",
    icon: "red",
  },
  {
    id: "AT-2",
    title: "Blue Team Missed",
    subtitle: "Rules engine did not match payload; model confidence below threshold",
    icon: "blue",
  },
  {
    id: "AT-3",
    title: "Blind Spot Flagged",
    subtitle: "Analyst queue received anomaly and MITRE mapping candidate",
    icon: "blind",
  },
  {
    id: "AT-4",
    title: "Rule Approved by Analyst",
    subtitle: "Cypher detection rule prepared for graph insertion",
    icon: "approved",
  },
];

function threatTone(threatClass: ThreatClass): "danger" | "warning" | "safe" {
  if (threatClass === "Critical") {
    return "danger";
  }
  if (threatClass === "Blind Spot" || threatClass === "Suspicious") {
    return "warning";
  }
  return "safe";
}

function sidebarItems() {
  return [
    { key: "dashboard", label: "Dashboard", icon: LayoutDashboard },
    { key: "queue", label: "Queue", icon: ListTodo },
    { key: "rules", label: "Rules", icon: ShieldCheck },
    { key: "audit", label: "Audit", icon: ScrollText },
  ];
}

function auditIcon(icon: AuditEvent["icon"]) {
  if (icon === "red") {
    return <Siren className="h-4 w-4 text-red-400" />;
  }
  if (icon === "blue") {
    return <Radar className="h-4 w-4 text-cyan-400" />;
  }
  if (icon === "blind") {
    return <TriangleAlert className="h-4 w-4 text-amber-300" />;
  }
  return <CheckCircle2 className="h-4 w-4 text-emerald-300" />;
}

export function SocDashboard() {
  const [blindSpots, setBlindSpots] = useState<BlindSpotEvent[]>([]);
  const [selectedId, setSelectedId] = useState<string>(MOCK_BLIND_SPOTS[0].id);
  const [dialogAction, setDialogAction] = useState<ActionType | null>(null);
  const [modifyRule, setModifyRule] = useState<string>("");
  const [actionState, setActionState] = useState<string>("Awaiting analyst action");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const enableLiveSse = false;

  useEffect(() => {
    if (enableLiveSse) {
      const stream = new EventSource("/api/stream");
      stream.onmessage = (event) => {
        const incoming = JSON.parse(event.data) as BlindSpotEvent;
        setBlindSpots((prev) => [incoming, ...prev]);
      };
      return () => stream.close();
    }
    setBlindSpots(MOCK_BLIND_SPOTS);
  }, []);

  const selectedEvent = useMemo(
    () => blindSpots.find((item) => item.id === selectedId) ?? blindSpots[0],
    [blindSpots, selectedId],
  );

  useEffect(() => {
    if (selectedEvent) {
      setModifyRule(selectedEvent.generatedCypherRule);
    }
  }, [selectedEvent]);

  async function submitAnalystAction(action: ActionType): Promise<void> {
    if (!selectedEvent) {
      return;
    }
    setIsSubmitting(true);
    const payload = {
      blindSpotId: selectedEvent.id,
      action,
      cypher: action === "modify" ? modifyRule : selectedEvent.generatedCypherRule,
      timestamp: new Date().toISOString(),
    };
    try {
      const response = await fetch("/api/rules/approve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error(`Rule action failed: ${response.status}`);
      }
      setActionState(
        action === "approve"
          ? `Approved ${selectedEvent.id} and queued rule synchronization.`
          : `Modified ${selectedEvent.id} and sent updated Cypher for review.`,
      );
    } catch {
      setActionState("FastAPI endpoint unavailable in mock mode; action retained locally.");
    } finally {
      setIsSubmitting(false);
      setDialogAction(null);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-950 to-black text-slate-100">
      <div className="flex min-h-screen">
        <aside className="w-72 border-r border-slate-800/90 bg-[#05080f] px-4 py-6">
          <div className="mb-8 flex items-center gap-3">
            <div className="rounded-md border border-cyan-500/50 bg-cyan-500/10 p-2">
              <Shield className="h-5 w-5 text-cyan-300" />
            </div>
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-slate-500">HARIS SOC</p>
              <h1 className="text-lg font-semibold text-slate-100">Modern Dark Mode</h1>
            </div>
          </div>

          <nav aria-label="SOC Navigation">
            <ul className="space-y-2">
              {sidebarItems().map((item) => {
                const Icon = item.icon;
                return (
                  <li key={item.key}>
                    <button
                      type="button"
                      className="flex w-full items-center gap-3 rounded-md border border-slate-800 bg-slate-900/60 px-3 py-2 text-left text-sm text-slate-200 transition hover:border-cyan-500/40 hover:bg-slate-900"
                    >
                      <Icon className="h-4 w-4 text-cyan-300" />
                      <span>{item.label}</span>
                    </button>
                  </li>
                );
              })}
            </ul>
          </nav>

          <div className="mt-10 rounded-md border border-slate-700 bg-slate-900/70 p-3 text-xs text-slate-300">
            <p className="mb-1 uppercase tracking-[0.2em]">Stream status</p>
            <p className="flex items-center gap-2 text-slate-200">
              <Clock3 className="h-3.5 w-3.5 text-amber-300" />
              {enableLiveSse ? "Live SSE connection enabled" : "Mock SSE feed seeded from local fixtures"}
            </p>
          </div>
        </aside>

        <main className="flex-1 bg-[radial-gradient(circle_at_top_right,#0b1220,transparent_48%)] p-6">
          <div className="grid gap-6 xl:grid-cols-[420px_1fr]">
            <Card className="border-slate-700 bg-slate-900/95 text-slate-100">
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <h2 className="text-base font-semibold text-white">Real-time Blind Spot Queue</h2>
                  <p className="text-xs text-slate-300">Server-Sent Event feed (simulated)</p>
                </div>
                <Badge label={`${blindSpots.length} Events`} tone="warning" />
              </div>

              <div className="max-h-[560px] space-y-3 overflow-y-auto pr-1">
                {blindSpots.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => setSelectedId(item.id)}
                    className={
                      selectedEvent?.id === item.id
                        ? "w-full rounded-md border border-cyan-400 bg-slate-800/95 p-3 text-left shadow-[0_0_0_1px_rgba(34,211,238,0.35)]"
                        : "w-full rounded-md border border-slate-700 bg-slate-950/80 p-3 text-left hover:border-slate-500"
                    }
                  >
                    <div className="mb-2 flex items-center justify-between">
                      <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-300">{item.id}</p>
                      <Badge label={item.threatClass} tone={threatTone(item.threatClass)} />
                    </div>
                    <p className="text-sm text-slate-100">{item.attackText.slice(0, 100)}...</p>
                    <div className="mt-2 flex items-center justify-between text-xs text-slate-400">
                      <span>{item.source}</span>
                      <span>{new Date(item.timestamp).toLocaleTimeString()}</span>
                    </div>
                  </button>
                ))}
              </div>
            </Card>

            <div className="space-y-6">
              <Card className="border-slate-700 bg-slate-900/95 text-slate-100">
                <div className="mb-4 flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-base font-semibold text-white">Attack Autopsy Card</h2>
                    <p className="text-xs text-slate-300">Detailed forensic context for selected blind spot</p>
                  </div>
                  <Badge label={selectedEvent?.threatClass ?? "N/A"} tone={selectedEvent ? threatTone(selectedEvent.threatClass) : "neutral"} />
                </div>

                {selectedEvent ? (
                  <>
                    <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                      <div className="rounded border border-slate-700 bg-[#040711] p-3">
                        <p className="text-[11px] uppercase tracking-[0.14em] text-slate-500">Threat Class</p>
                        <p className="mt-1 text-sm text-white">{selectedEvent.threatClass}</p>
                      </div>
                      <div className="rounded border border-slate-700 bg-[#040711] p-3">
                        <p className="text-[11px] uppercase tracking-[0.14em] text-slate-500">Confidence</p>
                        <p className="mt-1 text-sm text-white">{selectedEvent.confidenceScore}%</p>
                      </div>
                      <div className="rounded border border-slate-700 bg-[#040711] p-3">
                        <p className="text-[11px] uppercase tracking-[0.14em] text-slate-500">Timestamp</p>
                        <p className="mt-1 text-sm text-white">{new Date(selectedEvent.timestamp).toLocaleString()}</p>
                      </div>
                      <div className="rounded border border-slate-700 bg-[#040711] p-3">
                        <p className="text-[11px] uppercase tracking-[0.14em] text-slate-500">MITRE</p>
                        <p className="mt-1 text-sm text-cyan-300">{selectedEvent.mitreTechnique}</p>
                      </div>
                    </div>

                    <div className="mt-4 rounded border border-slate-700 bg-[#040711] p-3">
                      <p className="mb-1 text-[11px] uppercase tracking-[0.14em] text-slate-500">Raw Attack Text</p>
                      <p className="text-sm leading-6 text-slate-100">{selectedEvent.attackText}</p>
                    </div>

                    <div className="mt-4 rounded border border-slate-700 bg-[#040711] p-3">
                      <p className="mb-2 text-[11px] uppercase tracking-[0.14em] text-slate-500">SHAP Explanation</p>
                      <div className="h-72 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                          <BarChart data={selectedEvent.shap} layout="vertical" margin={{ left: 24, right: 16, top: 8, bottom: 8 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                            <XAxis type="number" stroke="#cbd5e1" tick={{ fill: "#e2e8f0", fontSize: 12 }} />
                            <YAxis type="category" dataKey="feature" stroke="#cbd5e1" width={190} tick={{ fill: "#e2e8f0", fontSize: 12 }} />
                            <Tooltip
                              cursor={{ fill: "#0f172a" }}
                              contentStyle={{
                                backgroundColor: "#030712",
                                borderColor: "#475569",
                                borderRadius: 8,
                                color: "#f8fafc",
                              }}
                            />
                            <Bar dataKey="value" fill="#06b6d4" radius={[0, 6, 6, 0]} />
                          </BarChart>
                        </ResponsiveContainer>
                      </div>
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-slate-400">No event selected.</p>
                )}
              </Card>

              <Card className="border-slate-700 bg-slate-900/95 text-slate-100">
                <h3 className="text-base font-semibold text-white">Action Board</h3>
                <p className="mt-1 text-xs text-slate-300">Analyst confirmation required before rule mutation request.</p>

                <div className="mt-4 flex flex-wrap gap-2">
                  <Button
                    className="bg-emerald-600 text-white hover:bg-emerald-500"
                    onClick={() => setDialogAction("approve")}
                    disabled={!selectedEvent}
                  >
                    <CheckCircle2 className="mr-1.5 h-4 w-4" />
                    Approve Rule
                  </Button>
                  <Button
                    className="bg-cyan-600 text-white hover:bg-cyan-500"
                    onClick={() => setDialogAction("modify")}
                    disabled={!selectedEvent}
                  >
                    <ShieldCheck className="mr-1.5 h-4 w-4" />
                    Modify Rule
                  </Button>
                  <Button
                    variant="danger"
                    className="bg-red-700 hover:bg-red-600"
                    disabled={!selectedEvent}
                    onClick={() => setActionState(`Dismissed ${selectedEvent?.id ?? "event"} from analyst queue.`)}
                  >
                    <XCircle className="mr-1.5 h-4 w-4" />
                    Dismiss
                  </Button>
                </div>

                <div className="mt-4 rounded border border-slate-700 bg-[#040711] p-3 text-sm text-slate-100">{actionState}</div>
              </Card>
            </div>
          </div>

          <Card className="mt-6 border-slate-700 bg-slate-900/95 text-slate-100">
            <div className="mb-4 flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-cyan-300" />
              <h3 className="text-base font-semibold text-white">Audit Timeline · Neo4j Graph Path</h3>
            </div>

            <div className="relative pl-8">
              <div className="absolute left-3 top-0 h-full w-px bg-slate-600" />
              <ul className="space-y-4">
                {AUDIT_FLOW.map((event) => (
                  <li key={event.id} className="relative">
                    <span className="absolute -left-[1.72rem] mt-1 inline-flex h-6 w-6 items-center justify-center rounded-full border border-cyan-500/30 bg-slate-950">
                      {auditIcon(event.icon)}
                    </span>
                    <div className="rounded-md border border-slate-700 bg-[#040711] p-3">
                      <p className="text-sm font-semibold text-white">{event.title}</p>
                      <p className="mt-1 text-xs text-slate-300">{event.subtitle}</p>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </Card>
        </main>
      </div>

      <Dialog
        open={dialogAction === "approve"}
        title="Approve Generated Cypher Rule"
        confirmLabel="Confirm Approval"
        confirmDisabled={isSubmitting || !selectedEvent}
        onCancel={() => setDialogAction(null)}
        onConfirm={() => void submitAnalystAction("approve")}
      >
        <div className="space-y-2">
          <p className="text-slate-300">Review and confirm rule deployment for the selected blind spot.</p>
          <pre className="max-h-36 overflow-auto rounded border border-slate-700 bg-slate-950 p-3 text-xs text-cyan-300">
            {selectedEvent?.generatedCypherRule}
          </pre>
        </div>
      </Dialog>

      <Dialog
        open={dialogAction === "modify"}
        title="Modify Cypher Rule Before Submission"
        confirmLabel="Submit Modified Rule"
        confirmDisabled={isSubmitting || !selectedEvent}
        onCancel={() => setDialogAction(null)}
        onConfirm={() => void submitAnalystAction("modify")}
      >
        <div className="space-y-3">
          <p className="text-slate-300">Adjust the Cypher logic before sending the modification request.</p>
          <textarea
            className="h-40 w-full rounded border border-slate-700 bg-slate-950 p-3 text-xs text-cyan-300"
            value={modifyRule}
            onChange={(event) => setModifyRule(event.target.value)}
          />
        </div>
      </Dialog>
    </div>
  );
}
