"use client";

import { useEffect, useRef, useState } from "react";
import { roster, seatingRows } from "@/lib/roster";

export default function SeatingChart({ me, partner }: { me: string | null; partner: string | null }) {
  const panel = useRef<HTMLElement>(null);
  const toggle = useRef<HTMLButtonElement>(null);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (!open) return;
    const previous = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    panel.current?.querySelector<HTMLButtonElement>("button")?.focus();
    const escape = (event: KeyboardEvent) => {
      if (event.key === "Escape") { setOpen(false); toggle.current?.focus(); }
      if (event.key === "Tab" && panel.current) {
        const buttons = Array.from(panel.current.querySelectorAll<HTMLButtonElement>("button:not(:disabled)"));
        const first = buttons[0], last = buttons[buttons.length - 1];
        if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
        else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
      }
    };
    window.addEventListener("keydown", escape);
    return () => { document.body.style.overflow = previous; window.removeEventListener("keydown", escape); };
  }, [open]);
  return <><button ref={toggle} type="button" className="outline full seating-toggle" onClick={() => setOpen(true)}>전체 자리표 보기</button>{open && <section ref={panel} className="seating-chart is-open" role="dialog" aria-modal="true" aria-label="전체 팀 자리표">
    <button type="button" className="chart-close" onClick={() => { setOpen(false); toggle.current?.focus(); }}>자리표 닫기 ×</button>
    <div className="seat-legend"><span>내 자리</span><span>파트너 자리</span></div>
    <div className="seating-scroll"><div className="seat-map"><div className="room-front">RYAN D <span>좌석표 기준</span> RYAN A</div>
      {seatingRows.map((row, ri) => <div className="seat-map-row" key={ri}>{row.map((team, ci) => team ? <div className="seat-team" key={team}>
        <div className="seat-team-row">{[1,2,3].map(seat => cell(team, "상단", seat))}</div>
        <strong>{team}팀</strong>
        <div className="seat-team-row">{[1,2,3].map(seat => cell(team, "하단", seat))}</div>
      </div> : <div key={`empty-${ci}`} />)}</div>)}
    </div></div>
  </section>}</>;
  function cell(team: number, side: string, seat: number) {
    const member = roster.find(m => m.team === `${team}팀` && m.side === side && m.seat === seat);
    if (!member) return <span key={seat} className="seat empty-seat" aria-label="빈 자리">—</span>;
    return <div key={seat} className={`seat ${member.id === me ? "my-seat" : ""} ${member.id === partner ? "partner-seat" : ""}`} title={`${member.name} · ${member.id.split(".")[0]}`} aria-label={`${team}팀 ${member.name} ${member.id.split(".")[0]}`}><span>{member.id.split(".")[0]}</span></div>;
  }
}
