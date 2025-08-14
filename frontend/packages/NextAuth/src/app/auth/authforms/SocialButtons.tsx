"use client";
import React from "react";
import Google from "/public/images/svgs/google-icon.svg";
import Git from "/public/images/svgs/git-icon.svg";
import Image from "next/image";
import { Button, HR, HRText} from "flowbite-react";
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
          color={"transparent"}
          onClick={handleGoogleSignIn}
          className="border border-ld flex gap-2 items-enter w-full rounded-md text-center justify-center  hover:bg-transparent !h-11 font-normal text-ld"
        >
          <Image src={Google} alt="google" height={18} width={18} /> With Google
        </Button>
        <Button
          color={"transparent"}
          onClick={handleGithubSignIn}
          className="border border-ld flex gap-2 items-enter w-full rounded-md text-center justify-center hover:bg-transparent !h-11 font-normal text-ld"
        >
          <Image src={Git} alt="google" height={18} width={18} />
          With Github
        </Button>
      </div>
      {/* Divider */}
      <HRText
        text={`${title}`}
        className="!border-t !border-ld !bg-transparent"
      />
    </>
  );
};

export default SocialButtons;
