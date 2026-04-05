import { Button } from "../ui/button";

type RunRedTeamButtonProps = {
  onRun: () => void;
};

export function RunRedTeamButton({ onRun }: RunRedTeamButtonProps) {
  return (
    <Button type="button" variant="danger" onClick={onRun}>
      Run Red Team
    </Button>
  );
}
