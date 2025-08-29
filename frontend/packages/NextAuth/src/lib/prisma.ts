// src/lib/prisma.ts (or lib/prisma.ts)
import { PrismaClient } from "../generated/prisma/client";

// This is the generated prisma client for the NextAuth package
// We are using the relative path instead of the standard @prisma/client package
// This is because this would be a custom output path as opposed to the default output path of @prisma/client
// Better for organization as well as it is commitable to the repository in github

const globalForPrisma = globalThis as unknown as { prisma?: PrismaClient };

// We are creating a global variable to store the Prisma Client instance here

export const prisma =
  globalForPrisma.prisma ??
  new PrismaClient({
    // log: ["query", "error", "warn"], // optional
  });

// We are just checking if the prisma client already exists globally, if it does, we are using that instance, if not, we are creating a new instance

if (process.env.NODE_ENV !== "production") globalForPrisma.prisma = prisma;

// We are just checking if the node environment is not production, if it is not, we are setting the global prisma client to the prisma client instance
// In development, hot-reload will cause multiple instances of the prisma client to be created, so we are setting the global prisma client to the prisma client instance
// In production, we are not setting the global prisma client to the prisma client instance, which is better for performance
