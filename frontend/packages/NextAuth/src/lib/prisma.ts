// src/lib/prisma.ts (or lib/prisma.ts)
import { PrismaClient } from "../generated/prisma/client";

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    // log: ["query", "error", "warn"], // optional
  });

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;

// This is a global for prisma to avoid multiple instances of the prisma client in development
// For the development environment, hot-reload will cause multiple instances of the prisma client to be created
// This is a global for prisma to avoid multiple instances of the prisma client in development
// For the development environment, hot-reload will cause multiple instances of the prisma client to be created
