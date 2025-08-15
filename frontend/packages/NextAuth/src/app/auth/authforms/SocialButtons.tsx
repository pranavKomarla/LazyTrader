"use client";
import React from "react";
import Google from "/public/images/svgs/google-icon.svg";
import Git from "/public/images/svgs/git-icon.svg";
import Image from "next/image";
import { Button, HR } from "flowbite-react";
import { signInType } from "@/app/(DashboardLayout)/types/auth/auth";
import { signIn } from "next-auth/react";

interface MyAppProps {
  title?: string;
}

const SocialButtons: React.FC<MyAppProps> = ({ title }: signInType) => {
  const handleGoogleSignIn = async () => {
    await signIn("google");
  };
  const handleGithubSignIn = async () => {
    await signIn("github");
  };
  return (
    <>
      <div className="flex justify-between gap-8 my-6 ">
        <Button
          color="light"
          onClick={handleGoogleSignIn}
          className="border border-gray-300 flex gap-2 items-center w-full rounded-md text-center justify-center hover:bg-gray-50 h-11 font-normal text-gray-700"
        >
          <Image src={Google} alt="google" height={18} width={18} /> With Google
        </Button>
        <Button
          color="light"
          onClick={handleGithubSignIn}
          className="border border-gray-300 flex gap-2 items-center w-full rounded-md text-center justify-center hover:bg-gray-50 h-11 font-normal text-gray-700"
        >
          <Image src={Git} alt="google" height={18} width={18} />
          With Github
        </Button>
      </div>
      {/* Divider */}
      <div className="relative my-6">
        <HR className="border-t border-gray-300" />
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="bg-white px-4 text-sm text-gray-500">{title}</span>
        </div>
      </div>
    </>
  );
};

export default SocialButtons;
