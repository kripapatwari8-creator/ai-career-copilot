import { useState } from "react";

      <div className="max-w-6xl mx-auto">

        {/* HEADER */}

        <h1 className="text-5xl font-bold mb-4 text-center text-blue-700">
          AI Career Copilot
        </h1>

        <p className="text-center text-gray-600 text-lg mb-8">
          AI Powered Resume Analyzer + ATS Checker + FAANG Mentor
        </p>

        {/* INPUT */}

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
        {/* LOADING */}
            <div className="grid md:grid-cols-2 gap-8">

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

            {/* FOUND SKILLS */}

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
{/* MISSING SKILLS */}
                    className="bg-green-100 border-l-4 border-green-600 p-4 rounded-xl"
                  >
                    <span className="font-bold mr-2">
                      Step {index + 1}:
                    </span>
                    {item}
                  </div>

                ))}

              </div>

            </div>

            {/* SUGGESTIONS */}

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

            {/* AI FEEDBACK */}

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