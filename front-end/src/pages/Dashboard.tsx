import { motion } from "framer-motion";
import { useInventoryList } from "@/api/inventory";
import { Package, AlertTriangle, ArrowRight } from "lucide-react";
import { Link } from "react-router-dom";

export default function Dashboard() {
  const { data: items = [], isLoading, isError, error } = useInventoryList();

  const stats = [
    {
      label: "Total de Itens",
      value: items.length.toString(),
      change: `${items.reduce((s, i) => s + (i.quantity ?? 0), 0)} un.`,
      icon: Package,
    },
    {
      label: "Estoque Crítico",
      value: items.filter((i) => (i.quantity ?? 0) < 5).length.toString(),
      change: "< 5 unidades",
      icon: AlertTriangle,
      critical: true,
    },
  ];

  const criticalItems = items
    .filter((i) => (i.quantity ?? 0) < 5)
    .sort((a, b) => (a.quantity ?? 0) - (b.quantity ?? 0));

  if (isLoading) {
    return (
      <div className="p-8 max-w-5xl w-full mx-auto flex flex-col gap-8">
        <section>
          <h1 className="text-3xl font-bold tracking-tighter">Dashboard</h1>
          <p className="text-muted-foreground text-sm animate-pulse">
            Carregando...
          </p>
        </section>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2].map((i) => (
            <div
              key={i}
              className="bg-card p-5 rounded-xl ring-1 ring-border h-24 animate-pulse"
            />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-8 max-w-5xl w-full mx-auto flex flex-col gap-4">
        <h1 className="text-3xl font-bold tracking-tighter">Dashboard</h1>
        <div className="bg-destructive/10 text-destructive rounded-lg p-4 text-sm">
          Erro ao carregar estoque: {error instanceof Error ? error.message : String(error)}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl w-full mx-auto flex flex-col gap-8">
      <section>
        <h1 className="text-3xl font-bold tracking-tighter">Dashboard</h1>
        <p className="text-muted-foreground text-sm">
          Visão geral do sistema de estoque.
        </p>
      </section>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="bg-card p-5 rounded-xl ring-1 ring-border flex flex-col gap-1"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold uppercase tracking-widest text-muted-foreground">
                {s.label}
              </span>
              <s.icon size={16} className={s.critical ? "text-warning" : "text-muted-foreground"} />
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-2xl font-bold tracking-tighter">{s.value}</span>
              <span className={`text-xs font-medium ${s.critical ? "text-warning" : "text-success"}`}>
                {s.change}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      {criticalItems.length > 0 && (
        <section className="bg-card rounded-xl ring-1 ring-border overflow-hidden">
          <div className="p-4 border-b border-border flex items-center justify-between bg-muted/30">
            <div className="flex items-center gap-2">
              <AlertTriangle size={14} className="text-warning" />
              <span className="text-sm font-bold tracking-tight">Itens com Estoque Crítico</span>
            </div>
            <Link
              to="/inventory"
              className="text-xs font-bold text-primary flex items-center gap-1 hover:underline"
            >
              Ver estoque <ArrowRight size={12} />
            </Link>
          </div>
          <div className="divide-y divide-border">
            {criticalItems.map((item) => (
              <div key={item.id} className="px-6 py-3 flex items-center justify-between">
                <div>
                  <span className="text-sm font-semibold">{item.name ?? item.identifier}</span>
                  <span className="text-xs text-muted-foreground ml-2">#{item.identifier}</span>
                </div>
                <span className="text-sm font-bold text-destructive tabular-nums">
                  {item.quantity ?? 0} un.
                </span>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}
