import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "@/lib/api";
import type {
  AddInventoryRequest,
  AddInventoryResponse,
  InventoryItem,
} from "@/types/inventory";

const INVENTORY_BASE = "/api/inventory";

type SortKey = "name" | "quantity" | "last_updated";
type Direction = "asc" | "desc";

export const inventoryKeys = {
  all: ["inventory"] as const,
  list: (orderBy?: SortKey | null, direction?: Direction | null) =>
    [...inventoryKeys.all, "list", orderBy ?? null, direction ?? null] as const,
};

async function listInventory(
  orderBy?: SortKey | null,
  direction?: Direction | null
): Promise<InventoryItem[]> {
  const params = new URLSearchParams();
  if (orderBy) params.set("order_by", orderBy);
  if (direction) params.set("direction", direction);
  const qs = params.toString();
  const path = qs ? `${INVENTORY_BASE}/?${qs}` : `${INVENTORY_BASE}/`;
  return apiFetch<InventoryItem[]>(path);
}

async function addItem(body: AddInventoryRequest): Promise<AddInventoryResponse> {
  return apiFetch<AddInventoryResponse>(INVENTORY_BASE + "/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

async function removeQuantity(
  itemId: string,
  quantity: number
): Promise<InventoryItem> {
  return apiFetch<InventoryItem>(`${INVENTORY_BASE}/${itemId}/`, {
    method: "DELETE",
    body: JSON.stringify({ quantity }),
  });
}

export function useInventoryList(
  orderBy?: SortKey | null,
  direction?: Direction | null
) {
  return useQuery({
    queryKey: inventoryKeys.list(orderBy, direction),
    queryFn: () => listInventory(orderBy, direction),
  });
}

export function useAddInventoryItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: addItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all });
    },
  });
}

export function useRemoveInventoryQuantity() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ itemId, quantity }: { itemId: string; quantity: number }) =>
      removeQuantity(itemId, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: inventoryKeys.all });
    },
  });
}
