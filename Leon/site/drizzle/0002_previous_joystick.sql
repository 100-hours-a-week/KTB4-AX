CREATE TABLE `daily_matches` (
	`day` text PRIMARY KEY NOT NULL,
	`count` integer DEFAULT 0 NOT NULL
);
--> statement-breakpoint
ALTER TABLE `tickets` ADD `member_id` text;--> statement-breakpoint
ALTER TABLE `tickets` ADD `meeting_role` text;--> statement-breakpoint
ALTER TABLE `tickets` ADD `meeting_team` text;