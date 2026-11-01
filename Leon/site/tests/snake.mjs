import assert from 'node:assert/strict';
import { stepSnake } from '../lib/snake.ts';
for (const [start, direction, expected] of [
  [{x:15,y:6},{x:1,y:0},{x:0,y:6}],
  [{x:0,y:6},{x:-1,y:0},{x:15,y:6}],
  [{x:6,y:0},{x:0,y:-1},{x:6,y:15}],
  [{x:6,y:15},{x:0,y:1},{x:6,y:0}],
]) {
  const frame = stepSnake([start],direction,{x:8,y:8});
  assert.deepEqual(frame.snake[0],expected);
  assert.equal(frame.collision,false);
}
const body = [{x:3,y:3},{x:3,y:4},{x:2,y:4},{x:2,y:3}];
assert.equal(stepSnake(body,{x:-1,y:0},{x:8,y:8}).collision,true,'Hitting the tail ends the game');
assert.equal(stepSnake([{x:15,y:4},{x:0,y:4}],{x:1,y:0},{x:8,y:8}).collision,true,'Body collision still applies across the edge');
const fed = stepSnake([{x:15,y:4}],{x:1,y:0},{x:0,y:4});
assert.equal(fed.eats,true); assert.equal(fed.snake.length,2);
let frame = {snake:[{x:8,y:8},{x:7,y:8},{x:6,y:8},{x:5,y:8},{x:4,y:8}]};
for(let i=0;i<100;i++) { frame=stepSnake(frame.snake,{x:1,y:0},{x:6,y:2}); assert.equal(frame.collision,false); }
console.log('PASS: four-edge wrapping, tail collision, collision across edge, food on edge, and 100 uninterrupted straight steps.');
