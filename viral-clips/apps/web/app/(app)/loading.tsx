export default function Loading() {
  return (
    <div className="space-y-4">
      <div className="skeleton h-8 w-64" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {[0, 1, 2, 3].map((i) => (
          <div key={i} className="skeleton h-28 w-full" />
        ))}
      </div>
      <div className="skeleton h-64 w-full" />
    </div>
  );
}
