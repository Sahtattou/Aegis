import { Button } from "../ui/button";

type RunRedTeamButtonProps = {
  onRun: () => void;
};

export function RunRedTeamButton({ onRun }: RunRedTeamButtonProps) {
  return (
    <Button
      type="button"
      className="border-red-200 bg-red-50 text-red-700 hover:bg-red-100"
      onClick={onRun}
    >
      Run Red Team
    </Button>
  );
}
