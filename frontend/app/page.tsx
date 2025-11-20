"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Database, Sparkles, Zap, Shield } from "lucide-react";

export default function HomePage() {
  return (
    <div className="relative">
      {/* Hero Section */}
      <section className="min-h-screen flex items-center justify-center relative overflow-hidden pt-20">
        {/* Ambient Background */}
        <div className="absolute inset-0 -z-10">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" />
          <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-pink-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" style={{ animationDelay: "2s" }} />
          <div className="absolute bottom-1/4 left-1/3 w-96 h-96 bg-blue-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" style={{ animationDelay: "4s" }} />
        </div>

        <div className="max-w-7xl mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column - Text */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="font-display text-6xl md:text-7xl font-bold mb-6 leading-tight">
              Build Databases
              <br />
              <span className="gradient-text">With Natural Language</span>
            </h1>

            <p className="text-xl text-muted-foreground mb-8 max-w-xl text-balance">
              AI-powered database creation and management. Just describe what you want to track,
              and watch your custom database come to life instantly.
            </p>

            <div className="flex gap-4">
              <Link href="/signup">
                <Button size="lg" className="group">
                  Get Started
                  <Sparkles className="ml-2 w-4 h-4 group-hover:rotate-12 transition-transform" />
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline">
                  Sign In
                </Button>
              </Link>
            </div>
          </motion.div>

          {/* Right Column - Hero Image */}
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="relative"
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
      <section className="py-24 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="font-display text-4xl md:text-5xl font-bold mb-4">
              Intelligent Database Management
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Powered by AI to make database creation and management effortless
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="glass-card card-3d h-full">
                  <CardHeader>
                    <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center mb-4 shadow-glow">
                      <feature.icon className="w-7 h-7 text-white" />
                    </div>
                    <CardTitle className="mb-2">{feature.title}</CardTitle>
                    <CardDescription className="text-base">
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
      <section className="py-24 px-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-4xl mx-auto"
        >
          <Card className="glass-card text-center p-12 ambient-light">
            <h2 className="font-display text-4xl md:text-5xl font-bold mb-6">
              Ready to get started?
            </h2>
            <p className="text-xl text-muted-foreground mb-8">
              Create your first database in seconds with natural language
            </p>
            <Link href="/signup">
              <Button size="lg" className="group">
                Start Building Now
                <Zap className="ml-2 w-4 h-4 group-hover:scale-110 transition-transform" />
              </Button>
            </Link>
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
    title: "Banking Integration",
    description: "Connect your bank with Plaid and automatically sync transactions to your databases.",
  },
  {
    icon: Sparkles,
    title: "Natural Language Queries",
    description: "Query your data with simple commands. AI converts them to SQL automatically.",
  },
];
