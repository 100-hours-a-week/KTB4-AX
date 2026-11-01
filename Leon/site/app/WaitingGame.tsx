"use client";

import { useEffect, useRef, useState } from "react";
import { stepSnake, type Point } from "@/lib/snake";

const start = [{ x: 8, y: 8 }, { x: 7, y: 8 }, { x: 6, y: 8 }, { x: 5, y: 8 }, { x: 4, y: 8 }];
const vectors: Record<string, Point> = { ArrowUp: { x: 0, y: -1 }, ArrowDown: { x: 0, y: 1 }, ArrowLeft: { x: -1, y: 0 }, ArrowRight: { x: 1, y: 0 } };
const equal = (a: Point, b: Point) => a.x === b.x && a.y === b.y;

export default function WaitingGame({ seconds }: { seconds: number }) {
  const [snake, setSnake] = useState<Point[]>(start);
  const [food, setFood] = useState<Point>({ x: 6, y: 2 });
  const [running, setRunning] = useState(false);
  const [over, setOver] = useState(false);
  const direction = useRef<Point>({ x: 1, y: 0 });
  const next = useRef<Point>({ x: 1, y: 0 });
  const touch = useRef<Point | null>(null);
  const board = useRef<HTMLDivElement>(null);
  const score = snake.length - start.length;
  function turn(key: string) {
    const v = vectors[key];
    if (v && !(v.x === -direction.current.x && v.y === -direction.current.y)) next.current = v;
  }
  function restart() {
    setSnake(start); setFood({ x: 6, y: 2 }); setOver(false); setRunning(true);
    direction.current = next.current = { x: 1, y: 0 };
    board.current?.focus();
  }
  useEffect(() => {
    if (!running) return;
    const timer = setInterval(() => {
      // Keep state updates pure; derive the next frame once per tick.
      direction.current = next.current;
      const frame = stepSnake(snake, direction.current, food);
      if (frame.collision) {
        setOver(true); setRunning(false); return;
      }
      const updated = frame.snake;
      if (frame.eats) {
        const available = Array.from({ length: 256 }, (_, i) => ({ x: i % 16, y: Math.floor(i / 16) })).filter(p => !updated.some(s => equal(s, p)));
        if (!available.length) { setOver(true); setRunning(false); }
        else setFood(available[Math.floor(Math.random() * available.length)]);
      }
      setSnake(updated);
    }, 170);
    return () => clearInterval(timer);
  }, [running, snake, food]);

  return <div className="waiting-game">
    <div className="game-heading"><span>기다리는 동안 지렁이 한 판</span><span>먹이 {score}개</span></div>
    <div ref={board} className="game-board" tabIndex={0} role="group" aria-label="지렁이 게임. 방향키로 움직이고 스페이스로 일시정지하세요."
      onKeyDown={e => { if (vectors[e.key]) { e.preventDefault(); turn(e.key); } if (e.code === "Space") { e.preventDefault(); if (over) restart(); else setRunning(v => !v); } }}
      onTouchStart={e => { touch.current = { x: e.touches[0].clientX, y: e.touches[0].clientY }; }}
      onTouchEnd={e => { if (!touch.current) return; const dx = e.changedTouches[0].clientX - touch.current.x, dy = e.changedTouches[0].clientY - touch.current.y; if (Math.max(Math.abs(dx), Math.abs(dy)) > 15) turn(Math.abs(dx) > Math.abs(dy) ? dx > 0 ? "ArrowRight" : "ArrowLeft" : dy > 0 ? "ArrowDown" : "ArrowUp"); touch.current = null; }}>
      <svg viewBox="0 0 400 400" aria-hidden="true">
        {Array.from({ length: 256 }, (_, i) => <circle key={i} cx={20 + (i % 16) * 24} cy={20 + Math.floor(i / 16) * 24} r="1.6" fill="#dce0e5" />)}
        <circle cx={20 + food.x * 24} cy={20 + food.y * 24} r="8" fill="#387ff7" />
        {[...snake].reverse().map((p, i) => <circle key={i} cx={20 + p.x * 24} cy={20 + p.y * 24} r={i === snake.length - 1 ? 10 : 5 + i / snake.length * 4} fill="#387ff7" opacity={.5 + i / snake.length * .5} />)}
        <circle cx={20 + snake[0].x * 24 + direction.current.x * 4 - direction.current.y * 3} cy={20 + snake[0].y * 24 + direction.current.y * 4 + direction.current.x * 3} r="1.5" fill="#102349" />
        <circle cx={20 + snake[0].x * 24 + direction.current.x * 4 + direction.current.y * 3} cy={20 + snake[0].y * 24 + direction.current.y * 4 - direction.current.x * 3} r="1.5" fill="#102349" />
      </svg>
      {!running && <div className="game-overlay"><button type="button" onClick={() => { if (over || score === 251) restart(); else { setRunning(true); board.current?.focus(); } }}>{over ? score === 251 ? "모든 먹이를 먹었어요! 게임 시작" : "게임 시작" : "게임 시작 / 계속하기"}</button></div>}
      <span className="game-seconds" aria-label={`매칭 대기 ${seconds}초`}>{seconds}<small>초</small></span>
    </div>
  </div>;
}
