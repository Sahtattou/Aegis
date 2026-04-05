import type { ReactNode } from "react";

import { Button } from "./button";

type DialogProps = {
  open: boolean;
  title: string;
  children?: ReactNode;
  confirmLabel: string;
  cancelLabel?: string;
  confirmDisabled?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
};

export function Dialog({
  open,
  title,
  children,
  confirmLabel,
  cancelLabel = "Cancel",
  confirmDisabled = false,
  onConfirm,
  onCancel,
}: DialogProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/70 p-4">
      <div className="w-full max-w-2xl rounded-lg border border-slate-800 bg-slate-900 p-4 text-slate-100 shadow-2xl">
        <h3 className="text-lg font-semibold">{title}</h3>
        <div className="mt-3 text-sm text-slate-300">{children}</div>
        <div className="mt-4 flex justify-end gap-2">
          <Button className="border-slate-700 bg-slate-800 text-slate-200 hover:bg-slate-700" onClick={onCancel}>
            {cancelLabel}
          </Button>
          <Button
            className="border-cyan-500 bg-cyan-500 text-slate-950 hover:bg-cyan-400"
            onClick={onConfirm}
            disabled={confirmDisabled}
          >
            {confirmLabel}
          </Button>
        </div>
      </div>
    </div>
  );
}
