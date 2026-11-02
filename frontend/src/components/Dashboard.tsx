"use client";

import { useState } from "react";

import EmailForm from "./EmailForm";
import KanbanBoard from "./KanbanBoard";
import SyncButton from "./SyncButton";

export default function Dashboard() {
  const [refreshKey, setRefreshKey] = useState(0);
  const refresh = () => setRefreshKey((key) => key + 1);

  return (
    <>
      <SyncButton onSynced={refresh} />
      <EmailForm onSaved={refresh} />
      <KanbanBoard refreshKey={refreshKey} />
    </>
  );
}