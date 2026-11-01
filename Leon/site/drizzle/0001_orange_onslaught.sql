DROP INDEX `idx_tickets_queue`;--> statement-breakpoint
ALTER TABLE `tickets` ADD `department` text DEFAULT 'AI' NOT NULL;--> statement-breakpoint
CREATE INDEX `idx_tickets_queue` ON `tickets` (`department`,`state`,`created`);--> statement-breakpoint
ALTER TABLE `tickets` DROP COLUMN `contact`;--> statement-breakpoint
ALTER TABLE `tickets` DROP COLUMN `slot`;--> statement-breakpoint
ALTER TABLE `tickets` DROP COLUMN `starts`;