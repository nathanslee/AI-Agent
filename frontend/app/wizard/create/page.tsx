"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { databaseAPI } from "@/lib/api";
import { Sparkles, Check, ArrowLeft } from "lucide-react";

export default function CreateDatabaseWizard() {
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [description, setDescription] = useState("");
  const [generatedSchema, setGeneratedSchema] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerateSchema = async () => {
    if (!description.trim()) {
      setError("Please describe what you want to track");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await databaseAPI.create(description);
      setGeneratedSchema(response.data.schema);
      setStep(2);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to generate schema");
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = () => {
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen px-6 pt-32 pb-16">
      {/* Background Effect */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-1/4 left-1/3 w-96 h-96 bg-purple-300 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-float" />
      </div>

      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <Button
            variant="ghost"
            onClick={() => router.push("/dashboard")}
            className="mb-6"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Dashboard
          </Button>

          <h1 className="font-display text-5xl font-bold mb-4">
            Create New Database
          </h1>
          <p className="text-xl text-muted-foreground">
            Describe what you want to track in natural language
          </p>
        </motion.div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-4 mb-12">
          {[1, 2].map((s) => (
            <div key={s} className="flex items-center">
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${
                  s === step
                    ? "bg-gradient-to-br from-purple-500 to-pink-500 text-white shadow-glow"
                    : s < step
                    ? "bg-green-500 text-white"
                    : "bg-gray-200 text-gray-400"
                }`}
              >
                {s < step ? <Check className="w-5 h-5" /> : s}
              </div>
              {s < 2 && (
                <div className={`w-16 h-1 ${s < step ? "bg-green-500" : "bg-gray-200"}`} />
              )}
            </div>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {/* Step 1: Describe Database */}
          {step === 1 && (
            <motion.div
              key="step1"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
            >
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="text-3xl">
                    What do you want to track?
                  </CardTitle>
                  <CardDescription className="text-base">
                    Describe your database in plain English. Our AI will create the perfect schema.
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-6">
                  <div className="space-y-2">
                    <Label htmlFor="description" className="text-lg">
                      Description
                    </Label>
                    <textarea
                      id="description"
                      className="flex min-h-[200px] w-full rounded-2xl border border-input bg-white/50 backdrop-blur-sm px-4 py-3 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none"
                      placeholder="Example: I want to track grocery items with the item name, date bought, store, food type, and expiration date."
                      value={description}
                      onChange={(e) => setDescription(e.target.value)}
                      disabled={loading}
                    />
                  </div>

                  {/* Example Prompts */}
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-muted-foreground">
                      Need inspiration? Try these:
                    </p>
                    <div className="grid gap-2">
                      {examplePrompts.map((prompt, index) => (
                        <button
                          key={index}
                          onClick={() => setDescription(prompt)}
                          className="text-left p-3 rounded-2xl bg-white/50 hover:bg-white border border-gray-200 text-sm transition-all hover:shadow-soft"
                          disabled={loading}
                        >
                          {prompt}
                        </button>
                      ))}
                    </div>
                  </div>

                  {error && (
                    <div className="p-3 rounded-2xl bg-red-50 border border-red-200 text-red-600 text-sm">
                      {error}
                    </div>
                  )}

                  <Button
                    size="lg"
                    onClick={handleGenerateSchema}
                    disabled={loading}
                    className="w-full group"
                  >
                    {loading ? (
                      "Generating schema..."
                    ) : (
                      <>
                        Generate Database
                        <Sparkles className="ml-2 w-4 h-4 group-hover:rotate-12 transition-transform" />
                      </>
                    )}
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Step 2: Review Schema */}
          {step === 2 && generatedSchema && (
            <motion.div
              key="step2"
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
            >
              <Card className="glass-card">
                <CardHeader>
                  <CardTitle className="text-3xl">
                    Review Your Database
                  </CardTitle>
                  <CardDescription className="text-base">
                    Your AI-generated database schema is ready!
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-6">
                  <div className="p-6 rounded-2xl bg-gradient-purple border border-purple-200">
                    <h3 className="font-display text-2xl font-semibold mb-1">
                      {generatedSchema.display_name}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      Table: {generatedSchema.database_name}
                    </p>
                  </div>

                  <div className="space-y-3">
                    <h4 className="font-semibold text-lg">Fields</h4>
                    <div className="grid gap-3">
                      {generatedSchema.fields?.map((field: any, index: number) => (
                        <div
                          key={index}
                          className="p-4 rounded-2xl bg-white border border-gray-200 flex items-center justify-between"
                        >
                          <div>
                            <p className="font-medium">{field.name}</p>
                            <p className="text-sm text-muted-foreground">
                              Type: {field.type}
                              {field.optional && " • Optional"}
                            </p>
                          </div>
                          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                            <Check className="w-5 h-5 text-white" />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="flex gap-4">
                    <Button
                      variant="outline"
                      onClick={() => setStep(1)}
                      className="flex-1"
                    >
                      Start Over
                    </Button>
                    <Button
                      size="lg"
                      onClick={handleConfirm}
                      className="flex-1 group"
                    >
                      Create Database
                      <Check className="ml-2 w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

const examplePrompts = [
  "I want to track grocery items with name, date bought, store, food type, and expiration date.",
  "Create a workout log with exercise name, sets, reps, weight, and date.",
  "Track my expenses with description, amount, category, date, and payment method.",
  "Manage my book collection with title, author, genre, pages, and reading status.",
];
