import { ArrowRight, Heart, Activity, TrendingUp, Shield, Users, Sparkles } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 via-cyan-50 to-blue-50">
      {/* Navigation */}
      <nav className="bg-white/95 backdrop-blur-lg border-b border-slate-200/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Heart className="w-8 h-8 text-emerald-500" />
              <span className="text-2xl font-bold bg-gradient-to-r from-emerald-600 to-cyan-600 bg-clip-text text-transparent">
                VitaNexus
              </span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-slate-600 hover:text-emerald-600 font-medium transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-slate-600 hover:text-emerald-600 font-medium transition-colors">
                How It Works
              </a>
              <a href="#pricing" className="text-slate-600 hover:text-emerald-600 font-medium transition-colors">
                Pricing
              </a>
              <Link
                to="/dashboard"
                className="bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2 rounded-xl font-semibold transition-all shadow-lg hover:shadow-xl"
              >
                Member Login
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center space-x-2 bg-emerald-100 text-emerald-700 px-4 py-2 rounded-full text-sm font-medium">
              <Sparkles className="w-4 h-4" />
              <span>Health Assurance Cooperative</span>
            </div>

            <h1 className="text-5xl lg:text-6xl font-bold tracking-tight text-slate-900 leading-tight">
              Your Health Score.
              <br />
              <span className="bg-gradient-to-r from-emerald-600 to-cyan-600 bg-clip-text text-transparent">
                Your Savings.
              </span>
              <br />
              Your Control.
            </h1>

            <p className="text-2xl font-light text-slate-600 leading-relaxed">
              Know your health before it becomes healthcare. Get rewarded for staying healthy with our AI-powered cooperative model.
            </p>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                to="/dashboard"
                className="inline-flex items-center justify-center space-x-2 bg-emerald-500 hover:bg-emerald-600 text-white px-8 py-4 rounded-xl text-lg font-semibold shadow-lg hover:shadow-xl transition-all"
              >
                <span>Start Your Health Journey</span>
                <ArrowRight className="w-5 h-5" />
              </Link>
              <button className="inline-flex items-center justify-center space-x-2 bg-white/80 backdrop-blur-sm border-2 border-slate-200 hover:border-emerald-500 text-slate-700 hover:text-emerald-600 px-8 py-4 rounded-xl text-lg font-semibold transition-all">
                Watch Demo
              </button>
            </div>

            <div className="flex items-center space-x-8 pt-4">
              <div>
                <div className="text-3xl font-bold text-slate-900">98%</div>
                <div className="text-sm font-medium text-slate-500">Member Satisfaction</div>
              </div>
              <div className="w-px h-12 bg-slate-300"></div>
              <div>
                <div className="text-3xl font-bold text-slate-900">$2.4k</div>
                <div className="text-sm font-medium text-slate-500">Avg. Annual Savings</div>
              </div>
              <div className="w-px h-12 bg-slate-300"></div>
              <div>
                <div className="text-3xl font-bold text-slate-900">24/7</div>
                <div className="text-sm font-medium text-slate-500">Health Monitoring</div>
              </div>
            </div>
          </div>

          {/* Hero Graphic - Health Score Card */}
          <div className="relative">
            <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl p-10 text-white shadow-2xl transform hover:scale-105 transition-all">
              <div className="flex items-start justify-between mb-8">
                <div>
                  <div className="text-sm font-light opacity-90 mb-2">Your Health Score</div>
                  <div className="text-7xl font-bold">87</div>
                  <div className="text-xl font-light opacity-90 mt-2">Low Risk</div>
                </div>
                <div className="bg-white/20 backdrop-blur-sm px-4 py-2 rounded-full text-sm font-medium">
                  +5 this week
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mt-8">
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                  <Activity className="w-6 h-6 mb-2 opacity-90" />
                  <div className="text-2xl font-bold">12.5k</div>
                  <div className="text-xs opacity-75">steps/day</div>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                  <Heart className="w-6 h-6 mb-2 opacity-90" />
                  <div className="text-2xl font-bold">68</div>
                  <div className="text-xs opacity-75">bpm avg</div>
                </div>
                <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4">
                  <TrendingUp className="w-6 h-6 mb-2 opacity-90" />
                  <div className="text-2xl font-bold">$320</div>
                  <div className="text-xs opacity-75">saved</div>
                </div>
              </div>

              <div className="mt-8 bg-white/10 backdrop-blur-sm rounded-xl p-4">
                <div className="text-sm opacity-90 mb-2">Next Recommended Action</div>
                <div className="font-semibold">Complete your annual checkup to unlock $50 reward</div>
              </div>
            </div>

            {/* Floating badges */}
            <div className="absolute -top-4 -right-4 bg-white rounded-2xl shadow-xl p-4 animate-pulse">
              <div className="flex items-center space-x-2">
                <Shield className="w-5 h-5 text-emerald-500" />
                <span className="text-sm font-semibold text-slate-900">HIPAA Compliant</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-semibold text-slate-900 mb-4">
            Proactive Health, Powered by AI
          </h2>
          <p className="text-xl font-light text-slate-600 max-w-2xl mx-auto">
            Precision health insights that save you money and keep you healthy
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, idx) => (
            <div
              key={idx}
              className="bg-white/80 backdrop-blur-md rounded-2xl p-8 border border-slate-200/50 shadow-xl hover:shadow-2xl hover:scale-105 transition-all"
            >
              <div className={`w-14 h-14 ${feature.iconBg} rounded-xl flex items-center justify-center mb-6`}>
                <feature.icon className={`w-7 h-7 ${feature.iconColor}`} />
              </div>
              <h3 className="text-2xl font-semibold text-slate-900 mb-4">
                {feature.title}
              </h3>
              <p className="text-lg font-light text-slate-600 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="bg-white/60 backdrop-blur-sm py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-semibold text-slate-900 mb-4">
              How VitaNexus Works
            </h2>
            <p className="text-xl font-light text-slate-600">
              Three simple steps to better health and more savings
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-12">
            {steps.map((step, idx) => (
              <div key={idx} className="relative">
                <div className="text-center">
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-cyan-500 text-white text-2xl font-bold mb-6 shadow-lg">
                    {idx + 1}
                  </div>
                  <h3 className="text-xl font-semibold text-slate-900 mb-3">
                    {step.title}
                  </h3>
                  <p className="text-base font-light text-slate-600">
                    {step.description}
                  </p>
                </div>
                {idx < steps.length - 1 && (
                  <div className="hidden md:block absolute top-8 left-full w-full h-0.5 bg-gradient-to-r from-emerald-200 to-cyan-200 transform -translate-x-1/2"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-3xl p-12 text-center text-white shadow-2xl">
          <h2 className="text-4xl font-bold mb-4">
            Ready to Transform Your Health?
          </h2>
          <p className="text-xl font-light opacity-90 mb-8 max-w-2xl mx-auto">
            Join thousands of members who are taking control of their health and saving money with VitaNexus
          </p>
          <Link
            to="/dashboard"
            className="inline-flex items-center space-x-2 bg-white text-emerald-600 px-8 py-4 rounded-xl text-lg font-semibold shadow-lg hover:shadow-xl hover:scale-105 transition-all"
          >
            <span>Get Started Today</span>
            <ArrowRight className="w-5 h-5" />
          </Link>
          <p className="mt-6 text-sm opacity-75">
            No credit card required • 30-day free trial • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <Heart className="w-6 h-6 text-emerald-400" />
                <span className="text-xl font-bold">VitaNexus</span>
              </div>
              <p className="text-sm text-slate-400 font-light">
                Health Assurance Cooperative
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-emerald-400 transition-colors">Features</a></li>
                <li><a href="#" className="hover:text-emerald-400 transition-colors">Pricing</a></li>
                <li><a href="#" className="hover:text-emerald-400 transition-colors">Security</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Company</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-emerald-400 transition-colors">About</a></li>
                <li><a href="#" className="hover:text-emerald-400 transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-emerald-400 transition-colors">Careers</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li><a href="#" className="hover:text-emerald-400 transition-colors">Privacy</a></li>
                <li><a href="#" className="hover:text-emerald-400 transition-colors">Terms</a></li>
                <li><a href="#" className="hover:text-emerald-400 transition-colors">HIPAA</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 mt-12 pt-8 text-center text-sm text-slate-400">
            <p>&copy; 2025 VitaNexus Health Assurance Cooperative. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

const features = [
  {
    icon: Activity,
    iconBg: 'bg-emerald-100',
    iconColor: 'text-emerald-600',
    title: 'AI Health Scoring',
    description: 'Real-time health risk assessment powered by machine learning and your wearable data.',
  },
  {
    icon: Heart,
    iconBg: 'bg-pink-100',
    iconColor: 'text-pink-600',
    title: 'Wearable Integration',
    description: 'Seamlessly sync with Apple Watch, Fitbit, Garmin, and other popular devices.',
  },
  {
    icon: TrendingUp,
    iconBg: 'bg-cyan-100',
    iconColor: 'text-cyan-600',
    title: 'Financial Rewards',
    description: '70/30 profit split means staying healthy literally saves you money.',
  },
  {
    icon: Shield,
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    title: 'HIPAA Compliant',
    description: 'Bank-grade encryption and security. Your health data is always private.',
  },
  {
    icon: Users,
    iconBg: 'bg-violet-100',
    iconColor: 'text-violet-600',
    title: 'Cooperative Model',
    description: 'Join a community where better health outcomes benefit everyone.',
  },
  {
    icon: Sparkles,
    iconBg: 'bg-amber-100',
    iconColor: 'text-amber-600',
    title: 'Personalized Insights',
    description: 'Get custom recommendations based on your unique health profile.',
  },
];

const steps = [
  {
    title: 'Connect Your Devices',
    description: 'Link your Apple Watch, Fitbit, or other wearable to start tracking your health metrics automatically.',
  },
  {
    title: 'Get Your Health Score',
    description: 'Our AI analyzes your data to calculate a real-time health score and identify opportunities.',
  },
  {
    title: 'Earn & Save',
    description: 'Follow personalized recommendations, hit health goals, and watch your savings grow with our 70/30 model.',
  },
];
