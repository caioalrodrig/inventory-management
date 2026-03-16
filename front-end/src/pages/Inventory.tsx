import { useState } from "react";
import { motion } from "framer-motion";
import { useInventoryList, useRemoveInventoryQuantity } from "@/api/inventory";
import type { InventoryItem } from "@/types/inventory";
import { ArrowUpDown, Minus, Package } from "lucide-react";
import { toast } from "sonner";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog";

type SortKey = "name" | "quantity" | "last_updated";
type Direction = "asc" | "desc";

export default function Inventory() {
  const [sortBy, setSortBy] = useState<SortKey>("quantity");
  const [direction, setDirection] = useState<Direction>("asc");
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [removeQty, setRemoveQty] = useState<string>("");

  const { data: items = [], isLoading, isError, error } = useInventoryList(
    sortBy,
    direction
  );
  const removeMutation = useRemoveInventoryQuantity();

  const toggleSort = (key: SortKey) => {
    if (sortBy === key) setDirection((d) => (d === "asc" ? "desc" : "asc"));
    else {
      setSortBy(key);
      setDirection("asc");
    }
  };

  const openRemoveDialog = (item: InventoryItem) => {
    if ((item.quantity ?? 0) <= 0) return;
    setSelectedItem(item);
    setRemoveQty("1");
  };

  const handleConfirmRemove = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItem) return;
    const currentQty = selectedItem.quantity ?? 0;
    const qtyNumber = parseInt(removeQty, 10);
    if (Number.isNaN(qtyNumber) || qtyNumber <= 0) {
      toast.error("Informe uma quantidade maior que zero.");
      return;
    }
    if (qtyNumber > currentQty) {
      toast.error("Quantidade a remover não pode ser maior que o estoque atual.");
      return;
    }
    removeMutation.mutate(
      { itemId: selectedItem.id, quantity: qtyNumber },
      {
        onSuccess: () => {
          toast.success(
            `Removidos ${qtyNumber} de ${selectedItem.name ?? selectedItem.identifier}`
          );
          setSelectedItem(null);
          setRemoveQty("");
        },
        onError: (err) => {
          toast.error(err instanceof Error ? err.message : "Erro ao remover");
        },
      }
    );
  };

  const SortHeader = ({ label, field }: { label: string; field: SortKey }) => (
    <th
      className="px-6 py-4 font-semibold cursor-pointer select-none hover:text-foreground transition-colors"
      onClick={() => toggleSort(field)}
    >
      <span className="flex items-center gap-1">
        {label}
        <ArrowUpDown size={10} className={sortBy === field ? "text-primary" : ""} />
      </span>
    </th>
  );

  if (isLoading) {
    return (
      <div className="p-8 max-w-5xl w-full mx-auto flex flex-col gap-6">
        <section>
          <h1 className="text-3xl font-bold tracking-tighter">Estoque</h1>
          <p className="text-muted-foreground text-sm animate-pulse">
            Carregando...
          </p>
        </section>
        <div className="bg-card rounded-xl ring-1 ring-border h-64 animate-pulse" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-8 max-w-5xl w-full mx-auto flex flex-col gap-4">
        <h1 className="text-3xl font-bold tracking-tighter">Estoque</h1>
        <div className="bg-destructive/10 text-destructive rounded-lg p-4 text-sm">
          Erro ao carregar estoque: {error instanceof Error ? error.message : String(error)}
        </div>
      </div>
    );
  }

  return (
    <div className="p-8 max-w-5xl w-full mx-auto flex flex-col gap-6">
      <section>
        <h1 className="text-3xl font-bold tracking-tighter">Estoque</h1>
        <p className="text-muted-foreground text-sm">
          GET /api/inventory/?order_by={sortBy}&direction={direction}
        </p>
      </section>

      <section className="bg-card rounded-xl ring-1 ring-border overflow-hidden">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="text-[11px] uppercase tracking-widest text-muted-foreground border-b border-border">
              <th className="px-6 py-4 font-semibold">ID</th>
              <SortHeader label="Nome" field="name" />
              <SortHeader label="Quantidade" field="quantity" />
              <SortHeader label="Atualizado" field="last_updated" />
              <th className="px-6 py-4 font-semibold text-right">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-muted">
            {items.map((item, i) => (
              <motion.tr
                key={item.id}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                className="group hover:bg-muted/50 transition-colors"
              >
                <td className="px-6 py-4 text-xs text-muted-foreground font-mono">#{item.id}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-muted rounded flex items-center justify-center text-muted-foreground group-hover:bg-card group-hover:ring-1 group-hover:ring-border transition-all">
                      <Package size={14} />
                    </div>
                    <div className="flex flex-col">
                      <span className="text-sm font-semibold">{item.name ?? item.identifier}</span>
                      <span className="text-[11px] text-muted-foreground">{item.identifier}</span>
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span
                    className={`text-sm font-bold tabular-nums ${
                      (item.quantity ?? 0) < 5 ? "text-destructive" : "text-foreground"
                    }`}
                  >
                    {item.quantity ?? 0}
                  </span>
                  {(item.quantity ?? 0) < 5 && (
                    <span className="ml-2 text-[10px] font-bold uppercase text-warning bg-amber-50 px-1.5 py-0.5 rounded-full ring-1 ring-amber-200">
                      Crítico
                    </span>
                  )}
                </td>
                <td className="px-6 py-4 text-sm text-muted-foreground tabular-nums">
                  {item.last_updated
                    ? new Date(item.last_updated).toLocaleDateString("pt-BR", {
                        day: "2-digit",
                        month: "short",
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    : "—"}
                </td>
                <td className="px-6 py-4 text-right">
                  <button
                    onClick={() => openRemoveDialog(item)}
                    disabled={removeMutation.isPending || (item.quantity ?? 0) <= 0}
                    className="text-xs font-semibold text-destructive hover:bg-destructive/10 px-3 py-1.5 rounded-md transition-colors inline-flex items-center gap-1 disabled:opacity-50"
                  >
                    <Minus size={12} />
                    Remover
                  </button>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </section>

      <Dialog open={!!selectedItem} onOpenChange={(open) => !open && setSelectedItem(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Remover quantidade do estoque</DialogTitle>
            <DialogDescription>
              Informe quanto deseja remover de{" "}
              <span className="font-semibold">
                {selectedItem?.name ?? selectedItem?.identifier}
              </span>{" "}
              (estoque atual: {selectedItem?.quantity ?? 0}).
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleConfirmRemove} className="flex flex-col gap-4 mt-2">
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Quantidade a remover
              </label>
              <input
                type="number"
                min={1}
                max={selectedItem?.quantity ?? undefined}
                value={removeQty}
                onChange={(e) => setRemoveQty(e.target.value)}
                required
                className="border border-input rounded-md px-3 py-2 text-sm bg-background outline-none focus:ring-2 focus:ring-ring"
              />
            </div>
            <DialogFooter>
              <button
                type="button"
                onClick={() => setSelectedItem(null)}
                className="px-3 py-2 text-sm rounded-md border border-input text-muted-foreground hover:bg-muted"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={removeMutation.isPending}
                className="bg-destructive text-destructive-foreground py-2 px-4 rounded-lg text-sm font-semibold hover:brightness-110 transition-all active:scale-95 disabled:opacity-50"
              >
                {removeMutation.isPending ? "Removendo..." : "Confirmar remoção"}
              </button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
