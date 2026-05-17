import { useState } from "react";

const API_URL = "https://career-copilot-backend2.onrender.com";

function App() {

  const [resumeText, setResumeText] = useState("");
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  async function analyzeResume() {

    if (!resumeText.trim()) {
      alert("Please paste your resume");
      return;
    }

    setLoading(true);

    try {

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          resume_text: resumeText
        })
      });

      const data = await response.json();

      setAnalysis(data);

    } catch (error) {

      console.error(error);
      alert("Backend connection failed");

    }

    setLoading(false);
  }

  async function uploadResume() {

    if (!selectedFile) {
      alert("Please upload PDF");
      return;
    }

    const formData = new FormData();

    formData.append("file", selectedFile);

    setLoading(true);

    try {

      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData
      });

      const data = await response.json();

      setAnalysis(data);

    } catch (error) {

      console.error(error);
      alert("PDF Upload Failed");

    }

    setLoading(false);
  }

  return (

    <div className="min-h-screen bg-gray-100 p-10">

      <div className="max-w-6xl mx-auto">

        <h1 className="text-5xl font-bold text-center text-blue-700 mb-4">
          AI Career Copilot
        </h1>

        <p className="text-center text-gray-600 text-lg mb-8">
          ATS Resume Analyzer + FAANG Career Mentor
        </p>

        <div className="bg-white p-8 rounded-2xl shadow-lg">

          <textarea
            rows="10"
            placeholder="Paste your resume here..."
            value={resumeText}
            onChange={(e) => setResumeText(e.target.value)}
            className="w-full border rounded-xl p-4 mb-6"
          />

          <div className="flex gap-4 flex-wrap">

            <button
              onClick={analyzeResume}
              className="bg-blue-600 text-white px-6 py-3 rounded-xl"
            >
              Analyze Resume
            </button>

            <input
              type="file"
              accept=".pdf"
              onChange={(e) => setSelectedFile(e.target.files[0])}
            />

            <button
              onClick={uploadResume}
              className="bg-green-600 text-white px-6 py-3 rounded-xl"
            >
              Upload PDF
            </button>

          </div>

        </div>

        {loading && (

          <div className="text-center mt-10 text-2xl font-bold text-purple-700">
            AI is analyzing your resume...
          </div>

        )}

        {analysis && (

          <div className="bg-white p-8 rounded-2xl shadow-lg mt-10">

            <h2 className="text-3xl font-bold text-blue-700 mb-4">
              Predicted Role: {analysis.predicted_role}
            </h2>

            <h2 className="text-2xl font-bold text-green-700 mb-4">
              Resume Score: {analysis.resume_score}/100
            </h2>

            <h2 className="text-2xl font-bold text-purple-700 mb-4">
              ATS Score: {analysis.ats_score}/100
            </h2>

            <h2 className="text-2xl font-bold text-orange-700 mb-8">
              FAANG Readiness: {analysis.faang_readiness}%
            </h2>

            <div className="grid md:grid-cols-2 gap-8">

              <div>

                <h3 className="text-2xl font-semibold mb-4 text-green-600">
                  Strengths
                </h3>

                <ul className="list-disc ml-5">

                  {analysis.strengths?.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}

                </ul>

              </div>

              <div>

                <h3 className="text-2xl font-semibold mb-4 text-red-600">
                  Weaknesses
                </h3>

                <ul className="list-disc ml-5">

                  {analysis.weaknesses?.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}

                </ul>

              </div>

            </div>

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

            <div className="mt-10">

              <h3 className="text-2xl font-semibold mb-4 text-orange-600">
                Missing Skills
              </h3>

              <div className="flex flex-wrap gap-3">

                {analysis.missing_skills?.map((skill, index) => (
                  <span
                    key={index}
                    className="bg-orange-100 text-orange-700 px-4 py-2 rounded-full"
                  >
                    {skill}
                  </span>
                ))}

              </div>

            </div>

            <div className="mt-10">

              <h3 className="text-2xl font-semibold mb-4 text-green-700">
                Personalized Roadmap
              </h3>

              <ul className="list-disc ml-5">

                {analysis.roadmap?.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}

              </ul>

            </div>

            <div className="mt-10">

              <h3 className="text-2xl font-semibold mb-4 text-purple-700">
                Suggestions
              </h3>

              <ul className="list-disc ml-5">

                {analysis.suggestions?.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}

              </ul>

            </div>

            <div className="mt-10 bg-gray-100 p-6 rounded-2xl">

              <h3 className="text-2xl font-semibold mb-4 text-indigo-700">
                AI Career Guidance
              </h3>

              <p className="whitespace-pre-wrap leading-8">
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