export interface InventoryItem {
  id: string;
  identifier: string;
  name: string | null;
  quantity: number | null;
  last_updated: string | null;
}

export interface AddInventoryRequest {
  name: string;
  quantity: number;
}

export interface AddInventoryResponse {
  id: string;
  identifier: string;
}
