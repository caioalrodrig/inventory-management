import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar";
import AppHeader from "./AppHeader";

export default function AppLayout() {
  return (
    <div className="min-h-svh flex bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <AppHeader />
        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
