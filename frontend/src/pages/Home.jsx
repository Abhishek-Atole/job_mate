import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div>
      <section className="bg-gradient-to-br from-blue-50 to-white py-20">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">Find Your Perfect Match</h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            AI-powered job matching that connects talent with opportunity in seconds. 
            Upload your resume and let our smart engine do the rest.
          </p>
          <div className="flex gap-4 justify-center">
            <Link to="/jobs" className="bg-blue-600 text-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-blue-700">Browse Jobs</Link>
            <Link to="/register" className="border-2 border-blue-600 text-blue-600 px-8 py-3 rounded-lg text-lg font-medium hover:bg-blue-50">Get Started</Link>
          </div>
        </div>
      </section>

      <section className="py-12 bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 grid grid-cols-3 gap-8 text-center">
          <div><div className="text-3xl font-bold text-blue-600">10,000+</div><div className="text-gray-500">Jobs Posted</div></div>
          <div><div className="text-3xl font-bold text-blue-600">5,000+</div><div className="text-gray-500">Employers</div></div>
          <div><div className="text-3xl font-bold text-blue-600">95%</div><div className="text-gray-500">Match Accuracy</div></div>
        </div>
      </section>

      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: '1', title: 'Upload Resume', desc: 'Upload your PDF resume and let our AI extract your skills and experience.' },
              { step: '2', title: 'AI Matches', desc: 'Our NLP engine compares your profile against job descriptions to find the best fit.' },
              { step: '3', title: 'Apply & Get Hired', desc: 'Apply to your best-matching jobs and track your application status in real time.' },
            ].map((item) => (
              <div key={item.step} className="text-center p-6">
                <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">{item.step}</div>
                <h3 className="text-xl font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-600">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  )
}
