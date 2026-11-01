CREATE TABLE `tickets` (
	`owner` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`team` text NOT NULL,
	`contact` text NOT NULL,
	`slot` text NOT NULL,
	`starts` integer NOT NULL,
	`state` text NOT NULL,
	`partner` text,
	`excluded` text,
	`created` integer NOT NULL,
	`seen` integer NOT NULL,
	`matched` integer
);
--> statement-breakpoint
CREATE INDEX `idx_tickets_queue` ON `tickets` (`slot`,`state`,`created`);