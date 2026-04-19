import { cookies } from "next/headers";
import { redirect } from "next/navigation";

export default async function Home() {
  const token = (await cookies()).get("med_auth_token")?.value;
  redirect(token ? "/agenda" : "/login");
}
