"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Database, Sparkles, Zap, Shield } from "lucide-react";
import { isAuthenticated } from "@/lib/auth";

export default function HomePage() {
  const [isAuth, setIsAuth] = useState(false);

  useEffect(() => {
    setIsAuth(isAuthenticated());
  }, []);

  return (
    <div className="relative overflow-x-hidden">
      {/* Hero Section */}
      <section className="min-h-screen flex items-center justify-center relative overflow-hidden pt-16 sm:pt-20">
        {/* Ambient Background */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-48 sm:w-96 h-48 sm:h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" />
          <div className="absolute top-1/3 right-1/4 w-48 sm:w-96 h-48 sm:h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" style={{ animationDelay: "2s" }} />
          <div className="absolute bottom-1/4 left-1/3 w-48 sm:w-96 h-48 sm:h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" style={{ animationDelay: "4s" }} />
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 grid lg:grid-cols-2 gap-6 sm:gap-12 items-center">
          {/* Left Column - Text */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <h1 className="font-display text-4xl sm:text-5xl md:text-7xl font-bold mb-4 sm:mb-6 leading-tight">
              Build Databases
              <br />
              <span className="gradient-text">With Natural Language</span>
            </h1>

            <p className="text-base sm:text-xl text-muted-foreground mb-6 sm:mb-8 max-w-xl text-balance">
              AI-powered database creation and management. Just describe what you want to track,
              and watch your custom database come to life instantly.
            </p>

            <div className="flex flex-wrap gap-3 sm:gap-4">
              <Link href={isAuth ? "/dashboard" : "/signup"}>
                <button className="relative group overflow-hidden px-6 h-12 rounded-full flex space-x-2 items-center bg-gradient-to-r from-pink-500 to-purple-500 hover:to-purple-600">
                  <span className="relative text-sm text-white font-display">Get Started</span>
                  <div className="flex items-center -space-x-3 translate-x-3">
                    <div className="w-2.5 h-[1.6px] rounded bg-white origin-left scale-x-0 transition duration-300 group-hover:scale-x-100"></div>
                    <svg strokeWidth="2" stroke="currentColor" viewBox="0 0 24 24" fill="none" className="h-5 w-5 stroke-white -translate-x-2 transition duration-300 group-hover:translate-x-0" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 5l7 7-7 7" strokeLinejoin="round" strokeLinecap="round"></path>
                    </svg>
                  </div>
                </button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline" className="font-display">
                  Sign In
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* Right Column - Hero Image */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="relative hidden lg:block"
          >
            <div className="relative w-full aspect-square">
              <Image
                src="/hero-image.png"
                alt="AI Database Management Illustration"
                fill
                className="object-contain drop-shadow-2xl"
                priority
              />
            </div>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-12 sm:py-24 px-4 sm:px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-8 sm:mb-16"
          >
            <h2 className="font-display text-2xl sm:text-4xl md:text-5xl font-bold mb-3 sm:mb-4">
              Intelligent Database Management
            </h2>
            <p className="text-base sm:text-xl text-muted-foreground max-w-2xl mx-auto">
              Powered by AI to make database creation and management effortless
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="glass-card card-3d h-full bg-white/80 dark:bg-gray-900/90">
                  <CardHeader className="p-4 sm:p-6">
                    <div className="w-10 sm:w-14 h-10 sm:h-14 rounded-xl sm:rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-3 sm:mb-4 shadow-glow">
                      <feature.icon className="w-5 sm:w-7 h-5 sm:h-7 text-white" />
                    </div>
                    <CardTitle className="mb-1 sm:mb-2 text-lg sm:text-xl text-gray-900 dark:text-gray-100">{feature.title}</CardTitle>
                    <CardDescription className="text-sm sm:text-base">
                      {feature.description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-12 sm:py-24 px-4 sm:px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto"
        >
          <Card className="glass-card text-center p-6 sm:p-12 ambient-light bg-white/80 dark:bg-gray-900/90">
            <h2 className="font-display text-2xl sm:text-4xl md:text-5xl font-bold mb-4 sm:mb-6 text-gray-900 dark:text-gray-100">
              Ready to get started?
            </h2>
            <p className="text-base sm:text-xl text-muted-foreground mb-6 sm:mb-8">
              Create your first database in seconds with natural language
            </p>
            <div className="flex justify-center">
              <Link href={isAuth ? "/dashboard" : "/signup"}>
                <button className="relative group overflow-hidden px-6 h-12 rounded-full flex space-x-2 items-center bg-gradient-to-r from-pink-500 to-purple-500 hover:to-purple-600">
                  <span className="relative text-sm text-white font-display">Start Building Now</span>
                  <div className="flex items-center -space-x-3 translate-x-3">
                    <div className="w-2.5 h-[1.6px] rounded bg-white origin-left scale-x-0 transition duration-300 group-hover:scale-x-100"></div>
                    <svg strokeWidth="2" stroke="currentColor" viewBox="0 0 24 24" fill="none" className="h-5 w-5 stroke-white -translate-x-2 transition duration-300 group-hover:translate-x-0" xmlns="http://www.w3.org/2000/svg">
                      <path d="M9 5l7 7-7 7" strokeLinejoin="round" strokeLinecap="round"></path>
                    </svg>
                  </div>
                </button>
              </Link>
            </div>
          </Card>
        </motion.div>
      </section>
    </div>
  );
}

const features = [
  {
    icon: Sparkles,
    title: "Natural Language Creation",
    description: "Describe your database in plain English. AI generates the perfect schema instantly.",
  },
  {
    icon: Database,
    title: "Per-User Isolation",
    description: "Your data is completely private and isolated. Each user gets their own secure databases.",
  },
  {
    icon: Zap,
    title: "Dynamic Forms",
    description: "Automatically generated forms based on your schema. No coding required.",
  },
  {
    icon: Shield,
    title: "Smart Suggestions",
    description: "AI-powered auto-categorization, expiration dates, and intelligent defaults.",
  },
  {
    icon: Database,
    title: "Data Export",
    description: "Export your data to CSV, JSON, or PDF formats. Share and backup your databases easily.",
  },
  {
    icon: Sparkles,
    title: "Natural Language Queries",
    description: "Query your data with simple commands. AI converts them to SQL automatically.",
  },
];
