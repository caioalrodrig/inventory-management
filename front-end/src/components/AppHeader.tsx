import { Search, Plus } from "lucide-react";
import { useState } from "react";
import AddItemDialog from "./AddItemDialog";

export default function AppHeader() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <header className="h-16 border-b border-border bg-card flex items-center justify-between px-8">
        <div className="flex items-center gap-4 flex-1">
          <Search size={18} className="text-muted-foreground" />
          <input
            type="text"
            placeholder="Buscar itens, identificadores..."
            className="bg-transparent outline-none text-sm w-64 font-medium placeholder:text-muted-foreground"
          />
        </div>
        <button
          onClick={() => setOpen(true)}
          className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-semibold hover:brightness-110 transition-all active:scale-95"
        >
          <Plus size={16} />
          Adicionar Item
        </button>
      </header>
      <AddItemDialog open={open} onOpenChange={setOpen} />
    </>
  );
}
