import React from 'react';
import { AlertTriangle, Info, AlertOctagon } from 'lucide-react';

export default function AlertsBanner({ alerts }) {
  if (!alerts || !alerts.length) return null;

  return (
    <div className="alerts-topbar">
      <AlertTriangle size={16} />
      <span>{alerts[0].message || 'Transit alert active'}</span>
    </div>
  );
}
