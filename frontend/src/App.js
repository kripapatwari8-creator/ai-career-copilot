import { useState } from "react";

function App() {

  // =========================
  // STATES
  // =========================

  const [resumeText, setResumeText] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  // =========================
  // ANALYZE TEXT RESUME
  // =========================

  async function analyzeResume() {

    if (!resumeText.trim()) {
      alert("Please paste your resume.");
      return;
    }

    setLoading(true);

    try {

      const response = await fetch(
        "https://career-copilot-backend2.onrender.com",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            resume_text: resumeText
          })
        }
      );

      const data = await response.json();

      setAnalysis(data);

    } catch (error) {

      console.error(error);
      alert("Backend connection failed.");

    }

    setLoading(false);
  }

  // =========================
  // PDF UPLOAD
  // =========================

  async function uploadResume() {

    if (!selectedFile) {
      alert("Please upload a PDF");
      return;
    }

    const formData = new FormData();

    formData.append("file", selectedFile);

    setLoading(true);

    try {

      const response = await fetch(
        "https://career-copilot-backend2.onrender.com/upload",
        {
          method: "POST",
          body: formData
        }
      );

      const data = await response.json();

      setAnalysis(data);

    } catch (error) {

      console.error(error);
      alert("PDF Upload Failed");

    }

    setLoading(false);
  }

  // =========================
  // UI
  // =========================

  return (

    <div className="min-h-screen bg-gray-100 p-10">

      <div className="max-w-6xl mx-auto">

        {/* ========================= */}
        {/* HEADER */}
        {/* ========================= */}

        <h1 className="text-5xl font-bold mb-4 text-center text-blue-700">

          AI Career Copilot

        </h1>

        <p className="text-center text-gray-600 text-lg mb-8">

          AI Powered Resume Analyzer + FAANG Career Mentor

        </p>

        {/* ========================= */}
        {/* INPUT SECTION */}
        {/* ========================= */}

        <div className="bg-white rounded-2xl shadow-lg p-8">

          <textarea
            rows="10"
            placeholder="Paste your resume text here..."
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            className="w-full border rounded-xl p-4 mb-6"
          />

          <div className="flex gap-4 flex-wrap">

            <button
              onClick={analyzeResume}
              className="bg-blue-600 text-white px-6 py-3 rounded-xl hover:bg-blue-700"
            >
              Analyze Text Resume
            </button>

            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setSelectedFile(e.target.files[0])}
              className="border p-2 rounded-lg"
            />

            <button
              onClick={uploadResume}
              className="bg-green-600 text-white px-6 py-3 rounded-xl hover:bg-green-700"
            >
              Upload PDF Resume
            </button>

          </div>

        </div>

        {/* ========================= */}
        {/* LOADING */}
        {/* ========================= */}

        {loading && (

          <div className="text-center mt-10 text-2xl font-semibold text-purple-700">

            AI is analyzing your resume...

          </div>

        )}

        {/* ========================= */}
        {/* ANALYSIS RESULTS */}
        {/* ========================= */}

        {analysis && (

          <div className="bg-white mt-10 rounded-2xl shadow-lg p-8">

            {/* ========================= */}
            {/* ROLE */}
            {/* ========================= */}

            <h2 className="text-3xl font-bold mb-4 text-purple-700">

              Predicted Role: {analysis.predicted_role}

            </h2>

            {/* ========================= */}
            {/* RESUME SCORE */}
            {/* ========================= */}

            <h2 className="text-3xl font-bold mb-4 text-blue-700">

              Resume Score: {analysis.resume_score}/100

            </h2>

            <div className="w-full bg-gray-200 rounded-full h-6 mb-8">

              <div
                className="bg-blue-600 h-6 rounded-full"
                style={{
                  width: `${analysis.resume_score}%`
                }}
              ></div>

            </div>

            {/* ========================= */}
            {/* FAANG READINESS */}
            {/* ========================= */}

            <h2 className="text-3xl font-bold mb-8 text-green-700">

              FAANG Readiness: {analysis.faang_readiness}%

            </h2>

            {/* ========================= */}
            {/* STRENGTHS + WEAKNESSES */}
            {/* ========================= */}

            <div className="grid md:grid-cols-2 gap-8">

              {/* STRENGTHS */}

              <div>

                <h3 className="text-2xl font-semibold mb-4 text-green-600">

                  Strengths

                </h3>

                <ul className="list-disc ml-5 space-y-2">

                  {analysis.strengths?.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}

                </ul>

              </div>

              {/* WEAKNESSES */}

              <div>

                <h3 className="text-2xl font-semibold mb-4 text-red-600">

                  Weaknesses

                </h3>

                <ul className="list-disc ml-5 space-y-2">

                  {analysis.weaknesses?.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}

                </ul>

              </div>

            </div>

            {/* ========================= */}
            {/* FOUND SKILLS */}
            {/* ========================= */}

            <div className="mt-10">

              <h3 className="text-2xl font-semibold mb-4 text-blue-600">

                Found Skills

              </h3>

              <div className="flex flex-wrap gap-3">

                {analysis.found_skills?.map((skill, index) => (

                  <span
                    key={index}
                    className="bg-blue-100 text-blue-700 px-4 py-2 rounded-full"
                  >

                    {skill}

                  </span>

                ))}

              </div>

            </div>

            {/* ========================= */}
            {/* MISSING FAANG SKILLS */}
            {/* ========================= */}

            <div className="mt-10">

              <h3 className="text-2xl font-semibold mb-4 text-orange-600">

                Missing FAANG Skills

              </h3>

              <div className="flex flex-wrap gap-3">

                {analysis.missing_faang_skills?.map((skill, index) => (

                  <span
                    key={index}
                    className="bg-orange-100 text-orange-700 px-4 py-2 rounded-full"
                  >

                    {skill}

                  </span>

                ))}

              </div>

            </div>

            {/* ========================= */}
            {/* ROADMAP */}
            {/* ========================= */}

            <div className="mt-10">

              <h3 className="text-2xl font-semibold mb-4 text-green-700">

                Personalized Learning Roadmap

              </h3>

              <ul className="list-disc ml-5 space-y-2">

                {analysis.roadmap?.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}

              </ul>

            </div>

            {/* ========================= */}
            {/* SUGGESTIONS */}
            {/* ========================= */}

            <div className="mt-10">

              <h3 className="text-2xl font-semibold mb-4 text-purple-600">

                Suggestions

              </h3>

              <ul className="list-disc ml-5 space-y-2">

                {analysis.suggestions?.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}

              </ul>

            </div>

            {/* ========================= */}
            {/* AI FEEDBACK */}
            {/* ========================= */}

            <div className="mt-10 bg-gray-100 rounded-2xl p-6">

              <h3 className="text-2xl font-semibold mb-4 text-indigo-700">

                AI Career Guidance

              </h3>

              <p className="whitespace-pre-wrap leading-8 text-gray-800">

                {analysis.ai_feedback}

              </p>

            </div>

          </div>

        )}

      </div>

    </div>
  );
}

export default App;