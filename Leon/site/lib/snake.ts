export type Point = { x: number; y: number };
export function stepSnake(snake: Point[], direction: Point, food: Point) {
  const head = { x: (snake[0].x + direction.x + 16) % 16, y: (snake[0].y + direction.y + 16) % 16 };
  const eats = head.x === food.x && head.y === food.y;
  const collision = snake.some(p => p.x === head.x && p.y === head.y);
  return { collision, eats, snake: [head, ...(eats ? snake : snake.slice(0, -1))] };
}
