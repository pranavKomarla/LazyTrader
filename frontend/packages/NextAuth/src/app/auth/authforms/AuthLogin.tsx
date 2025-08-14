"use client";
import { Alert, Button, Checkbox, Label, TextInput } from "flowbite-react";
import Link from "next/link";
import React, { useState } from "react";
import { loginType } from "@/app/(DashboardLayout)/types/auth/auth";
import { signIn, useSession } from "next-auth/react";
import { redirect } from "next/navigation";
import { Icon } from "@iconify/react";
const AuthLogin = ({ title, subtitle, subtext }: loginType) => {
  const { data: session } = useSession();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    const result = await signIn("credentials", {
      redirect: false,
      username,
      password,
    });
    if (result?.error) {
      // Handle successful sign-in
      setError(result.error);
    }
  };
  if (session) {
    return redirect("/");
  }
  return (
    <>
      {title ? <p>{title}</p> : null}

      {subtext}
      {error ? (
        <div className="mt-4">
          <Alert
            color={"lighterror"}
            icon={() => (
              <Icon
                icon="solar:info-circle-outline"
                className="me-3"
                height={20}
              />
            )}
          >
            Sign-in error: Username or Password is Wrong
          </Alert>
        </div>
      ) : (
        ""
      )}

      <form onSubmit={handleSubmit} className="mt-6">
        <div className="mb-4">
          <div className="mb-2 block">
            <Label htmlFor="Username" value="Username" />
          </div>
          <TextInput
            id="Username"
            type="text"
            sizing="md"
            value={username}
            className={`form-control ${ error !== "" ? 'error-border' : '' }`}
            onChange={(e) => setUsername(e.target.value)}
          />
        </div>
        <div className="mb-4">
          <div className="mb-2 block">
            <Label htmlFor="password" value="Password" />
          </div>
          <TextInput
            id="password"
            type="password"
            sizing="md"
            className={`form-control ${ error !== "" ? 'error-border' : '' }`}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>
        <div className="flex justify-between my-5">
          <div className="flex items-center gap-2">
            <Checkbox id="accept" className="checkbox" />
            <Label
              htmlFor="accept"
              className="opacity-90 font-normal cursor-pointer"
            >
              Remember this Device
            </Label>
          </div>
          <Link href={"/"} className="text-primary text-sm font-medium">
            Forgot Password ?
          </Link>
        </div>
        <Button color={"primary"} type="submit" className=" w-full">
          Sign in
        </Button>
      </form>

      {subtitle}
    </>
  );
};

export default AuthLogin;
