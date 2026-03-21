import { Link, useLocation } from "react-router";
import {
    PolarAngleAxis,
    PolarGrid,
    PolarRadiusAxis,
    Radar,
    RadarChart,
    ResponsiveContainer,
    Tooltip,
} from "recharts";
import { FiArrowLeft, FiAward, FiTarget, FiTrendingUp } from "react-icons/fi";

const sampleEvaluationResult = {
    all_skills: {
        Python: {
            score: 8.2,
            difficulty: 2,
            time: "2 weeks",
            unlock_power: 10,
        },
        Docker: {
            score: 5.2,
            difficulty: 6,
            time: "2 weeks",
            unlock_power: 3,
        },
    },
};

function CustomTooltip({ active, payload }) {
    if (!active || !payload?.length) {
        return null;
    }

    const skill = payload[0].payload;

    return (
        <div className="rounded-2xl border border-slate-200 bg-white px-4 py-3 shadow-xl">
            <p className="text-sm font-semibold text-slate-900">{skill.skill}</p>
            <p className="mt-2 text-sm text-slate-600">Score: {skill.score}/10</p>
            <p className="text-sm text-slate-600">
                Difficulty: {skill.difficulty}/10
            </p>
            <p className="text-sm text-slate-600">Time: {skill.time}</p>
            <p className="text-sm text-slate-600">
                Unlock power: {skill.unlockPower}/10
            </p>
        </div>
    );
}

export default function Evaluate() {
    const { state } = useLocation();
    const evaluationResult =
        state?.evaluationResult && Object.keys(state.evaluationResult).length
            ? state.evaluationResult
            : sampleEvaluationResult;

    const skills = Object.entries(evaluationResult.all_skills ?? {}).map(
        ([skill, details]) => ({
            skill,
            score: Number(details.score ?? 0),
            difficulty: Number(details.difficulty ?? 0),
            time: details.time ?? "Unknown",
            unlockPower: Number(details.unlock_power ?? 0),
        }),
    );

    const averageScore = skills.length
        ? (
              skills.reduce((total, skill) => total + skill.score, 0) /
              skills.length
          ).toFixed(1)
        : "0.0";

    const strongestSkill = skills.reduce(
        (best, skill) => (skill.score > best.score ? skill : best),
        skills[0] ?? { skill: "None", score: 0 },
    );

    return (
        <main className="min-h-screen bg-[radial-gradient(circle_at_top,_#eff6ff,_#e2e8f0_40%,_#0f172a_140%)] px-4 py-6 text-slate-900 sm:px-6">
            <div className="mx-auto flex max-w-7xl flex-col gap-6">
                <header className="rounded-[2rem] border border-white/60 bg-white/75 p-6 shadow-xl shadow-slate-900/5 backdrop-blur sm:p-8">
                    <div className="flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
                        <div className="max-w-2xl">
                            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-sky-700">
                                Skill Synapse
                            </p>
                            <h1 className="mt-3 font-serif text-4xl font-semibold tracking-tight text-slate-950 sm:text-5xl">
                                Skill Match Radar
                            </h1>
                            <p className="mt-4 text-sm leading-7 text-slate-600 sm:text-base">
                                Your submitted resume has been translated into a
                                skill profile. Each spoke represents a skill, and
                                the radar surface shows how strongly it matches
                                the current job requirements.
                            </p>
                        </div>

                        <Link
                            to="/"
                            className="inline-flex items-center gap-2 self-start rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-semibold text-slate-700 transition hover:border-sky-300 hover:text-sky-700"
                        >
                            <FiArrowLeft className="text-base" />
                            Back to upload
                        </Link>
                    </div>
                </header>

                <section className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
                    <article className="rounded-[2rem] border border-slate-200/70 bg-white/85 p-4 shadow-xl shadow-slate-900/5 backdrop-blur sm:p-6">
                        <div className="mb-5 flex items-center justify-between gap-4">
                            <div>
                                <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-700">
                                    Radar View
                                </p>
                                <h2 className="mt-2 text-2xl font-semibold tracking-tight text-slate-950">
                                    Score by skill
                                </h2>
                            </div>
                            <div className="rounded-full bg-sky-50 px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-sky-700">
                                {skills.length} skills plotted
                            </div>
                        </div>

                        <div className="h-[420px] w-full rounded-[1.5rem] bg-[linear-gradient(180deg,_rgba(248,250,252,0.95),_rgba(239,246,255,0.88))] p-4">
                            <ResponsiveContainer width="100%" height="100%">
                                <RadarChart
                                    data={skills}
                                    outerRadius="72%"
                                >
                                    <PolarGrid
                                        gridType="polygon"
                                        stroke="#cbd5e1"
                                    />
                                    <PolarAngleAxis
                                        dataKey="skill"
                                        tick={{
                                            fill: "#0f172a",
                                            fontSize: 13,
                                            fontWeight: 600,
                                        }}
                                    />
                                    <PolarRadiusAxis
                                        domain={[0, 10]}
                                        tickCount={6}
                                        tick={{
                                            fill: "#64748b",
                                            fontSize: 11,
                                        }}
                                        axisLine={false}
                                    />
                                    <Tooltip content={<CustomTooltip />} />
                                    <Radar
                                        name="Match Score"
                                        dataKey="score"
                                        stroke="#0ea5e9"
                                        fill="#38bdf8"
                                        fillOpacity={0.4}
                                        strokeWidth={3}
                                    />
                                </RadarChart>
                            </ResponsiveContainer>
                        </div>
                    </article>

                    <aside className="grid gap-4">
                        <section className="rounded-[2rem] border border-slate-200/70 bg-slate-950 p-6 text-white shadow-xl shadow-slate-900/10">
                            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-300">
                                Snapshot
                            </p>
                            <div className="mt-5 grid gap-4">
                                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                                    <div className="flex items-center gap-3">
                                        <div className="rounded-2xl bg-sky-400/15 p-3 text-sky-300">
                                            <FiTrendingUp className="text-lg" />
                                        </div>
                                        <div>
                                            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                                                Average score
                                            </p>
                                            <p className="mt-1 text-2xl font-semibold">
                                                {averageScore}/10
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                                    <div className="flex items-center gap-3">
                                        <div className="rounded-2xl bg-emerald-400/15 p-3 text-emerald-300">
                                            <FiAward className="text-lg" />
                                        </div>
                                        <div>
                                            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                                                Strongest skill
                                            </p>
                                            <p className="mt-1 text-2xl font-semibold">
                                                {strongestSkill.skill}
                                            </p>
                                            <p className="text-sm text-slate-300">
                                                {strongestSkill.score}/10 match
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                                    <div className="flex items-center gap-3">
                                        <div className="rounded-2xl bg-amber-400/15 p-3 text-amber-300">
                                            <FiTarget className="text-lg" />
                                        </div>
                                        <div>
                                            <p className="text-xs uppercase tracking-[0.2em] text-slate-400">
                                                Readiness
                                            </p>
                                            <p className="mt-1 text-2xl font-semibold">
                                                {Number(averageScore) >= 7
                                                    ? "Strong"
                                                    : Number(averageScore) >= 5
                                                      ? "Promising"
                                                      : "Needs work"}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </section>

                        <section className="rounded-[2rem] border border-slate-200/70 bg-white/85 p-6 shadow-xl shadow-slate-900/5 backdrop-blur">
                            <p className="text-sm font-semibold uppercase tracking-[0.24em] text-sky-700">
                                Skill Breakdown
                            </p>
                            <div className="mt-5 grid gap-3">
                                {skills.map((skill) => (
                                    <article
                                        key={skill.skill}
                                        className="rounded-3xl border border-slate-200 bg-slate-50/80 p-4"
                                    >
                                        <div className="flex items-start justify-between gap-3">
                                            <div>
                                                <h3 className="text-lg font-semibold text-slate-900">
                                                    {skill.skill}
                                                </h3>
                                                <p className="mt-1 text-sm text-slate-500">
                                                    Time estimate: {skill.time}
                                                </p>
                                            </div>
                                            <div className="rounded-full bg-slate-900 px-3 py-1 text-sm font-semibold text-white">
                                                {skill.score}/10
                                            </div>
                                        </div>

                                        <div className="mt-4 grid grid-cols-2 gap-3 text-sm text-slate-600">
                                            <div className="rounded-2xl bg-white px-3 py-2">
                                                Difficulty: {skill.difficulty}/10
                                            </div>
                                            <div className="rounded-2xl bg-white px-3 py-2">
                                                Unlock power: {skill.unlockPower}/10
                                            </div>
                                        </div>
                                    </article>
                                ))}
                            </div>
                        </section>
                    </aside>
                </section>
            </div>
        </main>
    );
}
