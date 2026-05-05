import { cn } from "@/lib/utils";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "default" | "success" | "warning" | "error" | "info";
  className?: string;
}

const variantStyles = {
  default: "bg-gray-100 text-gray-800",
  success: "bg-green-100 text-green-800",
  warning: "bg-yellow-100 text-yellow-800",
  error: "bg-red-100 text-red-800",
  info: "bg-blue-100 text-blue-800",
};

export function Badge({ children, variant = "default", className }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium",
        variantStyles[variant],
        className
      )}
    >
      {children}
    </span>
  );
}

// Status-specific badge
export function StatusBadge({ status }: { status: string }) {
  const statusConfig: Record<string, { label: string; variant: BadgeProps["variant"] }> = {
    draft: { label: "Draft", variant: "default" },
    in_review: { label: "In Review", variant: "warning" },
    approved: { label: "Approved", variant: "success" },
    scheduled: { label: "Scheduled", variant: "info" },
    publishing: { label: "Publishing", variant: "info" },
    published: { label: "Published", variant: "success" },
    failed: { label: "Failed", variant: "error" },
    archived: { label: "Archived", variant: "default" },
  };

  const config = statusConfig[status] || { label: status, variant: "default" as const };

  return <Badge variant={config.variant}>{config.label}</Badge>;
}
