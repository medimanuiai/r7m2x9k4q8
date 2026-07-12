import { redirect } from "next/navigation";

export default function Home() {
  // Redirect to the auth register page to avoid a root 404
  redirect("/register");
}
