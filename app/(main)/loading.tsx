export default function MainLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-paper">
      <div className="text-center">
        <div className="mx-auto h-10 w-10 rounded-full border-2 border-sea border-t-transparent animate-spin" />
        <p className="mt-4 text-sm text-mist font-medium">Loading...</p>
      </div>
    </div>
  );
}
