export default function NotFound() {
    return (
        <main className="min-h-screen bg-slate-100 px-4 py-4 text-slate-900 sm:px-6 sm:py-6">
            <div className="mx-auto flex min-h-[calc(100vh-2rem)] max-w-4xl items-center justify-center sm:min-h-[calc(100vh-3rem)]">
                <section className="w-full rounded-3xl border border-slate-200 bg-white p-6 text-center shadow-sm sm:p-8">
                    <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-700">
                        Skill Synapse
                    </p>
                    <h1 className="mt-3 text-3xl font-bold tracking-tight sm:text-4xl">
                        Page not found
                    </h1>
                    <p className="mt-3 text-sm leading-6 text-slate-600 sm:text-base">
                        The page you are looking for does not exist.
                    </p>
                    <Link
                        to="/"
                        className="mt-6 inline-flex rounded-2xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-600 focus:outline-none focus:ring-4 focus:ring-sky-200"
                    >
                        Back to home
                    </Link>
                </section>
            </div>
        </main>
    );
}
