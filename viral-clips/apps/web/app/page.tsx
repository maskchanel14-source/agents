import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { COOKIE_NAME } from "@/lib/api";

export default async function Home() {
  const store = await cookies();
  redirect(store.get(COOKIE_NAME)?.value ? "/dashboard" : "/login");
}
