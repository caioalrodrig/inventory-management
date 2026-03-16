import { Package, LayoutGrid } from "lucide-react";
import { useLocation, Link } from "react-router-dom";

const NAV_ITEMS = [
  { to: "/", icon: LayoutGrid, label: "Dashboard" },
  { to: "/inventory", icon: Package, label: "Estoque" },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <aside className="w-64 border-r border-border flex flex-col p-4 gap-8 bg-card/50 shrink-0">
      <div className="px-3 py-2 flex items-center gap-2">
        <div className="w-7 h-7 bg-primary rounded-sm flex items-center justify-center">
          <Package size={14} className="text-primary-foreground" />
        </div>
        <span className="font-bold tracking-tighter text-lg">ESTOQUE</span>
      </div>

      <nav className="flex flex-col gap-1">
        {NAV_ITEMS.map(({ to, icon: Icon, label }) => {
          const active = location.pathname === to;
          return (
            <Link
              key={to}
              to={to}
              className={`flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200 ${
                active
                  ? "bg-card ring-1 ring-border text-primary shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Icon size={18} />
              <span className="text-sm font-medium">{label}</span>
            </Link>
          );
        })}
      </nav>

    </aside>
  );
}
