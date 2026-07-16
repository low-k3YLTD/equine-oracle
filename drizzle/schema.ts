import { mysqlTable, serial, varchar, timestamp } from "drizzle-orm/mysql-core";

export const users = mysqlTable("users", {
  id: serial("id").primaryKey(),
  name: varchar("name", { length: 256 }),
  email: varchar("email", { length: 256 }).unique(),
  createdAt: timestamp("created_at").defaultNow(),
});

// Add other tables as needed for your application
