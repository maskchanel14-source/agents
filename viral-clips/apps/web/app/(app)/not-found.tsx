import Link from "next/link";

export default function NotFound() {
  return (
    <div className="grid min-h-[50vh] place-items-center">
      <div className="card p-8 text-center">
        <p className="text-3xl font-semibold">404</p>
        <p className="mt-2 text-sm text-mist-500">That project or clip does not exist, or belongs to another account.</p>
        <Link href="/dashboard" className="btn-primary mt-4">
          Back to dashboard
        </Link>
      </div>
    </div>
  );
}
