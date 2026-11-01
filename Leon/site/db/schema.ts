import { sqliteTable, text, integer, index } from "drizzle-orm/sqlite-core";

export const tickets = sqliteTable("tickets", {
  owner: text("owner").primaryKey(),
  name: text("name").notNull(),
  team: text("team").notNull(),
  department: text("department").notNull().default("AI"),
  state: text("state").notNull(),
  partner: text("partner"),
  excluded: text("excluded"),
  created: integer("created").notNull(),
  seen: integer("seen").notNull(),
  matched: integer("matched"),
  memberId: text("member_id"),
  meetingRole: text("meeting_role"),
  meetingTeam: text("meeting_team"),
}, t => [index("idx_tickets_queue").on(t.department, t.state, t.created)]);

// Aggregate only: no participant details are retained in daily counts.
export const dailyMatches = sqliteTable("daily_matches", {
  day: text("day").primaryKey(),
  count: integer("count").notNull().default(0),
});
