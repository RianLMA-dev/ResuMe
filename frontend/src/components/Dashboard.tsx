"use client";

import { useState } from "react";

import EmailForm from "./EmailForm";
import KanbanBoard from "./KanbanBoard";

export default function Dashboard() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <>
      <EmailForm onSaved={() => setRefreshKey((key) => key + 1)} />
      <KanbanBoard refreshKey={refreshKey} />
    </>
  );
}