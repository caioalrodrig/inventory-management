import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog";
import { useState } from "react";
import { toast } from "sonner";
import { useAddInventoryItem } from "@/api/inventory";

interface Props {
  open: boolean;
  onOpenChange: (v: boolean) => void;
}

export default function AddItemDialog({ open, onOpenChange }: Props) {
  const [name, setName] = useState("");
  const [quantity, setQuantity] = useState("");
  const addItem = useAddInventoryItem();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const qty = parseInt(quantity, 10);
    if (Number.isNaN(qty) || qty < 1) {
      toast.error("Quantidade deve ser pelo menos 1.");
      return;
    }
    addItem.mutate(
      { name: name.trim(), quantity: qty },
      {
        onSuccess: (data) => {
          toast.success(`Item adicionado: ${data.identifier}`, {
            description: `ID: ${data.id}`,
          });
          setName("");
          setQuantity("");
          onOpenChange(false);
        },
        onError: (err) => {
          toast.error(
            err instanceof Error ? err.message : "Erro ao adicionar item",
          );
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Adicionar Item ao Estoque</DialogTitle>
          <DialogDescription>
            POST /api/inventory/ — O nome será normalizado automaticamente.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="flex flex-col gap-4 mt-2">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Nome do Item
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              placeholder="Ex: Açaí"
              className="border border-input rounded-md px-3 py-2 text-sm bg-background outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              Quantidade
            </label>
            <input
              type="number"
              min={1}
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              required
              placeholder="10"
              className="border border-input rounded-md px-3 py-2 text-sm bg-background outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <button
            type="submit"
            disabled={addItem.isPending}
            className="bg-primary text-primary-foreground py-2 rounded-lg text-sm font-semibold hover:brightness-110 transition-all active:scale-95 disabled:opacity-50"
          >
            {addItem.isPending ? "Adicionando..." : "Adicionar ao Estoque"}
          </button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
