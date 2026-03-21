export default function Loading() {
    return (
        <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-slate-950 px-6 text-white">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(56,189,248,0.24),transparent_45%),radial-gradient(circle_at_bottom,rgba(14,165,233,0.18),transparent_35%)]" />

            <section className="relative flex w-full max-w-sm flex-col items-center rounded-3xl border border-white/10 bg-white/5 px-8 py-10 text-center shadow-2xl shadow-sky-950/30 backdrop-blur">
                <div className="relative flex h-24 w-24 items-center justify-center">
                    <span className="absolute h-24 w-24 animate-ping rounded-full bg-sky-400/20" />
                    <span className="absolute h-18 w-18 rounded-full border border-sky-300/30" />
                    <span className="h-12 w-12 animate-spin rounded-full border-4 border-sky-200/20 border-t-sky-400" />
                </div>

                <p className="mt-8 text-xs font-semibold uppercase tracking-[0.35em] text-sky-300">
                    Skill Synapse
                </p>
                <h1 className="mt-3 text-2xl font-semibold tracking-tight">
                    Loading your workspace
                </h1>
                <p className="mt-3 text-sm leading-6 text-slate-300">
                    Preparing your results and getting everything ready.
                </p>
            </section>
        </main>
    );
}
