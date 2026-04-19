export default function LoginPage() {
  return (
    <section className="mx-auto mt-12 w-full max-w-md rounded-lg border border-slate-800 bg-slate-900 p-6">
      <h2 className="mb-4 text-xl font-semibold">Login</h2>
      <form className="space-y-3">
        <label className="block text-sm text-slate-300">
          Email
          <input
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2"
            placeholder="analyst@helix.ai"
            type="email"
          />
        </label>
        <label className="block text-sm text-slate-300">
          Password
          <input
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-3 py-2"
            placeholder="••••••••"
            type="password"
          />
        </label>
        <button
          className="w-full rounded bg-cyan-500 px-3 py-2 font-medium text-slate-950"
          type="button"
        >
          Sign In
        </button>
      </form>
    </section>
  )
}
