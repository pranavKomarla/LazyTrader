import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';
import GoogleProvider from 'next-auth/providers/google';
import GitHubProvider from 'next-auth/providers/github';
import { PrismaAdapter } from '@auth/prisma-adapter';
import { prisma } from "@/lib/prisma";  

import bcrypt from 'bcryptjs';

export const runtime = "nodejs";  

const handler = NextAuth({
  adapter: PrismaAdapter(prisma),
  // site: process.env.NEXTAUTH_URL || 'http://localhost:3000',
  session: {
    strategy: 'jwt',
    maxAge: 30 * 24 * 60 * 60, // 30 days
  },
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
    CredentialsProvider({
      name: 'credentials',
      credentials: {
        email: { label: 'Email', type: 'text' },
        password: { label: 'Password', type: 'password' },
        action: { label: 'Action', type: 'text' }
      },
      authorize: async (credentials) => {
        if (!credentials?.email || !credentials?.password) return null;
        
        const { email, password, action } = credentials;
        
        if (action === 'register') {
          // Registration logic
          const existingUser = await prisma.user.findFirst({
            where: { email: email }
          });
          
          if (existingUser) return null; // User already exists
          
          // Hash password and create new user
          const passwordHash = await bcrypt.hash(password, 12);
          const newUser = await prisma.user.create({
            data: {
              email: email,
              username: email, // Using email as username for simplicity
              passwordHash: passwordHash,
              emailVerified: new Date(), // Auto-verify for manual registration
            }
          });
          
          return newUser;
        } else {
          // Login logic
          const user = await prisma.user.findUnique({ where: { email: email } });
          if (!user?.passwordHash) return null;
          const ok = await bcrypt.compare(password, user.passwordHash);
          return ok ? user : null;
        }
      },
    }),
  ],
  callbacks: {
    // Put user.id (and other lightweight claims) into the JWT
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        // Example: token.role = (user as any).role ?? "user";
      }
      return token;
    },
    // Expose those claims on session.user for your app to use
    async session({ session, token }) {
      if (session.user) {
        (session.user as any).id = token.id;
        // (session.user as any).role = token.role;
      }
      return session;
    },
  },
});
export { handler as GET, handler as POST };
