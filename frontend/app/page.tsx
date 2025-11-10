import React from 'react'; // Switched to generic React import for compatibility
import Image from 'next/image';

export default function Home() {
  // Define color palette based on Tailwind defaults for Navy, Blue, and White
  const primaryBlue = 'bg-blue-700 hover:bg-blue-800';
  const deepNavyText = 'text-gray-900'; // For contrast and professionalism

  return (
    <main className="min-h-screen">
      <div className="relative isolate pt-14 lg:pt-0">
        
        {/* Hero Section Container */}
        <div className="container mx-auto px-4 py-20 sm:py-24 lg:py-32">
          <div className="max-w-4xl mx-auto text-center">
            
            {/* Logo/Icon placeholder for visual interest */}
            <div className="mx-auto w-12 h-12 rounded-xl flex items-center justify-center mb-4">
                <Image
                  src="/images/icon.png"
                  alt="Digital Mentorship Log"
                  width={48}
                  height={48}
                  className="w-12 h-12"
                />
            </div>

            {/* Title */}
            <h1 className={`text-5xl md:text-6xl font-extrabold ${deepNavyText} mb-4 tracking-tight`}>
              Digital Mentorship Log
            </h1>
            
            {/* Description */}
            <p className="text-xl text-gray-600 mb-10 max-w-2xl mx-auto">
              Streamline mentorship activities, track facility performance, and enhance healthcare delivery
            </p>

            {/* Call to Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {/* Primary Button: Deep Blue Fill - Fixed to use standard <a> tag */}
              <a 
                href="/auth/login" 
                className={`
                  inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-semibold rounded-xl shadow-lg 
                  text-white ${primaryBlue} transition duration-300 transform hover:scale-[1.02] disabled:opacity-50
                `}
              >
                Get Started
              </a>
              
              {/* Secondary Button: Outline Blue - Fixed to use standard <a> tag */}
              <a 
                href="/auth/login" 
                className={`
                  inline-flex items-center justify-center px-8 py-3 text-base font-semibold rounded-xl 
                  border-2 border-blue-700 text-blue-700 bg-white hover:bg-blue-50 transition duration-300
                `}
              >
                Sign In
              </a>
            </div>
          </div>
        </div>

        {/* Feature Cards Section */}
        <div className="container mx-auto px-4 pb-20 sm:pb-24 lg:pb-32">
          <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8 pt-8">
            
            {/* Card 1: Plan Visits */}
            <div className="bg-white p-8 rounded-2xl shadow-xl border-t-4 border-blue-700 transition duration-300 hover:shadow-2xl hover:scale-[1.02]">
              <div className="text-3xl mb-4 p-3 inline-flex bg-blue-50 rounded-lg">📝</div>
              <h3 className={`text-xl font-bold ${deepNavyText} mb-3`}>Plan Visits</h3>
              <p className="text-gray-600">
                Schedule and plan mentorship visits with clear objectives
              </p>
            </div>

            {/* Card 2: Track Progress */}
            <div className="bg-white p-8 rounded-2xl shadow-xl border-t-4 border-blue-700 transition duration-300 hover:shadow-2xl hover:scale-[1.02]">
              <div className="text-3xl mb-4 p-3 inline-flex bg-blue-50 rounded-lg">📊</div>
              <h3 className={`text-xl font-bold ${deepNavyText} mb-3`}>Track Progress</h3>
              <p className="text-gray-600">
                Monitor facility performance and identify areas for improvement
              </p>
            </div>

            {/* Card 3: Follow-Up Actions */}
            <div className="bg-white p-8 rounded-2xl shadow-xl border-t-4 border-blue-700 transition duration-300 hover:shadow-2xl hover:scale-[1.02]">
              <div className="text-3xl mb-4 p-3 inline-flex bg-blue-50 rounded-lg">✅</div>
              <h3 className={`text-xl font-bold ${deepNavyText} mb-3`}>Follow-Up Actions</h3>
              <p className="text-gray-600">
                Manage action items and ensure continuous improvement
              </p>
            </div>
          </div>
        </div>

      </div>
    </main>
  )
}
